from distutils.log import debug
import pandas as pd
import geopandas as gpd
#import locale
import math

import dash
from dash import dcc
from dash import html
from dash import no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

#locale.setlocale(locale.LC_ALL, '')

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

#deutschland-karte
geo_df  = 'data/vg2500_geo84/vg2500_bld.shp'
map_df = gpd.read_file(geo_df)
geojson = map_df.__geo_interface__

#ids der Bundesländer in geo_df

id_bundesland = {
    '0': {'de': 'Hamburg', 'en': 'Hamburg', 'tr': 'Hamburg'},
    '1': {'de': 'Niedersachsen', 'en': 'Lower Saxony', 'tr': 'Aşağı Saksonya'},
    '2': {'de': 'Bremen', 'en': 'Bremen', 'tr': 'Bremen'},
    '3': {'de': 'Nordrhein-Westfalen', 'en': 'North Rhine-Westphalia', 'tr': 'Kuzey Ren-Vestfalyan'},
    '4': {'de': 'Hessen', 'en': 'Hesse', 'tr': 'Hesse'},
    '5': {'de': 'Rheinland-Pfalz', 'en': 'Rhineland-Palatinate', 'tr': 'Rheinland-Pfalz'},
    '6': {'de': 'Baden-Württemberg', 'en': 'Baden-Wuerttemberg', 'tr': 'Baden-Württemberg'},
    '7': {'de': 'Bayern', 'en': 'Bavaria', 'tr': 'Bavyera'},
    '8': {'de': 'Saarland', 'en': 'Saarland', 'tr': 'Saarland'},
    '9': {'de': 'Berlin', 'en': 'Berlin', 'tr': 'Berlin'},
    '10': {'de': 'Brandenburg', 'en': 'Brandenburg', 'tr': 'Brandenburg'},
    '11': {'de': 'Mecklenburg-Vorpommern', 'en': 'Mecklenburg-Western Pomerania', 'tr': 'Mecklenburg-Batı Pomeranya'},
    '12': {'de': 'Sachsen', 'en': 'Saxony', 'tr': 'Saksonya'},
    '13': {'de': 'Sachsen-Anhalt', 'en': 'Saxony-Anhalt', 'tr': 'Saksonya-Anhalt'},
    '14': {'de': 'Thüringen', 'en': 'Thuringia', 'tr': 'Bremen'},
    '15': {'de': 'Schleswig-Holstein', 'en': 'Schleswig Holstein', 'tr': 'Schleswig Holstein'}
}


# sort dict for drop down menu
def sort_id_bundesland(bundesland_dict,language):
    id_bundesland_sorted = {}
    id_bundesland_s = sorted(bundesland_dict.items(), key = lambda kv:(kv[1][language], kv[0]))
    for i in id_bundesland_s:
        id_bundesland_sorted[i[0]] = i[1]
    return id_bundesland_sorted

id_bundesland_sorted = sort_id_bundesland(id_bundesland,'de')
dropdown_list = [{'label': bundesland['de'], 'value': id} for id, bundesland in id_bundesland_sorted.items()]
pach = 'Verschiedene Bundesländer'

#rki daten
df_bundes = df[0].copy()
df_bundes.drop([2],inplace=True) #row DE-BUND dropen
df_bundes['id'] = ['10','9','6','7','2','4','0','11','1','3','5','15','8','12','13','14']

#different languages
sprache = {
    'h1': {'de': 'Impfquotenmonitoring', 'en': 'Vaccination rate monitoring', 'tr': 'Aşı oran takibi'},
    'h2': {'de': 'in Deutlschand', 'en': 'in Germany', 'tr': 'Almanyada'},
    'hover': {'de': 'Gesamtanzahl an Impfungen', 'en': 'Total number of vaccinations', 'tr': 'Toplam aşılanma sayısı'},
    'placeholder_dropdown': {'de': 'Verschiedene Bundesländer', 'en': 'different states', 'tr': 'farklı eyaletler'},
    'impfquote': {'de': 'Impfquote', 'en': 'Vaccination rate', 'tr': 'Aşı oran'}
}

