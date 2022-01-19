import pandas as pd
import geopandas as gpd
import locale
import math
import requests
import io

import dash
from dash import dcc
from dash import html
from dash import no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

locale.setlocale(locale.LC_ALL, '')

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

#pictogramm laden?
#image_filename = 'impf_pic.png' # replace with your own image
#encoded_image = pybase64.b64encode(open(image_filename, 'rb').read())

#impf-Fortschritt nach Bundesland
df = pd.read_csv('https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv' ,header=0, sep='\t'),
#impf-fortschritt über zeit
df2 = pd.read_csv('https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv' ,header=0, sep='\t')
df2_time = df2[["date","dosen_erst_kumulativ", "dosen_zweit_kumulativ", "dosen_dritt_kumulativ"]]
#impfquote nach altersruppen pro bundesland
url=    'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Impfquotenmonitoring.xlsx?__blob=publicationFile'
download = requests.get(url)

with io.BytesIO(download.content) as a:
    df3_agegroups = pd.io.excel.read_excel(a, "Impfquote_bundesweit_Alter", header=[0,1,2])

df_mindestens1x = df3_agegroups[[('Bundesland','Unnamed: 1_level_1','Unnamed: 1_level_2'),('Impfquote mindestens einmal geimpft','5-17 Jahre', '5-11 Jahre'),('Impfquote mindestens einmal geimpft','5-17 Jahre', '12-17 Jahre'), ('Impfquote mindestens einmal geimpft','18+ Jahre', '18-59 Jahre**'), ('Impfquote mindestens einmal geimpft','18+ Jahre', '60+ Jahre**')]]
df_mindestens1x.columns = ['Bundesland', '5-11 Jahre', '12-17 Jahre', '18-59 Jahre', '60+ Jahre']

df_grundimmunisiert = df3_agegroups[[('Bundesland','Unnamed: 1_level_1','Unnamed: 1_level_2'),('Impfquote grundimmunisiert','5-17 Jahre', '5-11 Jahre'),('Impfquote grundimmunisiert','5-17 Jahre', '12-17 Jahre'), ('Impfquote grundimmunisiert','18+ Jahre', '18-59 Jahre'), ('Impfquote grundimmunisiert','18+ Jahre', '60+ Jahre')]]
df_grundimmunisiert.columns = ['Bundesland', '5-11 Jahre', '12-17 Jahre', '18-59 Jahre', '60+ Jahre']

df_booster = df3_agegroups[[('Bundesland','Unnamed: 1_level_1','Unnamed: 1_level_2'),('Impfquote Auffrischimpfung','12-17 Jahre', 'Unnamed: 21_level_2'), ('Impfquote Auffrischimpfung','18+ Jahre', '18-59 Jahre'), ('Impfquote Auffrischimpfung','18+ Jahre', '60+ Jahre')]]
df_booster.columns = ['Bundesland', '12-17 Jahre', '18-59 Jahre', '60+ Jahre']

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

# sort dict for drop down menu
id_bundesland_sorted = {}
id_bundesland_s = sorted(id_bundesland.items(), key = lambda kv:(kv[1], kv[0]))
for i in id_bundesland_s:
    id_bundesland_sorted[i[0]] = i[1]
sprache = {
    'h1': {'de': 'Impfquotenmonitoring', 'en': 'Vaccination rate monitoring', 'tr': 'Aşılama oranları'},
    'h2': {'de': 'in Deutlschand', 'en': 'in Germany', 'tr': 'Almanyada'},
    'hover': {'de': 'Gesamtanzahl an Impfungen', 'en': 'Total number of vaccinations', 'tr': 'Toplam aşılanma sayısı'}
}

#rki daten
df_bundes = df[0].copy()
df_bundes.drop([2],inplace=True) #row DE-BUND dropen
df_bundes['id'] = ['10','9','6','7','2','4','0','11','1','3','5','15','8','12','13','14']

#map -- first map
fig = px.choropleth(
        df_bundes, geojson=geojson, #nach id mappen, karte nach zahlen des rki
        locations="id",
        color = 'vaccinationsTotal',
        projection="mercator",
        color_continuous_scale="Viridis",
        range_color=[0, df_bundes['vaccinationsTotal'].max()],
        labels={'vaccinationsTotal':'Gesamtanzahl an Impfungen'}, # weitere infos ueber bundeslander to do!!
    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(hoverinfo="none",hovertemplate=None)

#figure mit impf fortschritt nach zeit
fig2 = px.line(df2_time, x='date', y=['dosen_erst_kumulativ','dosen_zweit_kumulativ','dosen_dritt_kumulativ'],
    labels={"date": "Datum", 
            "dosen_erst_kumulativ": "Erstimpfungen", 
            "dosen_zweit_kumulativ": "Zweitimpfungen", 
            "dosen_dritt_kumulativ": "Drittimpfungen",
            "value": "Anzahl Impfungen"})

fig2.update_layout(
    title="Impf-Fortschritt in Deutschland",
    xaxis_title="Datum",
    yaxis_title="Anzahl Impfungen in Deutschland",
    legend_title="Impfungen",
    yaxis_range=[0,90000000])

fig2.update_traces(mode="lines", hovertemplate=None)
fig2.update_layout(hovermode="x")

def custom_legends_names(new_names):
    for i, new_name in enumerate(new_names):
        fig2.data[i].name = new_name

dict = {
    'germanlabels': ["Erstimpfungen", "Zweitimpfungen", "Drittimpfungen"]
}

custom_legends_names(dict['germanlabels'])

#funktion selektiert tabellen für ausgewähltes bundesland
def selectState(statename):
  df_first = df_mindestens1x.loc[df_mindestens1x['Bundesland'] == statename]
  df_immun = df_grundimmunisiert.loc[df_grundimmunisiert['Bundesland'] == statename]
  df_boost = df_booster.loc[df_booster['Bundesland'] == statename]

  return df_first, df_immun, df_boost

#funktion macht den dataframe für die figure nach altersgruppen
def df4ageFig(statename):
  df_first, df_immun, df_boost = selectState(statename)
  merged_df = pd.concat([df_first, df_immun, df_boost])
  new_df = merged_df.drop(columns="Bundesland")
  
  col_content_DE = ['Mindestens einmal geimpft', 'Grundimmunisiert','Auffrischimpfung'] #Spalte auf Deutsch, andere Sprachen müssen noch hinzugefügt werden
  col_name_DE = 'Art der Impfquote' #Spaltenname auf Deutsch, andere Sprachen müssen noch hinzugefügt werden

  new_df.insert(loc=0, column=col_name_DE, value=col_content_DE)

  return new_df

df_agegroups = df4ageFig('Berlin') ########## Berlin ist hier ein dummy, da kommt dann nur statename rein, je nachdem was dann aufgerufen wird

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["5-11 Jahre"],
                     name="5-11 Jahre"))
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["12-17 Jahre"],
                     name="12-17 Jahre"))
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["18-59 Jahre"],
                     name="18-59 Jahre"))
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["60+ Jahre"],
                     name="60+ Jahre"))

