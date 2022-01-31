from distutils.log import debug
from tkinter.ttk import Style
import pandas as pd
import numpy as np
import geopandas as gpd
#import locale
import math
import requests
import io
import dateutil
from datetime import datetime

import dash
from dash import dcc
from dash import html
from dash import no_update
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#locale.setlocale(locale.LC_ALL, '')

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

#pictogramm laden?
#image_filename = 'impf_pic.png' # replace with your own image
#encoded_image = pybase64.b64encode(open(image_filename, 'rb').read())

#corona inzidenzen - bundesländer über zeit
df_insidenz = pd.read_csv("https://raw.githubusercontent.com/jgehrcke/covid-19-germany-gae/master/cases-rki-by-state.csv")
#sub dataset
df_cases = pd.DataFrame(df_insidenz[['time_iso8601', 'sum_cases']])
df_cases.columns = ['date', 'cases']

#date formatieren 
ds = [dateutil.parser.parse(df_cases.iloc[i, 0]).replace(tzinfo=None) for i in range(len(df_cases))]
df_cases['date'] = ds
daily = df_cases['cases'] - df_cases['cases'].shift()
daily[0] = df_cases['cases'][0]
df_cases['cases'] = daily
df_cases = df_cases.drop(list(range(0,300)))
df_cases.reset_index(drop=True, inplace=True)

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

#impfungen pro tag
with io.BytesIO(download.content) as a:
    impfungen_daily = pd.io.excel.read_excel(a, "Impfungen_proTag", header=[0])
impfungen_daily =  impfungen_daily[[('Datum'),('Gesamtzahl verabreichter Impfstoffdosen')]] 
impfungen_daily.dropna(subset=['Gesamtzahl verabreichter Impfstoffdosen'], inplace=True) 
impfungen_daily.drop([len(impfungen_daily)-1], inplace=True) #drop gesamtanzahl an impfungen

daily = pd.concat([impfungen_daily, df_cases.reindex(impfungen_daily.index)], axis=1)
#print(daily)

# datenstand rki
url=    'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Impfquotenmonitoring.xlsx?__blob=publicationFile'
download = requests.get(url)

with io.BytesIO(download.content) as b:
    df_dataversionRKI = pd.io.excel.read_excel(b, "Erläuterung").fillna('')

#dataversion_RKI = df_dataversionRKI.iloc[0]['Digitales Impfquoten-Monitoring COVID-19 - Erläuterung']
#print(dataversion_RKI)
#print(df_dataversionRKI.head())
dataversion_RKI = df_dataversionRKI['Digitales Impfquoten-Monitoring COVID-19 - Erläuterung'].values[1]
#print(dataversion_RKI)
#print(type(dataversion_RKI))

#datenstand impfdashboard
r = requests.get('https://impfdashboard.de/static/data/metadata.json')
data = r.json()
dataversion_dashboard = data['vaccinationsLastUpdated']

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

#Impfquote grundimmunisiert
df_impfquote_grundimun = df3_agegroups[[('Bundesland','Unnamed: 1_level_1','Unnamed: 1_level_2'),('Impfquote grundimmunisiert','Gesamt-bevölkerung*', 'Unnamed: 13_level_2')]]
df_impfquote_grundimun.columns = ['Bundesland','Gesamtbevölkerung']
df_herdenimmun_grund = df_impfquote_grundimun['Gesamtbevölkerung'][17]
df_impfquote_grundimun = df_impfquote_grundimun[0:16]
df_impfquote_grundimun['id'] = list(id_bundesland_sorted.keys())
df_impfquote_grundimun['Gesamtbevölkerung'] = pd.to_numeric(df_impfquote_grundimun['Gesamtbevölkerung'])

#Impfquote einmal geimpft
df_impfquote_einmal = df3_agegroups[[('Bundesland','Unnamed: 1_level_1','Unnamed: 1_level_2'),('Impfquote mindestens einmal geimpft','Gesamt-bevölkerung*', 'Unnamed: 6_level_2')]]
df_impfquote_einmal.columns = ['Bundesland','Gesamtbevölkerung']
df_herdenimmun_einmal = df_impfquote_einmal['Gesamtbevölkerung'][17]
df_impfquote_einmal = df_impfquote_einmal[0:16]
df_impfquote_einmal['id'] = list(id_bundesland_sorted.keys())
df_impfquote_einmal['Gesamtbevölkerung'] = pd.to_numeric(df_impfquote_einmal['Gesamtbevölkerung'])

#Impfquote auffrischung
df_impfquote_auffrischung = df3_agegroups[[('Bundesland','Unnamed: 1_level_1','Unnamed: 1_level_2'),('Impfquote Auffrischimpfung','Gesamt-bevölkerung*', 'Unnamed: 20_level_2')]]
df_impfquote_auffrischung.columns = ['Bundesland','Gesamtbevölkerung']
df_herdenimmun_auffrischung = df_impfquote_auffrischung['Gesamtbevölkerung'][17]
df_impfquote_auffrischung = df_impfquote_auffrischung[0:16]
df_impfquote_auffrischung['id'] = list(id_bundesland_sorted.keys())
df_impfquote_auffrischung['Gesamtbevölkerung'] = pd.to_numeric(df_impfquote_auffrischung['Gesamtbevölkerung'])

