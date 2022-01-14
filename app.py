import pandas as pd
import geopandas as gpd

import dash
from dash import dcc
from dash import html
from dash import no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

#pictogramm laden?
#image_filename = 'impf_pic.png' # replace with your own image
#encoded_image = pybase64.b64encode(open(image_filename, 'rb').read())

#impf-Fortschritt nach Bundesland
df = pd.read_csv('https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv' ,header=0, sep='\t'),

#deutschland-karte
geo_df  = 'data/vg2500_geo84/vg2500_bld.shp' 
map_df = gpd.read_file(geo_df) 
geojson = map_df.__geo_interface__ 

#ids der Bundesländer in geo_df
id_bundesland = {
    '0': 'Hamburg',
    '1': 'Niedersachsen',
    '2': 'Bremen',
    '3': 'Nordrhein-Westfalen',
    '4': 'Hessen',
    '5': 'Rheinland-Pfalz',
    '6': 'Baden-Württemberg',
    '7': 'Bayern',
    '8': 'Saarland',
    '9': 'Berlin',
    '10': 'Brandenburg',
    '11': 'Mecklenburg-Vorpommern',
    '12': 'Sachsen',
    '13': 'Sachsen-Anhalt',
    '14': 'Thüringen',
    '15': 'Schleswig-Holstein'
    }

#rki daten
df_bundes = df[0].copy()
df_bundes.drop([2],inplace=True) #row DE-BUND dropen
df_bundes['id'] = ['10','9','6','7','2','4','0','11','1','3','5','15','8','12','13','14']

#map
fig = px.choropleth(
        df_bundes, geojson=geojson,
        locations="id", 
        color = 'vaccinationsTotal',
        projection="mercator", 
        color_continuous_scale="Viridis",
        range_color=[0, df_bundes['vaccinationsTotal'].max()],
        labels={'vaccinationsTotal':'Gesamtanzahl an Impfungen'},
    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(hoverinfo="none",hovertemplate=None)

app.layout = html.Div(children=[
    html.H1(children='Impfquoten Monitoring',
            style={'textAlign': 'center'}),
    html.H2(children='in Deutschland',
            style={'textAlign': 'center'}),
    #html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
    html.Div(style={'width': '28%', 'float': 'left', 'display': 'inline-block'},
    children=[
        dcc.Dropdown(
            id='dropdown_bundeslander',
            options=[{'label': bundesland, 'value': id} for id, bundesland in id_bundesland.items()],
            placeholder="Verschiedene Bundesländer",
        ),
    ]), 
    html.Div(
        style={'width': '100%','height': '1000px','display':'inline-block','overflow': 'hidden'},  
        children=[
            dcc.Graph(id="germany",figure=fig, clear_on_unhover=True, style={'width': '100%', 'height': '80vh'}),
            dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
    html.P('© Bundesamt für Kartographie und Geodäsie, Frankfurt am Main, 2011')
])  

#hover information
@app.callback(
    Output("tooltip_inf", "show"),
    Output("tooltip_inf", "bbox"),
    Output("tooltip_inf", "children"),
    Input("germany", "hoverData"),
)
def display_hover(hoverData):
    if hoverData is None:
        return False, no_update, no_update

    pt = hoverData["points"][0]
    id = pt['location']
    bbox = pt["bbox"]
    num = pt["pointNumber"]

    name = id_bundesland[id]

    df_row = df_bundes.iloc[num]
    total_count = df_row['vaccinationsTotal']

    children = [
        html.Div([
            html.H5(f"{name}",style={'textAlign': 'center'}),
            html.P(f"Gesamtanzahl an Impfungen: {total_count}"),
        ], style={'width': '300px', 'white-space': 'normal'})
    ]

    return True, bbox, children

#update fig nach dropdown
@app.callback(
    Output("germany", "figure"), 
    [Input("dropdown_bundeslander", "value")])
def display_choropleth(value):

    geojson_bund = geojson['features'][int(value)]
    df_bundes_bund = df_bundes[df_bundes['id']==value]

    fig = px.choropleth(
        df_bundes_bund, geojson=geojson_bund ,
        locations="id", 
        color = 'vaccinationsTotal',
        projection="mercator", 
        color_continuous_scale="Viridis",
        range_color=[0, df_bundes['vaccinationsTotal'].max()],
        labels={'vaccinationsTotal':'Gesamtanzahl an Impfungen'})

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(hoverinfo="none",hovertemplate=None)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
