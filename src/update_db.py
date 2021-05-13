'''
This module is used to pull weather forecast and actual from NWS.
'''
import sqlite3
import glob
import pandas as pd


def actual_table_exists(cur):
    """
    Determine if the table of actual weather data exists.

    Inputs
        cur: sqlite3 database cursor
    Output
        rslt_check: boolean
    """

    rslt_check = cur.execute(
        """
        SELECT
        name
        FROM sqlite_master
        WHERE type='table'
        AND name='weather_actual';
        """
    ).fetchone()

    return rslt_check is not None


def actual_loaded(cur, airport_name, pull_date_str):
    """
    Return whether any actual performance is loaded
    for a given airport on a given date.

    Inputs
        cur: sqlite3 database cursor
        airport_name: string for airport name
        pull_date_str: YYY-MM-DD formatted date string
    Output
        rslt_check: boolean
    """

    if not actual_table_exists(cur):
        return False

    else:
        rslt_check = cur.execute(
            f"""
            SELECT
            *
            FROM weather_actual
            WHERE airport = '{airport_name}'
            AND SUBSTR(datetime, 0, 11) = '{pull_date_str}'
            """
        ).fetchone()

        return rslt_check is not None


def actual_date_range_loaded(cur, airport_name):
    """
    Return the dates of actual weather performance loaded
    in the database for a given airport.

    Inputs
        cur: sqlite3 database cursor
        airport_name: string for airport name
    Output
        date_range: list of strings corresponding to YYYY-MM-DD
                    formatted dates which were found loaded
                    in the database for airport_name
    """
    if not actual_table_exists(cur):
        return []

    else:
        date_range = cur.execute(
            f"""
            SELECT
            SUBSTR(datetime, 0, 11) as actl_date
            FROM weather_actual
            WHERE airport = '{airport_name}'
            GROUP BY actl_date
            """
        ).fetchall()

        date_range = [d[0] for d in date_range]

        return date_range


def forecast_table_exists(cur):
    """
    Determine if the table of weather forecast data exists.

    Inputs
        cur: sqlite3 database cursor
    Output
        rslt_check: boolean
    """
    rslt_check = cur.execute(
        """
        SELECT
        name
        FROM sqlite_master
        WHERE type='table'
        AND name='weather_forecast';
        """
    ).fetchone()

    return rslt_check is not None


def forecast_loaded(cur, airport_name, pull_date_str):
    """
    Return whether any forecast data is loaded
    for a given airport for a given pull date.

    Inputs
        cur: sqlite3 database cursor
        airport_name: string for airport name
        pull_date_str: YYY-MM-DD formatted date string
    Output
        rslt_check: boolean
    """
    if not forecast_table_exists(cur):
        return False

    else:
        rslt_check = cur.execute(
            f"""
            SELECT
            *
            FROM weather_forecast
            WHERE airport = '{airport_name}'
            AND pull_date = '{pull_date_str}'
            """
        ).fetchone()

        return rslt_check is not None


def forecast_pull_date_range_loaded(cur, airport_name):
    """
    Return the pull dates of weather forecasts loaded
    in the database for a given airport.

    Inputs
        cur: sqlite3 database cursor
        airport_name: string for airport name
    Output
        date_range: list of strings corresponding to YYYY-MM-DD
                    formatted forecast pull dates that were found
                    loaded in the database for airport_name
    """
    if not forecast_table_exists(cur):
        return []

    else:
        date_range = cur.execute(
            f"""
            SELECT
            pull_date
            FROM weather_forecast
            WHERE airport = '{airport_name}'
            GROUP BY pull_date
            """
        ).fetchall()

        date_range = [d[0] for d in date_range]

        return date_range


def update_all_actual(cur, airports, data_root):
    """
    Update table of actual performance for any actual dates
    that are available in the reference folder but not in the
    database.

    Inputs
        cur: sqlite3 database cursor
        airports: list of strings corresponding to aiport names / folders
        data_root: root directory for the airport data folders
    """
    for airport_name in sorted(airports):
        airport_path = f"{data_root}/{airport_name}"
        actual_file_paths = glob.glob(f"{airport_path}/nws_actl_*.csv*")
        actual_file_paths.sort()

        actual_table_previously_created = actual_table_exists(cur)
        existing_actual_dates = actual_date_range_loaded(cur, airport_name)

        for file_path_actual in actual_file_paths:
            actual_date_str = file_path_actual.split("_")[-1].split(".")[0]

            if actual_date_str not in existing_actual_dates:
                # get data to load
                df = pd.read_csv(file_path_actual)
                df["airport"] = airport_name

                # load data if there is data to load
                # (sometimes the file has no rows)
                if df.size > 0:
                    print(f"Loading actual for {airport_name} " +
                          f"on {actual_date_str}.")
                    df.to_sql("weather_actual", con=conn, if_exists="append")
                    conn.commit()

            # create an index if table has just been created for first time
            if not actual_table_previously_created and actual_table_exists(cur):
                print("ADDING INDEX")
                cur.execute(
                    """
                    CREATE INDEX ix_actl_datetime
                    ON weather_actual (datetime);
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX ix_actl_airport
                    ON weather_actual (airport);
                    """
                )
                actual_table_previously_created = True


def update_all_forecast(cur, airports, data_root):
    """
    Update table of weather forecasts for any pull dates
    that are available in the reference folder but not in the
    database.

    Inputs
        cur: sqlite3 database cursor
        airports: list of strings corresponding to aiport names / folders
        data_root: root directory for the airport data folders
    """
    for airport_name in sorted(airports):
        airport_path = f"{data_root}/{airport_name}"
        forecast_file_paths = glob.glob(f"{airport_path}/nws_fcst_*.csv*")
        forecast_file_paths.sort()

        fcst_table_previously_created = forecast_table_exists(cur)
        existing_forecast_pull_dates = (
                forecast_pull_date_range_loaded(cur, airport_name)
        )

        for file_path_forecast in forecast_file_paths:
            forecast_date_str = file_path_forecast.split("_")[-1].split(".")[0]

            if forecast_date_str not in existing_forecast_pull_dates:
                # get data to load
                df = pd.read_csv(file_path_forecast)
                df["airport"] = airport_name
                df.rename(
                    columns={"forecast_time_stamps": "datetime"},
                    inplace=True
                )

                # load data if there is data to load
                # (sometimes the file has no rows)
                if df.size > 0:
                    print(
                        f"Loading forecast for {airport_name}" +
                        f" on {forecast_date_str}."
                    )
                    df.to_sql("weather_forecast", con=conn, if_exists="append")
                    conn.commit()

            # create an index if table has just been created for first time
            if not fcst_table_previously_created and forecast_table_exists(cur):
                print("ADDING INDEX")
                cur.execute(
                    """
                    CREATE INDEX ix_fcst_pull_date
                    ON weather_forecast (pull_date);
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX ix_fcst_datetime
                    ON weather_forecast (datetime);
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX ix_fcst_airport
                    ON weather_forecast (airport);
                    """
                )
                fcst_table_previously_created = True


if __name__ == '__main__':
    from config import root_path as data_root
    from config import df_airports

    print(f"Running from {data_root}")

    # sqlite stuff
    conn = sqlite3.connect(f"{data_root}/weather.db")
    cur = conn.cursor()

    # get airports
    airport_list = df_airports["icao_designation"].to_list()

    update_all_actual(cur, airport_list, data_root)
    update_all_forecast(cur, airport_list, data_root)

    conn.close()