#rki daten
df_bundes = df[0].copy()
df_bundes.drop([2],inplace=True) #row DE-BUND dropen
df_bundes['id'] = ['10','9','6','7','2','4','0','11','1','3','5','15','8','12','13','14']

#corona varianten
c_varianten = ['Alpha (B.1.1.7): 80%', 'Delta (B.1.617.2): 90%', 'Omikron (B.1.1.529): 95%']
varianten = {
    'a': {'de':'Alpha (B.1.1.7): 80%', 'en': 'Alpha (B.1.1.7): 80%', 'tr':'Alfa (B.1.1.7): %80'},
    'd': {'de':'Delta (B.1.617.2): 90%', 'en': 'Delta (B.1.617.2): 90%', 'tr':'Delta (B.1.617.2): %90'},
    'o': {'de':'Omikron (B.1.1.529): 95%', 'en':'Omicron (B.1.1.529): 95%', 'tr':'Omicron (B.1.1.529): %95'}
}

#different languages
sprache = {
    'h1': {'de': 'Impfquotenmonitoring', 'en': 'Vaccination rate monitoring', 'tr': 'Aşı oran takibi'},
    'h2': {'de': 'in Deutschland', 'en': 'in Germany', 'tr': 'Almanyada'},
    'hover': {'de': 'Gesamtanzahl an Impfungen', 'en': 'Total number of vaccinations', 'tr': 'Toplam aşılanma sayısı'},
    'placeholder_dropdown': {'de': 'Verschiedene Bundesländer', 'en': 'different states', 'tr': 'farklı eyaletler'},
    'impfquote': {'de': 'Impfquote', 'en': 'Vaccination rate', 'tr': 'Aşılanma oranı'},
    'impfquote_2mal': {'de': 'Vollständig geimpft', 'en': 'Fully vaccinated', 'tr': 'Tam aşılanmış'},
    'impfquote_einmal': {'de': 'Einmal geimpft', 'en': 'Vaccinated once', 'tr': 'Bir kez aşılanmış'},
    'impfquote_auffrischung': {'de': 'Auffrischungsimpfung', 'en': 'Booster vaccination', 'tr': 'Üçüncü kez aşılanmışlar'},
    'herdenimmunität': {'de': 'Herdenimmunität', 'en':'Herd immunity', 'tr': 'Sürü bağışıklığı'}

}

#map -- first map
fig = px.choropleth(
        df_impfquote_einmal, geojson=geojson, #nach id mappen, karte nach zahlen des rki
        locations="id",
        color = 'Gesamtbevölkerung',
        projection="mercator",
        color_continuous_scale= "Greens", #"Viridis"
        range_color=[math.floor(df_impfquote_einmal['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_einmal['Gesamtbevölkerung'].max())],
        labels={'Gesamtbevölkerung':'Impfquote'}, # weitere infos ueber bundeslander to do!!
    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
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

#figure mit impfquote nach altersgruppen
fig3_labels = {
            "5-11": {'de': "5-11 Jahre" , 'en': "5-11 years", 'tr': '5-11 yaş'},
            "12-17": {'de': "12-17 Jahre", 'en': "12-17 years", 'tr': '12-17 yaş'},
            "18-59": {'de': "18-59 Jahre", 'en': "18-59 years", 'tr': '18-59 yaş'},
            "60+": {'de': "60+ Jahre", 'en': "60+ years", 'tr': '60+ yaş'},
            "yaxis_title": {'de': 'Art der Impfquote', 'en': 'Type of vaccination rate', 'tr': "Aşılama oranın türü"},
            "xaxis_title": {'de': 'Impfquote in Prozent (%)', 'en': 'Vaccination rate in percent (%)', 'tr': 'Aşılama oranı yüzde olarak (%)'},
            #'title': {'de': 'Impfquote nach Altersgruppe in Berlin', 'en':'Vaccination rate as per age group in Berlin', 'tr': "Berlin'de yaş grublarına göre aşılama oranı"}, #hier muss berlin dann auch mit statename ersetzt werden
            "impfquote": {
            'de': ['Mindestens einmal geimpft', 'Grundimmunisiert (vollständig geimpft)', 'Auffrischimpfung'], 'en': ['At least once vaccinated', 'Initial immunization (fully vaccinated)', 'Booster vaccination'], 'tr': ['En az bir kez aşılanmış', 'Genel bağışıklık (tam aşılı)', 'Üçüncü aşı']
            }
}
        
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
 
#the colors for figure 3 are defined per color palette for color blind people: https://davidmathlogic.com/colorblind/#%23D81B60-%231E88E5-%23FFC107-%23004D40
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["5-11 Jahre"],
                     name="5-11 Jahre",
                     marker_color='#d81b60'))
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["12-17 Jahre"],
                     name="12-17 Jahre",
                     marker_color='#1e88e5'))
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["18-59 Jahre"],
                     name="18-59 Jahre",
                     marker_color='#ffc107'))
