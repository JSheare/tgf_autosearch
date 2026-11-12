# tgf_autosearch
## An application for automatically running searches of new UCSC TGF Group data.
### To install the application, run the following pip command:

    pip install tgfserver@git+https://github.com/JSheare/tgf_autosearch

After installation, it's also recommended that the following commands be executed before using the application:
- This command will make the user config file and help in filling it out:

        tgf-autosearch --setup

- And this command will validate the config file and report any issues. Run it after filling the file out:

        tgf-autosearch --test-config

To run the application, either run the following command or set it up as a cron job:

    tgf-autosearch

## Config File Options and Format:
The application's config file, auto_search_config.yaml, is how you configure the application's behavior (including what 
searches to run). It's comprised of two sections:

### Application Options:
This section contains general application options, including:
- log_level: the application's log level.
- lag_by_days: the minimum age of dates to run searches on. Only dates this many days old or older will be searched.

### Search Options:
This section is how you describe what searches the application should run. It contains the following options:
- default_export_loc: the default path where search results should be exported. This is an alias that exists mainly for
  the purpose of convenience.
- searches: descriptions of the searches themselves.

The 'searches' parameter is broken down into sections with the following form:
- instrument_name:
  - search_num_1:
    - import_loc: path
    - export_loc: path
    - before_date: yymmdd
    - after_date: yymmdd
    - options: [search_flags]
  - search_num_2:
    - ...

Each section describes searches for a particular instrument, and each entry within a section describes a search.
Searches have the following options:
- import_loc: the location of the daily data directories to be searched.
- export_loc: the location where search results should be exported.
- before_date: the end date for this search (non-inclusive) in YYMMDD format.
- after_date: the start date for this search (inclusive) in YYMMDD format.
- options: a list of flags/options to run the search with (--aircraft, --allscints, etc.)

Here's an example of a fully filled out searches section:
- GODOT:
  - "1":
    - import_loc: /media/david/AllDetectorData/Detectors/GODOT/Data
    - export_loc: ~/auto_search
    - before_date: "261112"
    - after_date: "150101"
    - options: ["--allscints"]

This details a single search for Godot: every day in '/media/david/AllDetectorData/Detectors/GODOT/Data' starting from 
150101 up to 261112 with the 'allscints' option enabled, and with results exported to '~/auto_search'.

To add a new search, simply add a new search entry for the desired instrument with the desired options. Some tips:
- The default_export_loc alias can save you some typing. To use it, enter '*default_search_loc' instead of 
    the actual path.
  - Ex: export_loc: *default_export_loc
- You can use "000000" as a shorthand date for the beginning of time.
  - Ex: after_date: "000000"
- You can use "999999" as a shorthand date for the end of time.
  - Ex: before_date: "999999"
- After adding a new search (or searches) run the following command to ensure that there aren't any mistakes:
  - tgf-autosearch --test-config