fig3.update_layout(
    title="Impfquote nach Altersgruppe in Berlin", #hier muss noch die statename variable rein statt Berlin
    xaxis_title="Art der Impfquote", #andere Sprachen fehlen noch
    yaxis_title="Impfquote in Prozent (%)", #andere Sprachen fehlen noch
    )

app.layout = html.Div(children=[
    html.H1(children='Impfquotenmonitoring',
            style={'margin': '30px', 'textAlign': 'center'}),
    dcc.RadioItems(
        id='language',
        options=[
            {'label': 'DE', 'value': 'de'},
            {'label': 'EN', 'value': 'en'},
            {'label': 'TR', 'value': 'tr'}
        ],
        value='de',
        labelStyle={'display': 'inline-block'}
    ),
    html.H2(children='in Deutschland',
            style={'textAlign': 'center'}),

    #html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
    
    html.Div(style={'margin': '10px', 'width': '23%', 'float': 'left', 'display': 'inline-block'},
    children=[
        dcc.Dropdown(
            id='dropdown_bundeslander',
            options=[{'label': bundesland, 'value': id} for id, bundesland in id_bundesland_sorted.items()],
            placeholder="Verschiedene Bundesländer",
        ),
    ]),
    html.Div(
        style={'width': '100%','display':'inline-block','overflow': 'hidden'},
        children=[
            html.H3(id = 'bundesland_name',
            children=[],
            style={'textAlign': 'center'}),
        ]
    ),
    html.Div(
        style={'width': '100%','display':'inline-block','overflow': 'hidden'},  
        children=[
            html.H3(id = 'bundesland_name2',
            children=[],
            style={'textAlign': 'center'}),
        ]
    ),
    html.Div(
        style={'width': '100%','height': '800px','display':'inline-block','overflow': 'hidden'},  
        children=[
            dcc.Graph(id="germany",figure=fig, clear_on_unhover=True, style={'width': '100%', 'height': '80vh'}),
            dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
    html.P('© Bundesamt für Kartographie und Geodäsie, Frankfurt am Main, 2011'),
    html.Div(
        style={'width': '50%','height': '300px','display':'inline-block', 'float':'left'},  
        children=[
            html.H3('Hier kommt der Info Text hin')
        ]
    ),
    html.Div(
        style={'width': '50%','height': '100%','display':'inline-block', 'float':'right'},  
        children=[
            dcc.Graph(id="timeseries",figure=fig2, clear_on_unhover=True, style={'width': '100%', 'height': '70vh'}),
            #dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
    html.Div(
        style={'width': '100%','height': '600px','display':'inline-block',},  
        children=[
            dcc.Graph(id="agegroups",figure=fig3, clear_on_unhover=True, style={'width': '100%', 'height': '70vh'}),
            #dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
])

#hover information #
@app.callback(
    Output("tooltip_inf", "show"),
    Output("tooltip_inf", "bbox"),
    Output("tooltip_inf", "children"),
    Input("germany", "hoverData"),
)
def display_hover(hoverData): # here we have to add all the other infos needed for hover menu
    if hoverData is None:
        return False, no_update, no_update

    pt = hoverData["points"][0]
    # print('pt', pt)
    id = pt['location']
    # print('id', id)
    bbox = pt["bbox"]
    # print('bbox', bbox)
    num = pt["pointNumber"]
    # print('num', num)

    name = id_bundesland_sorted[id]

    df_row = df_bundes.iloc[num]
    total_count = df_row['vaccinationsTotal']
    # weil die zahlen so gross sind ist es uebersichtlicher wenn Kommas die tausender Positionen angeben
    new_count = locale.format_string("%.2f", total_count, grouping = True)[0:-3]
    children = [
        html.Div([
            html.H5(f"{name}",style={'textAlign': 'center'}),
            html.P(f"Gesamtanzahl an Impfungen: {new_count}"),
        ], style={'width': '300px', 'white-space': 'normal'})
    ]

    return True, bbox, children

#update fig nach dropdown
@app.callback(
    Output("germany", "figure"),
    [Input("dropdown_bundeslander", "value")])
def display_choropleth(value):
    # print('geojson[features]', geojson['features'])
    # print('value', value)
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

#dropdown bundesland überschrift
@app.callback(
    Output('bundesland_name', "children"), 
    [Input("dropdown_bundeslander", "value")])
def display_droptitle(value):
    if value:
        return id_bundesland[value]

if __name__ == '__main__':
    app.run_server()