fig3.add_trace(go.Bar(x=df_agegroups["Art der Impfquote"],
                     y=df_agegroups["60+ Jahre"],
                     name="60+ Jahre",
                     marker_color='#004d40'))

fig3.update_layout(
    title="Impfquote nach Altersgruppe in Berlin", #hier muss noch die statename variable rein statt Berlin
    xaxis_title="Art der Impfquote", #andere Sprachen fehlen noch
    yaxis_title="Impfquote in Prozent (%)", #andere Sprachen fehlen noch
    )

# fig4_labels = {"date": {'de': "Datum", 'en': "Date", 'tr': 'Tarih'},
#             "inzidenz": {'de': "Inzidenzen" , 'en': "incidences", 'tr': 'vakalar'},
#             "impfdosen": {'de': "Impfstoffdosen", 'en': "vaccine doses", 'tr': 'aşı dozları'},
#             "yaxis1_title": {'de': 'COVID-19 Inzidenz', 'en': 'COVID-19 incidence', 'tr': "COVID-19 vakaları"},
#             "yaxis2_title": {'de': 'Verabreichte Impfdosen', 'en': 'Doses of vaccine administered', 'tr': "Uygulanan aşı dozları"},
#             'title': {'de': 'Zusammenhang zwischen Impfquote und Inzidenz', 'en':'Relationship between vaccination rate and incidence', 'tr': "Aşılama oranın ile vaka sayının arasındaki ilişki"},
#             'y0': {'de': 'Anzahl', 'en':'Count', 'tr': "Bazı"}
# }

# radio_IvsI = {'titel': {'de':'y-Achsen Einstellung: ', 'en': 'y-axis adjustment: ', 'tr': 'y eksen ayarı: '},
#               'y1': {'de':'y-Achsen Einstellung: ', 'en': 'y-axis adjustment: ', 'tr': 'y eksen ayarı: '},
#               'y2': {'de':'mit zweiter y-Achse ', 'en': 'with a second y-axis ', 'tr': 'ikinci y ekseni ile '},
#               'y0': {'de':'nur mit einer y-Achse ', 'en': 'only with one y-axis ', 'tr': 'sadece bir y ekseni ile '}
#     }

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
    html.Br(),
    html.Div(style={'margin': '10px', 'width': '50%', 'float': 'left', 'display': 'inline-block'},
        children = [
            html.Div(id ='herdenimmunität', 
                style={'float': 'right', 'display': 'inline-block'},
                children=[]
        ),
    ]),
    html.Div(id = 'herd_txt', 
        style={'margin': '10px', 'width': '45%', 'float': 'right', 'display': 'inline-block'},
        children = [
            html.H3(id = 'h3_herden'),
            html.P(id = 'herdenimmun_text', style={'text-align': 'justify', 'font-size': '9px'}),
            html.A(id ='1', href='https://www.infektionsschutz.de/coronavirus/basisinformationen/varianten-des-coronavirus-sars-cov-2/', target="_blank"),
            html.A(id ='2', href='https://www.quarks.de/gesundheit/medizin/warum-ein-impfstoff-die-pandemie-auch-2021-nicht-beendet/', target="_blank"),
            html.A(id ='3', href='https://www.swr.de/wissen/corona-pandemie-herdenimmunitaet-nicht-realistisch-100.html', target="_blank"),
            html.A(id ='4', href='https://kurier.at/chronik/welt/omikron-deutsche-regierung-herdenimmunitaet-erst-bei-95-prozent/401864954', target="_blank"),
            dcc.RadioItems(
                id='variante',
                #labelStyle={'display': 'block'},
                value=c_varianten[0],
                options=[{'label': x, 'value': x} for x in c_varianten]
            )
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
            html.H3('Hier kommt der Info Text hin')
        ]
    ),
    html.Div(
        style={'width': '50%','height': '100%','display':'inline-block', 'float':'right'},  
        children=[
            dcc.Graph(id="timeseries",figure=fig2, clear_on_unhover=True, style={'width': '100%', 'height': '70vh'}),
            #dcc.Tooltip(id="tooltip_inf"),
            html.Span('Datenstand: ' + str(dataversion_dashboard)),
        ]
    ),
    html.Div(
        style={'width': '100%','height': '100%','display':'inline-block',},  
        children=[
            dcc.Graph(id="agegroups",figure=fig3, clear_on_unhover=True, style={'width': '100%', 'height': '70vh'}),
            #dcc.Tooltip(id="tooltip_inf"),
        ]
    ),
    # html.Div(id = 'Inzidenz_vs_Impfung',
    #     style={'width': '100%','height': '100%','display':'inline-block'},  
    #     children=[
    #         dcc.Graph(id="inzidens"),
    #         html.Div(
    #             style={'width': '94%','height': '100%','float':'right'},
    #             children = [html.P(id='P_radio_IvsI'),
    #             dcc.RadioItems(
    #             id='radio',
    #             labelStyle={'display': 'block'},
    #             value=radio_IvsI['y2']['de'] + 'verabreichte Impfdosen',
    #             options=[{'label': x, 'value': x} for x in [radio_IvsI['y0']['de'], radio_IvsI['y2']['de']]]#[{'label': x, 'value': x} for x in [radio_IvsI['y0']['de'] + 'COVID-19 Inzidenz', radio_IvsI['y2']['de'] + 'verabreichte Impfdosen']
    #             )],
    #         ),
    #         html.Br(),
    #     ]
    # ),
    html.Br(),
    html.Br(),
    html.Div(
        id = 'rki_source',
        style={'width': '50%','height': '100%','display':'inline-block', 'float':'left'},
        children=[
            html.Span('Datenquellen: '),
            html.A('Robert Koch Institut - Impfquotenmonitoring',href='https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Impfquotenmonitoring.html', target="_blank"),
            html.A(', '),
            html.A('impfdashboard (RKI, BMG)', href='https://impfdashboard.de/daten', target="_blank")
        ]
    ),
    html.Div(
        id = 'data_version',
        style={'width': '50%','height': '100%','display':'inline-block', 'float':'right'},
        children=[
            html.Span(str(dataversion_RKI)),
        ]
    ),
])

