# A Simple Weather Forecast Tracking Web App
A simple web app, whose purposes is to source historical weather forecasts
/ actuals to see how much they deviate over time.

The dashboard is currently hosted at
[https://www.paulkepley.com/weather-app/](https://www.paulkepley.com/weather-app/).

## Setup
- A basic configuration file `config.py` is provided which sets default
  parameters for the data pull, e.g. location of file-store, database, time of
  pull. These should be updated if you want to store data elsewhere.
- A limited list of weather station locations (corresponding to airport weather
  stations) is provided in `airports.csv`. You can extend the list as needed.
- This project has been tested on Linux, and should work fine on a Mac. It may,
  however, require some changes to run natively on Windows. You should, however,
  be able to run on Windows using
  [Anaconda](https://www.anaconda.com/products/individual) or 
  [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

## Installation
- This project's dependencies can be installed using
  [PipEnv](https://pypi.org/project/pipenv/). Assuming that you have PipEnv
  installed, run the following command from the project's root folder:
  ```
  pipenv install Pipfile
  ```
- Alternatively, ensure that the required dependencies indicated in the Pipfile
  are installed before proceeding.


## Pulling Data
- If you are using PipEnv to run the project, then prepend `pipenv run` before
  any commands, or if you are running the scrips interactively, you can activate
  the environment by first running `pipenv shell`. In scripting the project, you
  need to do the former.
- If you have not updated `data_root` to reflect an absolute path in
  `config.py`, then you will need to change to the `src` directory in order to
  run the scripts below (since `data_root` is defined relative to the `src`
  directory).
- To pull data, run the script `pull_weather.py`. This will pull down the
  weather forecast and actual data for all locations for which the current time
  is equal `pull_hour` in the local time-zone.
- To update the database, run the script `update_db.py`. This will scan the
  sub-folders of the data directory (`data_root`) for CSV files corresponding to
  actuals / forecasts not contained in the database (saved at `db_path`), and
  will update the database with any new data.
