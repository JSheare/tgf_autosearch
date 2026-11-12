"""A module containing a class for managing the record of searched days for the application."""
import pathlib
import platformdirs
from typing import Dict, Set

import tgf_autosearch.config.parameters as params
import tgf_autosearch.helpers.helper_funcs as helpers


class DaysRecord:
    """A class that manages the record of searched days for the application.

    Attributes
    ----------
    _record : dict of [str, set of str]
        A dictionary of sets containing the list of days searched for each instrument.

    """
    def __init__(self):
        self._record = self._read()

    @staticmethod
    def _read() -> Dict[str, Set[str]]:
        """A helper function that reads the record of already searched days from a file."""
        days_file = f'{platformdirs.user_data_path(params.APPLICATION_NAME, appauthor=False)}/{params.DAYS_FILE}'
        if pathlib.Path(days_file).is_file():
            contents = helpers.read_json_file(days_file)
            for instrument in contents:
                contents[instrument] = set(contents[instrument])

            return contents

        return dict()

    def write(self) -> None:
        """A helper function that writes the record of already searched days to a file."""
        path = pathlib.Path(platformdirs.user_data_path(params.APPLICATION_NAME, appauthor=False))
        if not path.is_dir():
            path.mkdir(parents=True)

        days_file = f'{path}/{params.DAYS_FILE}'
        contents = dict()
        for instrument in self._record:
            contents[instrument] = list(self._record[instrument])

        helpers.write_json_file(contents, days_file)

    def day_is_present(self, instrument: str, day: str) -> bool:
        """Returns True if the day is present for the given instrument and False otherwise."""
        if instrument in self._record and day in self._record[instrument]:
            return True

        return False

    def add_day(self, instrument: str, day: str) -> None:
        """Adds the given day to the record for the given instrument, if not already present."""
        if instrument not in self._record:
            self._record[instrument] = set()

        self._record[instrument].add(day)

    def remove_day(self, instrument: str, day: str) -> None:
        """Removes the given day from the record for the given instrument, if present."""
        if instrument in self._record and day in self._record[instrument]:
            self._record[instrument].remove(day)
