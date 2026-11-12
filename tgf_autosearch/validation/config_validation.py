"""A module containing the pydantic model used to validate the application's config file."""
import datetime
import logging
import pathlib
import pydantic
from typing import Any, Annotated, Dict, List


def is_valid_directory_path(value: str) -> str:
    value.replace('\\', '/')
    if value != '' and value[-1] == '/':
        value = value[:-1]

    try:
        path = pathlib.Path(value).expanduser()
    except:
        raise ValueError('input should be a valid absolute directory path.')

    return str(path)


def is_valid_log_level(value: Any) -> int:
    if not isinstance(value, str):
        raise ValueError('input should be a string corresponding to a log level.')

    level_mappings = logging.getLevelNamesMapping()
    value = value.upper()
    if value not in level_mappings:
        raise ValueError('input should be a string corresponding to a log level.')

    return level_mappings[value]


def is_valid_yymmdd(value: Any) -> datetime.date:
    try:
        if not (isinstance(value, str) and len(value) == 6):
            raise ValueError

        if value == '000000':
            return datetime.datetime.fromtimestamp(0, datetime.UTC).date()
        elif value == '999999':
            # Maximum possible value for yymmdd in this century
            return datetime.datetime.fromtimestamp(4102387200, datetime.UTC).date()

        return datetime.datetime.strptime(value, '%y%m%d').replace(tzinfo=datetime.UTC).date()
    except ValueError:
        raise ValueError('input should be a valid date in YYMMDD format.')


class EntryModel(pydantic.BaseModel):
    """A model for validating the config file's search entries."""
    import_loc: Annotated[str, pydantic.AfterValidator(is_valid_directory_path)]
    export_loc: Annotated[str, pydantic.AfterValidator(is_valid_directory_path)]
    before_date: Annotated[datetime.date, pydantic.BeforeValidator(is_valid_yymmdd)]
    after_date: Annotated[datetime.date, pydantic.BeforeValidator(is_valid_yymmdd)]
    options: List[str]

    @pydantic.model_validator(mode='after')
    def check_dates(self):
        if self.after_date >= self.before_date:
            raise ValueError('after_date must be before before_date.')

        return self


class SearcherModel(pydantic.BaseModel):
    """A model for validating the application's config file."""
    log_level: Annotated[int, pydantic.BeforeValidator(is_valid_log_level)]
    lag_by_days: pydantic.PositiveInt
    default_export_loc: Annotated[str, pydantic.AfterValidator(is_valid_directory_path)]
    searches: Dict[str, Dict[str, EntryModel]]