#tabs
@app.callback(
    Output("tabs", "children"),
    Input("language", "value")
)
def update_fig2(language): 
    return[dcc.Tab(label=sprache['impfquote_einmal'][language], value='tab-1'),
    dcc.Tab(label=sprache['impfquote_2mal'][language], value='tab-2'),
    dcc.Tab(label=sprache['impfquote_auffrischung'][language], value='tab-3'),
    dcc.Tab(label=sprache['hover'][language], value='tab-4')]

#hover information #
@app.callback(
    Output("tooltip_inf", "show"),
    Output("tooltip_inf", "bbox"),
    Output("tooltip_inf", "children"),
    Input("germany", "hoverData"),
    Input("language", "value"),
    Input('tabs', 'value')
)
def display_hover(hoverData,language,tabs): # here we have to add all the other infos needed for hover menu
    if hoverData is None:
        return False, no_update, no_update

    pt = hoverData["points"][0]
    #print('pt', pt)
    id = pt['location']
    #print('id', id)
    bbox = pt["bbox"]
    #print('bbox', bbox)  
    num = pt["pointNumber"]
    #print('num', num)

    name = id_bundesland_sorted[id][language]

    if tabs == 'tab-1':

        #df_row = df_impfquote_einmal.iloc[num]
        total_count = pt["z"]#df_row['Gesamtbevölkerung']
        # weil die zahlen so gross sind ist es uebersichtlicher wenn Kommas die tausender Positionen angeben
        #new_count = locale.format_string("%.2f", total_count, grouping = True)[0:-3]
        if language != 'en':
            new_count = format(total_count, '').replace(".", ",")
        else:
            new_count = total_count

        children = [
            html.Div([
                html.H5(f"{name}",style={'textAlign': 'center'}),
                html.P(f"{sprache['impfquote'][language]}: {new_count} %"),
            ], style={'width': '300px', 'white-space': 'normal'})
        ]

    elif tabs == 'tab-2':

        #df_row = df_impfquote_grundimun.iloc[num]
        total_count = pt["z"] #df_row['Gesamtbevölkerung']
        # weil die zahlen so gross sind ist es uebersichtlicher wenn Kommas die tausender Positionen angeben
        #new_count = locale.format_string("%.2f", total_count, grouping = True)[0:-3]
        if language != 'en':
            new_count = format(total_count, '').replace(".", ",")
        else:
            new_count = total_count

        children = [
            html.Div([
                html.H5(f"{name}",style={'textAlign': 'center'}),
                html.P(f"{sprache['impfquote'][language]}: {new_count} %"),
            ], style={'width': '300px', 'white-space': 'normal'})
        ]

    elif tabs == 'tab-3':

        #df_row = df_impfquote_auffrischung.iloc[num]
        total_count = pt["z"]#df_row['Gesamtbevölkerung']
        # weil die zahlen so gross sind ist es uebersichtlicher wenn Kommas die tausender Positionen angeben
        #new_count = locale.format_string("%.2f", total_count, grouping = True)[0:-3]
        if language != 'en':
            new_count = format(total_count, '').replace(".", ",")
        else:
            new_count = total_count

        children = [
            html.Div([
                html.H5(f"{name}",style={'textAlign': 'center'}),
                html.P(f"{sprache['impfquote'][language]}: {new_count} %"),
            ], style={'width': '300px', 'white-space': 'normal'})
        ]

    elif tabs == 'tab-4':

        #df_row = df_bundes.iloc[num]
        total_count = pt["z"]#df_row['vaccinationsTotal']
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
    Input('tabs', 'value')
)
def display_choropleth(dropdown_bundeslander,language,tabs):
    # print('geojson[features]', geojson['features'])
    # print('value', value)

    #impquote einmal geimpft
    if tabs == 'tab-1':
        fig = px.choropleth(
        df_impfquote_einmal, geojson=geojson, #nach id mappen, karte nach zahlen des rki
        locations="id",
        color = 'Gesamtbevölkerung',
        projection="mercator",
        color_continuous_scale="Greens", #"Viridis"
        range_color=[math.floor(df_impfquote_einmal['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_einmal['Gesamtbevölkerung'].max())],
        labels={'Gesamtbevölkerung':sprache['impfquote'][language]}, 
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_traces(hoverinfo="none",hovertemplate=None)

        #einzelnes bundesland, wenn im dropdown ausgesucht
        if dropdown_bundeslander:

            geojson_bund = geojson['features'][int(dropdown_bundeslander)]
            df_bundes_bund = df_impfquote_einmal[df_impfquote_einmal['id']==dropdown_bundeslander]

            fig = px.choropleth(
                df_bundes_bund, geojson=geojson_bund ,
                locations="id",
                color = 'Gesamtbevölkerung',
                projection="mercator",
                color_continuous_scale="Greens",
                range_color=[math.floor(df_impfquote_einmal['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_einmal['Gesamtbevölkerung'].max())],
                labels={'Gesamtbevölkerung': sprache['impfquote'][language]})

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_traces(hoverinfo="none",hovertemplate=None)

    if tabs == 'tab-2':
        fig = px.choropleth(
        df_impfquote_grundimun, geojson=geojson, #nach id mappen, karte nach zahlen des rki
        locations="id",
        color = 'Gesamtbevölkerung',
        projection="mercator",
        color_continuous_scale="Greens", #"Viridis"
        range_color=[math.floor(df_impfquote_grundimun['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_grundimun['Gesamtbevölkerung'].max())],
        labels={'Gesamtbevölkerung':sprache['impfquote'][language]}, 
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_traces(hoverinfo="none",hovertemplate=None)

        #einzelnes bundesland, wenn im dropdown ausgesucht
        if dropdown_bundeslander:

            geojson_bund = geojson['features'][int(dropdown_bundeslander)]
            df_bundes_bund = df_impfquote_grundimun[df_impfquote_grundimun['id']==dropdown_bundeslander]

            fig = px.choropleth(
                df_bundes_bund, geojson=geojson_bund ,
                locations="id",
                color = 'Gesamtbevölkerung',
                projection="mercator",
                color_continuous_scale="Greens",
                range_color=[math.floor(df_impfquote_grundimun['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_grundimun['Gesamtbevölkerung'].max())],
                labels={'Gesamtbevölkerung': sprache['impfquote'][language]})

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_traces(hoverinfo="none",hovertemplate=None)

    if tabs == 'tab-3':
        fig = px.choropleth(
        df_impfquote_auffrischung, geojson=geojson, #nach id mappen, karte nach zahlen des rki
        locations="id",
        color = 'Gesamtbevölkerung',
        projection="mercator",
        color_continuous_scale="Greens", #"Viridis"
        range_color=[math.floor(df_impfquote_auffrischung['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_auffrischung['Gesamtbevölkerung'].max())],
        labels={'Gesamtbevölkerung':sprache['impfquote'][language]}, 
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_traces(hoverinfo="none",hovertemplate=None)

        #einzelnes bundesland, wenn im dropdown ausgesucht
        if dropdown_bundeslander:

            geojson_bund = geojson['features'][int(dropdown_bundeslander)]
            df_bundes_bund = df_impfquote_auffrischung[df_impfquote_auffrischung['id']==dropdown_bundeslander]

            fig = px.choropleth(
                df_bundes_bund, geojson=geojson_bund ,
                locations="id",
                color = 'Gesamtbevölkerung',
                projection="mercator",
                color_continuous_scale="Greens",
                range_color=[math.floor(df_impfquote_auffrischung['Gesamtbevölkerung'].min()), math.ceil(df_impfquote_auffrischung['Gesamtbevölkerung'].max())],
                labels={'Gesamtbevölkerung': sprache['impfquote'][language]})

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_traces(hoverinfo="none",hovertemplate=None)

    #gesamt anzahl
    elif tabs == 'tab-4':

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
        fig.update_layout(title='',margin={"r":0,"t":0,"l":0,"b":0})
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
            fig.update_layout(title='', margin={"r":0,"t":0,"l":0,"b":0})
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

#change H1 depending on language
@app.callback(
    Output("title", "children"),
    Input("language", "value"),
)
def display_H1(language):
    return html.H1(children=sprache['h1'][language], style={'margin': '30px', 'textAlign': 'center'})

#change H2 depending on language
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

    new_names = [fig2_labels['dosen_erst_kumulativ'][language], fig2_labels['dosen_zweit_kumulativ'][language], fig2_labels['dosen_dritt_kumulativ'][language]]

    for idx, name in enumerate(new_names):
        fig2.data[idx].name = name
        fig2.data[idx].hovertemplate = name

    #the colors for figure 2 are defined per color palette for color blind people: https://davidmathlogic.com/colorblind/#%23D81B60-%231E88E5-%23FFC107-%23004D40
    new_colors = ['#d81b60', '#1e88e5', '#ffc107']

    for idx, color in enumerate(new_colors):
        fig2.data[idx].line.color = color

    fig2.update_layout(
        title=fig2_labels['title'][language],
        xaxis_title=fig2_labels['date'][language],
        yaxis_title=fig2_labels['yaxis_title'][language],
        legend_title=fig2_labels['legend_title'][language],
        yaxis_range=[0,90000000])

    fig2.update_traces(mode="lines", hovertemplate=None)
    fig2.update_layout(hovermode="x")

    return fig2

#update fig3 sprache
@app.callback(
    Output("agegroups", "figure"),
    Input("language", "value"),
    [Input("dropdown_bundeslander", "value")]
)
def update_fig3(language, dropdown_bundeslander):
    # print('geojson[features]', geojson['features'])
    # print('value', value)
    statename = 'Gesamt'
    if dropdown_bundeslander:
        statename = (id_bundesland[dropdown_bundeslander]['de'])
        df_agegroups = df4ageFig(statename) ########## Berlin ist hier ein dummy, da kommt dann nur statename rein, je nachdem was dann aufgerufen wird
        title_languages = {'title': {'de': 'Impfquote nach Altersgruppe in ' + str(statename), 'en':'Vaccination rate as per age group in ' + str(statename), 'tr': str(statename) + "'de yaş grublarına göre aşılama oranı"}}
    else: 
        df_agegroups = df4ageFig(statename)
        title_languages = {'title': {'de': 'Impfquote nach Altersgruppe in Deutschland', 'en':'Vaccination rate as per age group in Germany', 'tr': "Almanyada yaş grublarına göre aşılama oranı"}}

    #print(statename)
    #print(df_agegroups.head())

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=fig3_labels['impfquote'][language],
                     y=df_agegroups["5-11 Jahre"],
                     name=fig3_labels['5-11'][language],
                     marker_color='#d81b60'))
    fig3.add_trace(go.Bar(x=fig3_labels['impfquote'][language],
                     y=df_agegroups["12-17 Jahre"],
                     name=fig3_labels['12-17'][language],
                     marker_color='#1e88e5'))
    fig3.add_trace(go.Bar(x=fig3_labels['impfquote'][language],
                     y=df_agegroups["18-59 Jahre"],
                     name=fig3_labels['18-59'][language],
                     marker_color='#ffc107'))
    fig3.add_trace(go.Bar(x=fig3_labels['impfquote'][language],
                     y=df_agegroups["60+ Jahre"],
                     name=fig3_labels['60+'][language],
                     marker_color='#004d40'))

    fig3.update_layout(
        title=title_languages['title'][language],
        xaxis_title=fig3_labels['xaxis_title'][language],
        yaxis_title=fig3_labels['yaxis_title'][language],
    )

    return fig3

@app.callback(
    Output("infotext", "children"),
    Input("language", "value")
)
def update_infotext(language):
    if language == 'de':
        return html.H3('Hier kommt der Info Text hin')
    elif language == 'en':
        return html.H3('Hier kommt der Info Text hin')
    else:
        return html.H3('Hier kommt der Info Text hin')

#herden div
@app.callback(
    Output('herd_txt', "children"),
    Input("tabs", "value"),
)
def herdenimmun_h3(tabs):  
    if tabs == 'tab-4':
        return []
    else:
        return [html.H4(id = 'h3_herden'),
            html.P(id = 'herdenimmun_text'),
            html.A(id ='1', href='https://www.infektionsschutz.de/coronavirus/basisinformationen/varianten-des-coronavirus-sars-cov-2/', target="_blank"),
            html.A(id ='2', href='https://www.quarks.de/gesundheit/medizin/warum-ein-impfstoff-die-pandemie-auch-2021-nicht-beendet/', target="_blank"),
            html.A(id ='3', href='https://www.swr.de/wissen/corona-pandemie-herdenimmunitaet-nicht-realistisch-100.html', target="_blank"),
            html.A(id ='4', href='https://kurier.at/chronik/welt/omikron-deutsche-regierung-herdenimmunitaet-erst-bei-95-prozent/401864954', target="_blank"),
            dcc.RadioItems(id='variante',
            #labelStyle={'display': 'block'},
            value=c_varianten[0],
            options=[{'label': x, 'value': x} for x in c_varianten]
            )
        ]

#variantan radio buttons
@app.callback(
    Output('variante', "value"),
    Input("language", "value"),
)
def herdenimmun_radio_value(value): 
     
    return  varianten['a'][value]

@app.callback(
    Output('variante', "options"),
    Input("language", "value"),
)
def herdenimmun_radio_options(value):  

    c_varianten = [varianten['a'][value],varianten['d'][value],varianten['o'][value]]

    return [{'label': x, 'value': x} for x in c_varianten]
    
#herdenimmunität H3
@app.callback(
    Output('h3_herden', "children"),
    Input("language", "value"),
)
def herdenimmun_h3(value):  
    return sprache['herdenimmunität'][value]   

#herdenimmunität text
@app.callback(
    Output('herdenimmun_text', "children"),
    Input("language", "value"),
)
def herdenimmun_text(value):  
    deutsch = 'Die Herdenimmunität gibt den Anteil der Bevölkerung an, die gegen das Virus immun sein müssen, damit sich er sich nicht mehr exponentiell weiterverbreiten kann. Diese hängt stark von der Reproduktionszahl (R0) ab, welche angibt, wie viele Menschen ein Infizierter im Schnitt ansteckt. Das RKI schätzte Anfang 2020 den R0 auf 3,3 bis 3,8, weswegen für eine Herdenimmunität von 70% ausgegangen wurde. Die Alpha-Variante B1.1.7 wies jedoch einen 1,5-fach höheren Reproduktionswert auf, wodurch die Herdenimmunität auf 80% stieg. Im Verlauf der Pandemie traten neue verschiedenen Varianten auf, darunter die Delta-Variante B.1.617.2. Im Vergleich zur Alpha-Variante, weist die Delta-Variante Mutationen auf, welche die Übertragbarkeit des Virus erhöhen. Das macht die Variante deutlich ansteckender, weshalb für einer Herdenimmunität eine Immunitätsquote von 90% erreicht werden muss. Mit der Omikron-Variante B.1.1.529 kammen eine ungewöhnlich hohe Anzahl von Mutationen mit. Darunter bekannte Mutationen, die die Übertragbarkeit des Virus erhöhen. Für Omikron wird von einer Herdenimmunität von 95% ausgegangen.'
    englisch = 'Herd immunity is the proportion of the population that must be immune to the virus to stop it from spreading exponentially. This depends heavily on the reproduction number (R0), which indicates how many people an infected person infects on average. At the beginning of 2020, the RKI estimated the R0 at 3.3 to 3.8, which is why a herd immunity of 70% was assumed. However, the alpha variant B1.1.7 had a 1.5-fold higher reproductive value, increasing herd immunity to 80%. As the pandemic progressed, new different variants emerged, including the delta variant B.1.617.2. Compared to the alpha variant, the delta variant has mutations that increase the transmissibility of the virus. This makes the variant much more contagious, which is why an immunity rate of 90% must be achieved for herd immunity. An unusually high number of mutations came along with the omicron variant B.1.1.529. These include known mutations that increase the transmissibility of the virus. A herd immunity of 95% is assumed for omicron.'
    türkisch = "Sürü bağışıklığı, virüsün katlanarak yayılmasını durdurmak için virüse karşı bağışık olması gereken nüfusun oranıdır. Bu, büyük ölçüde, enfekte olmuş bir kişinin ortalama olarak kaç kişiyi enfekte ettiğini gösteren üreme sayısına (R0) bağlıdır. 2020'nin başında RKI, R0'ı 3,3 ile 3,8 olarak tahmin etti, bu nedenle sürü bağışıklığının %70 olduğu varsayıldı. Bununla birlikte, alfa varyantı B1.1.7, 1.5 kat daha yüksek üreme değerine sahipti ve sürü bağışıklığını %80'e çıkardı. Pandemi ilerledikçe, delta varyantı B.1.617.2 dahil olmak üzere yeni farklı varyantlar ortaya çıktı. Alfa varyantı ile karşılaştırıldığında, delta varyantı, virüsün bulaşabilirliğini artıran mutasyonlara sahiptir. Bu, varyantı çok daha bulaşıcı hale getirir ve bu nedenle sürü bağışıklığı için %90'lık bir bağışıklık oranına ulaşılması gerekir. Omicron varyantı B.1.1.529 ile birlikte yüksek sayıda mutasyon geldi. Bunlar, virüsün bulaşabilirliğini artıran bilinen mutasyonları içerir. Omikron için %95'lik bir sürü bağışıklığı varsayılmaktadır."

    hs = {'de':deutsch, 'en':englisch, 'tr': türkisch}
    return hs[value]  

#herdenimmunität tacho
@app.callback(
    Output('herdenimmunität', "children"),
    Input("language", "value"),
    Input("tabs", "value"),
    Input('variante', "value"),
    Input("dropdown_bundeslander", "value")
)
def herdenimmun_anzeige(language,tabs,variante,dropdown_bundeslander):

    if variante == varianten['a'][language]:
        if tabs == 'tab-1':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,70], "yellow":[70,80], "green":[80,100]}},showCurrentValue=True, units="%", value= float(df_impfquote_einmal[df_impfquote_einmal['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else: 
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,70], "yellow":[70,80], "green":[80,100]}},showCurrentValue=True, units="%", value= df_herdenimmun_einmal,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-2':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,70], "yellow":[70,80], "green":[80,100]}},showCurrentValue=True, units="%",value= float(df_impfquote_grundimun[df_impfquote_grundimun['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else:     
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,70], "yellow":[70,80], "green":[80,100]}},showCurrentValue=True, units="%",value= df_herdenimmun_grund,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-3':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,70], "yellow":[70,80], "green":[80,100]}},showCurrentValue=True, units="%", value= float(df_impfquote_auffrischung[df_impfquote_auffrischung['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else: 
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,70], "yellow":[70,80], "green":[80,100]}},showCurrentValue=True, units="%", value= df_herdenimmun_auffrischung,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-4':
            return []
    
    elif variante == varianten['d'][language]:
        if tabs == 'tab-1':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,80], "yellow":[80,90], "green":[90,100]}},showCurrentValue=True, units="%", value= float(df_impfquote_einmal[df_impfquote_einmal['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else: 
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,80], "yellow":[80,90], "green":[90,100]}},showCurrentValue=True, units="%", value= df_herdenimmun_einmal,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-2':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,80], "yellow":[80,90], "green":[90,100]}},showCurrentValue=True, units="%",value= float(df_impfquote_grundimun[df_impfquote_grundimun['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else:     
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,80], "yellow":[80,90], "green":[90,100]}},showCurrentValue=True, units="%",value= df_herdenimmun_grund,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-3':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,80], "yellow":[80,90], "green":[90,100]}},showCurrentValue=True, units="%", value= float(df_impfquote_auffrischung[df_impfquote_auffrischung['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else: 
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,80], "yellow":[80,90], "green":[90,100]}},showCurrentValue=True, units="%", value= df_herdenimmun_auffrischung,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-4':
            return []

    else:
        if tabs == 'tab-1':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,85], "yellow":[85,95], "green":[95,100]}},showCurrentValue=True, units="%", value= float(df_impfquote_einmal[df_impfquote_einmal['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else: 
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,85], "yellow":[85,95], "green":[95,100]}},showCurrentValue=True, units="%", value= df_herdenimmun_einmal,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-2':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,85], "yellow":[85,95], "green":[95,100]}},showCurrentValue=True, units="%",value= float(df_impfquote_grundimun[df_impfquote_grundimun['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else:     
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,85], "yellow":[85,95], "green":[95,100]}},showCurrentValue=True, units="%",value= df_herdenimmun_grund,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-3':
            if dropdown_bundeslander:
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,85], "yellow":[85,95], "green":[95,100]}},showCurrentValue=True, units="%", value= float(df_impfquote_auffrischung[df_impfquote_auffrischung['id'] == dropdown_bundeslander]['Gesamtbevölkerung']),label=sprache['herdenimmunität'][language],max=100,min=0)
            else: 
                return daq.Gauge(color={"gradient":True,"ranges":{"white":[0,85], "yellow":[85,95], "green":[95,100]}},showCurrentValue=True, units="%", value= df_herdenimmun_auffrischung,label=sprache['herdenimmunität'][language],max=100,min=0)
        elif tabs == 'tab-4':
            return []

