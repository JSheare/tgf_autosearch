"""A module containing helper functions used by various parts of the application."""
import datetime
import json
from typing import Any


def read_json_file(file: str) -> Any:
    """Reads the given json-encoded file and returns the contents as the appropriate data structure."""
    try:
        with open(file, 'r') as f:
            result = json.load(f)

        return result
    except json.decoder.JSONDecodeError:
        raise SyntaxError('invalid JSON syntax.')


def write_json_file(data: Any, file: str, pretty: bool = False) -> None:
    """Writes the given data to a json-encoded file with the given name."""
    with open(file, 'w') as f:
        if pretty:
            json.dump(data, f, indent=4)
        else:
            json.dump(data, f)


def yymmdd_to_date(date_str: str) -> datetime.date:
    """Returns the given date string in YYMMDD format as a datetime.date object."""
    return datetime.datetime.strptime(date_str, '%y%m%d').astimezone(datetime.UTC).date()


def date_to_yymmdd(date: datetime.date) -> str:
    """Returns the given datetime.date object as a string in the YYMMDD format."""
    return date.strftime('%y%m%d')
