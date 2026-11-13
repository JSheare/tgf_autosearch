"""A module containing a class that implements the application's main functionality."""
import datetime
import logging
import pathlib
from importlib.metadata import version, PackageNotFoundError
from tgfsearch.search import parse_search_args, program
from typing import List

import tgf_autosearch.config.parameters as params
import tgf_autosearch.helpers.helper_funcs as helpers
from tgf_autosearch.helpers.days_record import DaysRecord
from tgf_autosearch.startup.config_funcs import read_config
from tgf_autosearch.startup.configure_logging import configure_logging
from tgf_autosearch.validation.config_validation import SearcherModel


class Searcher:
    """A class that implements the main functionality of the application.

    Attributes
    ----------
    _config : SearcherModel
        A pydantic model containing the application's config options.
    _logger : logging.Logger
        The application's logger.
    _days_record : DaysRecord
        A DaysRecord instance that maintains a record of the days searched.

    """

    def __init__(self):
        self._config = SearcherModel(**read_config())
        self._logger = logging.getLogger(params.APPLICATION_NAME)
        self._days_record = DaysRecord()

    def _get_day_list(self, instrument: str, import_loc: str, before_date : datetime.date,
                       after_date: datetime.date) -> List[str]:
        """Assembles a list of days to search for the given instrument with the given import loc on the given date
        range."""
        try:
            self._logger.info(f'Assembling day list for {instrument} [{helpers.date_to_yymmdd(after_date)}, '
                              f'{helpers.date_to_yymmdd(before_date)}).')
            latest_date = datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(days=self._config.lag_by_days)
            new_days = []
            day_dirs = [d for d in pathlib.Path(import_loc).rglob(r'[0-9][0-9][0-9][0-9][0-9][0-9]')]
            day_dirs.sort()
            for day_dir in day_dirs:
                day_str = str(day_dir)[-6:]
                date = helpers.yymmdd_to_date(day_str)

                self._logger.debug(f'Checking {day_str} ({day_dir}).')

                # Skipping the day if it isn't in the date range
                if not after_date <= date < before_date:
                    self._logger.debug(f'Rejecting {day_str} (not in date range).')
                    continue

                # Skipping the day if it's after the latest configured date
                if not date <= latest_date:
                    self._logger.debug(f'Rejecting {day_str} (after configured latest date).')
                    continue

                # Skipping the day if it's already been searched
                if self._days_record.day_is_present(instrument, day_str):
                    self._logger.debug(f'Rejecting {day_str} (already searched).')
                    continue

                # Skipping the day if the directory is empty
                if not any(day_dir.iterdir()):
                    self._logger.debug(f'Rejecting {day_str} (empty directory).')
                    continue

                # Skipping the day if a transfer marker file is present (incomplete data file transfer)
                if pathlib.Path(f'{day_dir}/{params.TRANSFER_FILE}').is_file():
                    self._logger.debug(f'Rejecting {day_str} (transfer marker present).')
                    continue

                self._logger.debug(f'Adding {day_str} to date list.')

                new_days.append(day_str)

            return new_days
        except Exception:
            self._logger.exception(f'Encountered an exception while assembling the day list for {instrument} '
                                   f'[{helpers.date_to_yymmdd(after_date)}, {helpers.date_to_yymmdd(before_date)}):')
            return []

    def _search_day(self, day: str, instrument: str, import_loc: str, export_loc: str, options:List[str]) -> None:
        """Searches the given instrument on the given day with the given options."""
        # Assembling the argument list
        args = [day, day, instrument]
        if import_loc != '':
            args.append('--import-loc')
            args.append(import_loc)

        if export_loc != '':
            args.append('--export-loc')
            args.append(export_loc)

        if len(options) > 0:
            args += options

        # Running the search
        self._logger.info(f'Running search on {instrument} {day}{' ' + str(options) if len(options) > 0 else ''}.')
        try:
            first_date, second_date, instrument_name, import_loc, export_loc, modes = parse_search_args(args)
            program(first_date, second_date, instrument_name, import_loc, export_loc, modes)
        except Exception:
            self._logger.exception(f'Encountered an exception when running search on {instrument} {day}'
                                   f'{' ' + str(options) if len(options) > 0 else ''}:')
            return

        # Recording that the day has been searched
        self._logger.debug(f'Adding {instrument} {day} to record.')
        self._days_record.add_day(instrument, day)
        self._days_record.write()

        self._logger.info(f'Search on {instrument} {day} concluded.')

    def main(self):
        """A function that implements the application's main functionality."""
        configure_logging(self._config.log_level)

        app_version = None
        try:
            app_version = version(params.APPLICATION_NAME)
        except PackageNotFoundError:
            pass

        if app_version is not None:
            self._logger.info(f'({params.APPLICATION_NAME} v{app_version}) Starting new run.')
        else:
            self._logger.info('Starting new run.')

        # Main autosearch logic. Loop through each instrument's searches and execute them one by one
        try:
            for instrument in self._config.searches:
                for search in self._config.searches[instrument]:
                    config = self._config.searches[instrument][search]
                    day_list = self._get_day_list(instrument, config.import_loc, config.before_date,
                                                  config.after_date)
                    for day in day_list:
                        self._search_day(day, instrument, config.import_loc, config.export_loc, config.options)

        except Exception:
            self._logger.debug('Encountered a critical exception:')

        self._logger.info('Run concluded.')