# #sprache updaten bei den radiobutten für das achsen wechseln bei Inzidenz_vs_Impfung
# @app.callback(
#     Output('P_radio_IvsI', "children"),
#     Input("language", "value"),
# )
# def update_langauge_radio_P(language):
#     return radio_IvsI['titel'][language]

# @app.callback(
#     Output('radio', "value"),
#     Input("language", "value"),
# )
# def update_langauge_radio_value(language):
#     return radio_IvsI['y2'][language]#+ fig4_labels['yaxis2_title'][language]

# @app.callback(
#     Output('radio', "options"),
#     Input("language", "value"),
# )
# def update_langauge_radio_opt(language):
#     return [{'label': x, 'value': x} for x in [radio_IvsI['y0'][language], radio_IvsI['y2'][language]]]
#     #[{'label': x, 'value': x} for x in [radio_IvsI['y0'][language] + fig4_labels['yaxis1_title'][language], radio_IvsI['y2'][language] + fig4_labels['yaxis2_title'][language]]]
            
    
# #figur  Inzidenz_vs_Impfung   
# @app.callback(
#     Output("inzidens", "figure"), 
#     [Input("radio", "value")],
#     Input("language", "value"))
# def display_(radio_value,language):

#     # Create figure with secondary y-axis
#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     # Add traces
#     fig.add_trace(
#         go.Scatter(x=daily['date'], y=daily['Gesamtzahl verabreichter Impfstoffdosen'], name=fig4_labels['impfdosen'][language]),
#         secondary_y=False,
#     )

#     fig.add_trace(
#         go.Scatter(x=daily['date'], y=daily['cases'], name=fig4_labels['inzidenz'][language]),
#         secondary_y=radio_value == radio_IvsI['y2'][language],
#     )

#     # Add figure title
#     fig.update_layout(
#         title_text=fig4_labels['title'][language]
#     )

#     fig.update_traces(mode="lines", hovertemplate=None)
#     fig.update_layout(hovermode="x") 

#     # Set x-axis title
#     fig.update_xaxes(title_text=fig4_labels['date'][language])

#     # Set y-axes titles
#     if radio_value != radio_IvsI['y2'][language]:
#         fig.update_yaxes(
#         title_text=fig4_labels['y0'][language], 
#         secondary_y=False)
#     else:
#         fig.update_yaxes(
#             title_text=fig4_labels['yaxis1_title'][language], 
#             secondary_y=False)

#     fig.update_yaxes(
#         title_text=fig4_labels['yaxis2_title'][language], 
#         secondary_y=True)

#     return fig


if __name__ == '__main__':
    app.run_server(debug=True)
