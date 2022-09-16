'''
This module is used to create the dashboard. Suitable for running locally,
but not for deployment.
'''
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

from config import airports, db_path


# Build the Dashboard object
app = dash.Dash(
    external_stylesheets=[
        dbc.themes.CYBORG,
        {
            'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
            'rel': 'stylesheet',
            'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
            'crossorigin': 'anonymous'
        }
    ],
    url_base_pathname='/weather-app/',
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)




def serve_layout():
    sidebar = dbc.Container([
        dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("Start Date"),
                        html.Br(),
                        dcc.DatePickerSingle(
                            id="date-picker",
                            min_date_allowed=date(2019, 8, 25),
                            max_date_allowed=date.today() + timedelta(days=-1),
                            date=date.today() + timedelta(days=-14),
                    ),
                    ]
                )
            )
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label("Select Location"),
                    html.Br(),
                    dcc.Dropdown(
                        id="airport-dropdown",
                        options=[
                            {
                                "label": (
                                    f"{d['city']}, " +
                                    f"{d['state_abbrev']} " +
                                    f"({d['icao_designation']})"
                                ),
                                "value": d["icao_designation"],
                            }
                            for d in airports
                        ],
                        value="KORD",
                    ),
                ]
            )
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [
                    html.I(className="fab fa-github fa-lg"),
                    " Repository for this page: ",
                    html.Br(),
                    html.A(
                        "https://github.com/pkepley/dash-weather-app",
                        href="https://github.com/pkepley/dash-weather-app",
                    )
                ],
                width=12
            )
        ),
    ])


    content = dbc.Container(
        children=[
            dbc.Row(dbc.Col([dcc.Graph(id="avf-temperature")], width=12)),
            dbc.Row(dbc.Col([dcc.Graph(id="avf-wind")], width=12)),
        ],
    )

    return dbc.Container([
        dbc.Row(
            dbc.Col(
                [html.H2("Weather Forecast vs Actual Comparison")],
                width=12
            )
        ),
        dbc.Row([
            dbc.Col(sidebar, width=3),
            dbc.Col(content, width=9)
        ]),
        # html.Br(),
        # dbc.Row(
        #     footer
        # )
    ])


# Serve the layout
app.layout = serve_layout


def get_actual(conn, airport, date_range_start, date_range_end):
    df = pd.read_sql(
        f"""
        SELECT
        *
        FROM weather_actual
        WHERE airport = '{airport}'
        AND datetime >= '{date_range_start}'
        AND datetime <= '{date_range_end}'
        ORDER BY datetime
        """,
        conn,
    )

    df["datetime"] = pd.to_datetime(df["datetime"])
    return df


def get_forecast(conn, airport, date_range_start, date_range_end):
    df = pd.read_sql(
        f"""
        SELECT
        *
        FROM weather_forecast
        WHERE airport = '{airport}'
        AND datetime >= '{date_range_start}'
        AND datetime <= '{date_range_end}'
        ORDER BY pull_date, datetime
        """,
        conn,
    )
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df


@app.callback(
    Output("avf-temperature", "figure"),
    Output("avf-wind", "figure"),
    Input("date-picker", "date"),
    Input("airport-dropdown", "value"),
)
def update_graphs(date_str_start, airport):
    date_range_start = datetime.strptime(date_str_start, "%Y-%m-%d")
    date_range_end = date_range_start + timedelta(days=13)
    date_str_end = date_range_end.strftime("%Y-%m-%d")

    # Query data from the database!
    conn = sqlite3.connect(db_path)
    df_fcst = get_forecast(conn, airport, date_str_start, date_str_end)
    df_actl = get_actual(conn, airport, date_str_start, date_str_end)
    conn.close()

    # Update the temperature plot!
    fig_temp_avf = px.line(
        df_fcst,
        x="datetime",
        y="temperature_hourly",
        labels={
            "datetime": "Date",
            "temperature_hourly": "Temperature (°F)",
            "pull_date": "Forecast Date",
        },
        title="Temperature Forecast vs Actual",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        color="pull_date",
        height=350
    )

    fig_temp_avf.add_scatter(
        x=df_actl["datetime"],
        y=df_actl["air_temp"],
        mode="lines",
        marker_color="white",
        name="Actual",
    )

    fig_temp_avf.update_traces(hovertemplate="%{y:d}°F")
    fig_temp_avf.update_yaxes(range=[0, 120])
    fig_temp_avf.update_layout(
        autosize=True,
        hovermode="x unified",
        margin=dict(l=75, r=50, t=50, b=50)
    )

    # Update the wind plot!
    fig_wind_avf = px.line(
        df_fcst,
        x="datetime",
        y="wind_speed_sustained",
        labels={
            "datetime": "Date",
            "wind_speed_sustained": "Wind Speed (MPH)",
            "pull_date": "Forecast Date",
        },
        title="Wind Speed Forecast vs Actual",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        color="pull_date",
        height=350
    )
    fig_wind_avf.add_scatter(
        x=df_actl["datetime"],
        y=df_actl["wind_speed"],
        mode="lines",
        marker_color="white",
        name="Actual",
    )

    fig_wind_avf.update_traces(hovertemplate="%{y:d} MPH")
    fig_wind_avf.update_yaxes(range=[0, 40])
    fig_wind_avf.update_layout(
        autosize=True,
        hovermode="x unified",
        margin=dict(l=75, r=50, t=50, b=50)
    )

    return fig_temp_avf, fig_wind_avf


if __name__ == "__main__":
    app.run_server(
        debug=True,
        host="0.0.0.0",
        port="8050"
    )