#map -- first map
fig = px.choropleth(
        df_bundes, geojson=geojson, #nach id mappen, karte nach zahlen des rki
        locations="id",
        color = 'vaccinationsTotal',
        projection="mercator",
        color_continuous_scale="Greens", #"Viridis"
        range_color=[0, df_bundes['vaccinationsTotal'].max()],
        labels={'vaccinationsTotal':'Gesamtanzahl an Impfungen'}, # weitere infos ueber bundeslander to do!!
    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(hoverinfo="none",hovertemplate=None)

#figure mit impf fortschritt nach zeit
fig2_labels = {"date": {'de': "Datum", 'en': "Date", 'tr': 'Tarih'},
            "dosen_erst_kumulativ": {'de': "Erstimpfungen" , 'en': "initial vaccinations", 'tr': 'ilk aşılar'},
            "dosen_zweit_kumulativ": {'de': "Zweitimpfungen", 'en': "second vaccinations", 'tr': 'ikinci aşılar'},
            "dosen_dritt_kumulativ": {'de': "Drittimpfungen", 'en': "third vaccinations", 'tr': 'üçüncü aşılar'},
            "value": {'de': "Anzahl Impfungen", 'en': "number of vaccinations", 'tr': 'aşılanma sayısı'},
            "yaxis_title": {'de': 'Anzahl Impfungen in Deutschland', 'en': 'Number of vaccinations in Germany', 'tr': "Almanya'daki aşılanma sayıları"},
            "legend_title": {'de': 'Impfungen', 'en': 'Vaccinations', 'tr': 'Aşılamalar'},
            'title': {'de': 'Impf-Fortschritt in Deutschland', 'en':'Vaccination progress in Germany', 'tr': "Almanya'da aşı ilerlemesi"}
}

fig2 = px.line(df2_time, x='date', y=['dosen_erst_kumulativ','dosen_zweit_kumulativ','dosen_dritt_kumulativ'],
    labels={"date": fig2_labels['date']['de'],
            "dosen_erst_kumulativ": fig2_labels['dosen_erst_kumulativ']['de'],
            "dosen_zweit_kumulativ": fig2_labels['dosen_zweit_kumulativ']['de'],
            "dosen_dritt_kumulativ": fig2_labels['dosen_dritt_kumulativ']['de'],
            "value": fig2_labels['value']['de']})

fig2.update_layout(
    title=fig2_labels['title']['de'],
    xaxis_title=fig2_labels['date']['de'],
    yaxis_title=fig2_labels['yaxis_title']['de'],
    legend_title=fig2_labels['legend_title']['de'],
    yaxis_range=[0,90000000])

fig2.update_traces(mode="lines", hovertemplate=None)
fig2.update_layout(hovermode="x")


def custom_legends_names(new_names):
    for i, new_name in enumerate(new_names):
        fig2.data[i].name = new_name

custom_legends_names([fig2_labels['dosen_erst_kumulativ']['de'], fig2_labels['dosen_zweit_kumulativ']['de'], fig2_labels['dosen_dritt_kumulativ']['de']])

app.layout = html.Div(children=[
    #titel and radio RadioItems
    html.Div(
        style={'width': '100%','display':'inline-block','overflow': 'hidden'},
        children = [
            html.Div(
                id = 'title',
                style={'width': '80%','display':'inline-block','overflow': 'hidden'},
                children = []
            ),
            html.Div(
                style={'width': '10%','display':'inline-block','overflow': 'hidden', 'float':'left'},
                children = [
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
            ]),
    ]),

    html.H2(id = 'subtitle',
            children= [],
            style={'textAlign': 'center'}),

    #html.Img(src='data:image/png;base64,{}'.format(encoded_image)),

    html.Div(
        id = 'dropdown',
        style={'margin': '10px', 'width': '23%', 'float': 'left', 'display': 'inline-block'},
        children=[
            dcc.Dropdown(id='dropdown_bundeslander', options=dropdown_list, placeholder=pach),
        ]
    ),

    dcc.Tabs(id="tabs", value='tab-1', children=[]),

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
        id = 'tab_input',
        style={'width': '100%','height': '700px','display':'inline-block','overflow': 'hidden'},
        children=[
            dcc.Graph(id="germany",figure=fig, clear_on_unhover=True, style={'width': '100%', 'height': '80vh'}),
            dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
    html.P('© Bundesamt für Kartographie und Geodäsie, Frankfurt am Main, 2011'),
    html.Div(
        id = 'infotext',
        style={'width': '50%','height': '300px','display':'inline-block', 'float':'left'},
        children=[
            #html.H3('Hier kommt der Info Text hin') müsste unten bei den callbacks gemacht werden wegen den verschiedenen sprachen
        ]
    ),
    html.Div(
        style={'width': '50%','height': '300px','display':'inline-block', 'float':'right'},
        children=[
            dcc.Graph(id="timeseries",figure=fig2, clear_on_unhover=True, style={'width': '100%', 'height': '70vh'}),
            #dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
])

#tabs
#@app.callback(
#    Output("tabs", "children"),
#    Input("language", "value")
#)
#def update_fig2(language):
#    return[dcc.Tab(label=sprache['impfquote'][language], value='tab-1'),
#    dcc.Tab(label=sprache['hover'][language], value='tab-2')]

#hover information #
@app.callback(
    Output("tooltip_inf", "show"),
    Output("tooltip_inf", "bbox"),
    Output("tooltip_inf", "children"),
    Input("germany", "hoverData"),
    Input("language", "value"),
)
def display_hover(hoverData,language): # here we have to add all the other infos needed for hover menu
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

    name = id_bundesland_sorted[id][language]

    df_row = df_bundes.iloc[num]
    total_count = df_row['vaccinationsTotal']
    # weil die zahlen so gross sind ist es uebersichtlicher wenn Kommas die tausender Positionen angeben
    #new_count = locale.format_string("%.2f", total_count, grouping = True)[0:-3]
    if language == 'en':
        new_count = format(total_count, ',')
    else: 
        new_count = format(total_count, ',').replace(",", ".")
    children = [
        html.Div([
            html.H5(f"{name}",style={'textAlign': 'center'}),
            html.P(f"{sprache['hover'][language]}: {new_count}"),
        ], style={'width': '300px', 'white-space': 'normal'})
    ]

    return True, bbox, children

#update fig nach sprache und dropdown
@app.callback(
    Output("germany", "figure"),
    [Input("dropdown_bundeslander", "value")],
    Input("language", "value"),
    #Input('tabs', 'value')
)
def display_choropleth(dropdown_bundeslander,language,tabs):
    # print('geojson[features]', geojson['features'])
    # print('value', value)
    #if tabs == 'tab-1':
        

    #elif tabs == 'tab-2':

        #deutschland karte 
    fig = px.choropleth(
        df_bundes, geojson=geojson,
        locations="id",
        color = 'vaccinationsTotal',
            projection="mercator",
            color_continuous_scale="Greens",
            range_color=[0, df_bundes['vaccinationsTotal'].max()],
            labels={'vaccinationsTotal': sprache['hover'][language]})

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(hoverinfo="none",hovertemplate=None)

        #einzelnes bundesland, wenn im dropdown ausgesucht
    if dropdown_bundeslander:

        geojson_bund = geojson['features'][int(dropdown_bundeslander)]
        df_bundes_bund = df_bundes[df_bundes['id']==dropdown_bundeslander]

        fig = px.choropleth(
            df_bundes_bund, geojson=geojson_bund ,
            locations="id",
            color = 'vaccinationsTotal',
            projection="mercator",
            color_continuous_scale="Greens",
            range_color=[0, df_bundes['vaccinationsTotal'].max()],
            labels={'vaccinationsTotal': sprache['hover'][language]})

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_traces(hoverinfo="none",hovertemplate=None)

    return fig

#dropdown bundesland überschrift
@app.callback(
    Output('bundesland_name', "children"),
    [Input("dropdown_bundeslander", "value")],
    Input("language", "value"))
def display_droptitle(dropdown_bundeslander,language):
    if dropdown_bundeslander:
        return id_bundesland[dropdown_bundeslander][language]

#chage H1 depending on language
@app.callback(
    Output("title", "children"),
    Input("language", "value"),
)
def display_H1(language):
    return html.H1(children=sprache['h1'][language], style={'margin': '30px', 'textAlign': 'center'})

#chage H2 depending on language
@app.callback(
    Output('subtitle', "children"),
    Input("language", "value"),
)
def display_H2(language):
    return html.H2(children=sprache['h2'][language])

#update dropdown_list depending on language
@app.callback(
    Output('dropdown_bundeslander', "options"),
    Input("language", "value"),
)
def update_dropdown_list(language):
    id_bundesland_sorted = sort_id_bundesland(id_bundesland,language)
    dropdown_list = [{'label': bundesland[language], 'value': id} for id, bundesland in id_bundesland_sorted.items()]
    return dropdown_list

#update dropdown placeholder depending on language
@app.callback(
    Output('dropdown_bundeslander', "placeholder"),
    Input("language", "value"),
)
def update_dropdown(language):
    return sprache['placeholder_dropdown'][language]

#update fig2 sprache
@app.callback(
    Output("timeseries", "figure"),
    Input("language", "value")
)
def update_fig2(language):
    # print('geojson[features]', geojson['features'])
    # print('value', value)
    fig2 = px.line(df2_time, x='date', y=['dosen_erst_kumulativ','dosen_zweit_kumulativ','dosen_dritt_kumulativ'],
        labels={"date": fig2_labels['date'][language],
                "dosen_erst_kumulativ": fig2_labels['dosen_erst_kumulativ'][language],
                "dosen_zweit_kumulativ": fig2_labels['dosen_zweit_kumulativ'][language],
                "dosen_dritt_kumulativ": fig2_labels['dosen_dritt_kumulativ'][language],
                "value": fig2_labels['value'][language]})

    custom_legends_names([fig2_labels['dosen_erst_kumulativ'][language], fig2_labels['dosen_zweit_kumulativ'][language], fig2_labels['dosen_dritt_kumulativ'][language]])

    fig2.update_layout(
        title=fig2_labels['title'][language],
        xaxis_title=fig2_labels['date'][language],
        yaxis_title=fig2_labels['yaxis_title'][language],
        legend_title=fig2_labels['legend_title'][language],
        yaxis_range=[0,90000000])

    fig2.update_traces(mode="lines", hovertemplate=None)
    fig2.update_layout(hovermode="x")

    return fig2

@app.callback(
    Output("infotext", "children"),
    Input("language", "value")
)
def update_fig2(language):
    if language == 'de':
        return html.H3('Hier kommt der Info Text hin')
    elif language == 'en':
        return html.H3('Hier kommt der Info Text hin')
    else:
        return html.H3('Hier kommt der Info Text hin')


if __name__ == '__main__':
    app.run_server(debug=True)
