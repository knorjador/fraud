from flask import Flask
from dash import Dash, dash_table, html, dcc, Output, Input
import sqlite3
import plotly.express as px
import dash
import dash_bootstrap_components as dbc

app = Flask(__name__)


def create_dash_application(flask_app):
    # Connexion à la base de données SQLite à l'intérieur de la fonction
    conn = sqlite3.connect('C:/Users/moon/fraud/app.db')
    cursor = conn.cursor()

    # Exécution d'une requête pour obtenir les données de la table de votre base de données SQLite
    cursor.execute('SELECT * FROM `transaction`')
    rows = cursor.fetchall()

    # Fermeture de la connexion à la base de données SQLite
    conn.close()

    dash_app = Dash(
        server=flask_app, name="Dashboard", url_base_pathname="/dash/"
    )

    dash_app.layout = html.Div([
        html.Div(className='row', children='Historique de vos prédictions',
                 style={'textAlign': 'center', 'color': 'white', 'fontSize': 30}),
        dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": col[0], "id": col[0], "deletable": True, "selectable": True} for col in cursor.description
            ],
            data=[dict(zip([col[0] for col in cursor.description], row)) for row in rows],
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
        )
    ])

    return dash_app

"""table = dbc.Table(
# using the same table as in the above example
bordered=True,
dark=True,
hover=True,
responsive=True,
striped=True,
)"""

create_dash_application(app)

if __name__ == '__main__':
    app.run(debug=True)
