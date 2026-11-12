"""A module containing the program that automatically runs searches on unexamined data."""
import argparse
import platformdirs
import psutil
import pydantic
import yaml

import tgf_autosearch.config.parameters as params
from tgf_autosearch.searcher import Searcher
from tgf_autosearch.startup.config_funcs import read_config
from tgf_autosearch.validation.config_validation import SearcherModel


def running_pid() -> int:
    """A function that returns the pid of the application, or -1 if it isn't currently running."""
    try:
        with (open(f'{platformdirs.user_runtime_path(params.APPLICATION_NAME, appauthor=False)}/{params.PID_FILE}', 'r')
              as file):
            # Checking to see if the pid in the file is still active
            pid = int(file.readline())
            if psutil.pid_exists(pid):
                return pid

        return -1
    except (OSError, FileNotFoundError, ValueError):
        return -1


def main() -> None:
    """A function that serves as the top level call for the tgf-autosearch application."""
    parser = argparse.ArgumentParser(prog='tgf-autosearch', description="A program that automatically searches new "
                                                                        "UCSC TGF Group data")
    parser.add_argument('--setup', help='run the set up process for the application', action='store_true')
    parser.add_argument('--test-config', help='test that the config file contains valid options', action='store_true')
    args = parser.parse_args()

    # Handling any arguments
    if args.setup:
        read_config()
        print(f'Made/updated config file at {platformdirs.user_config_path(params.APPLICATION_NAME, appauthor=False)}.')
        return
    if args.test_config:
        try:
            SearcherModel(**read_config())
            print('All config file options successfully validated.')
        except yaml.YAMLError as ex:
            if hasattr(ex, 'problem') and hasattr(ex, 'problem_mark'):
                mark = ex.problem_mark
                print(f'Encountered error when parsing config file: line {mark.line + 1} column {mark.column + 1}; '
                      f'{ex.problem}.')
            else:
                print(f'Encountered error when parsing config file: {ex}')

        except pydantic.ValidationError as ex:
            print(f'Encountered error(s) when validating config file:')
            for error in ex.errors():
                loc = '.'.join([s for s in error['loc'] if isinstance(s, str)])
                if error['type'] == 'missing':
                    print(f"Missing required field: {loc}.")
                else:
                    print(f"Invalid input '{error['input']}' at {loc}. {error['msg']}")

        return

    if running_pid() == -1:
        # Running the application
        try:
            searcher = Searcher()
        except (pydantic.ValidationError, yaml.YAMLError):
            print(f'Encountered error(s) when parsing and/or validating config file. Use --test_config flag for '
                  f'details.')
            return
        except Exception as ex:
            print('Fatal exception encountered during startup.')
            print(f'{type(ex).__name__}: {ex}')
            return

        searcher.main()


if __name__ == '__main__':
    main()
