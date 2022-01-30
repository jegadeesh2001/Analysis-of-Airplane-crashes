import numpy as np
import statsmodels.api as sm
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)



app.layout = html.Div(children= [

    dcc.Location(id='url', refresh=False),
    html.H1("AVIATION CRASH ANALYSIS",
            style={'text-align': 'center', 'color': 'black', 'backgroundColor': 'white'}),
    html.P(dcc.Link('Enter Dashboard', href='/page-1'), style={'text-align': 'center', 'color': 'white'}),
    html.Div(id='page-content'),
])
#
#Dataset and preprocessing
Data = pd.read_csv('Airplane_Crashes_and_Fatalities_Since_1908.csv')
Data['Time'] = Data['Time'].replace(np.nan, '00:00')
Data['Time'] = Data['Time'].str.replace('c: ', '')
Data['Time'] = Data['Time'].str.replace('c:', '')
Data['Time'] = Data['Time'].str.replace('c', '')
Data['Time'] = Data['Time'].str.replace('12\'20', '12:20')
Data['Time'] = Data['Time'].str.replace('18.40', '18:40')
Data['Time'] = Data['Time'].str.replace('0943', '09:43')
Data['Time'] = Data['Time'].str.replace('22\'08', '22:08')
Data['Time'] = Data['Time'].str.replace('114:20', '00:00')

Data['Time'] = Data['Date'] + ' ' + Data['Time']
def todate(x):
    return datetime.strptime(x, '%m/%d/%Y %H:%M')
Data['Time'] = Data['Time'].apply(todate)
print('Date ranges from ' + str(Data.Time.min()) + ' to ' + str(Data.Time.max()))

Data.Operator = Data.Operator.str.upper()

Data.dropna(subset=['Operator'],inplace=True)
Data.drop('Flight #',axis=1,inplace=True)
Data.drop('Route',axis=1,inplace=True)

Data.dropna(subset=['Type'],inplace=True)
Data.drop('Registration',axis=1,inplace=True)
Data.drop('cn/In',axis=1,inplace=True)

Data.Ground=Data.Ground.fillna(Data.Ground.median())

Data.dropna(subset=['Aboard','Fatalities'],how='any',inplace=True)
Data.dropna(subset=["Summary"],inplace=True)


#PLOTS
Temp = Data.groupby(Data.Time.dt.year)[['Date']].count() #Temp is going to be temporary data frame
Temp = Temp.rename(columns={"Date": "Count"})

fig1 = px.line(Temp,y="Count", title='Airplane Crashes Yearly')
#
#
Fatalities1 = Data.groupby(Data.Time.dt.year).sum()
fig2 = px.bar(Fatalities1, y=["Aboard","Fatalities"],title="Fatalities and Aboard VS Year")
#
#
OType = Data.groupby('Operator')['Fatalities', 'Aboard'].sum()
OType = OType.sort_values(by='Fatalities', ascending=False)
Osl=OType[:10]
fig3 = px.pie(Osl,names=Osl["Fatalities"].index ,values=Osl["Fatalities"],title="FATALITIES BASED ON TYPE OF OPERATOR")
#
#
PType = Data.groupby('Type')['Fatalities', 'Aboard'].sum()
PType = PType.sort_values(by='Fatalities', ascending=False)
psl=PType[:10]
fig4 = px.pie(psl,names=psl["Fatalities"].index ,values=psl["Fatalities"],title="FATALITIES BASED ON TYPE OF AIRCRAFTS")
#
#
co=pd.DataFrame(Data.Operator.value_counts().sort_values(ascending=False)[:10])
fig5 = px.bar(co, x=co["Operator"].index, y="Operator",title="TOP 10 CRASHES BY OPERATOR",labels=dict(Operator="Number of Crashes",index="Operator"))
fig5.update_traces(marker_color='LightSkyBlue')
fig5.update_layout(width=1000, height=700)

#
#
cm=pd.DataFrame(Data.Type.value_counts().sort_values(ascending=False))[:10]
fig6 = px.bar(cm, x=cm["Type"].index, y="Type",title="TOP 10 CRASHES BY TYPE OF FLIGHT",labels=dict(Type="Number of Crashes",index="Type of Air-Craft"))
fig6.update_traces(marker_color='MediumPurple')
fig6.update_layout(width=1000, height=700)
#
#
df=Data.copy()
df['Year'] = pd.DatetimeIndex(df['Date']).year
Gdy= df[['Year','Fatalities', 'Ground']].groupby('Year').sum()

fig7=px.line(Gdy,x=Gdy["Ground"].index,y="Ground")

#
#
fig8 = px.scatter_matrix(Data,
    dimensions=["Aboard", "Fatalities","Ground"],width=1000,height=1000)

#
#
fig9 = px.scatter(Data, x="Aboard", y="Fatalities", trendline="ols",trendline_color_override="red")

#
#

Temp = Data.groupby(Data.Time.dt.year)[['Date']].count()
Temp = Temp.rename(columns={"Date": "NOC"})

fig10 = px.scatter(Temp,x=Temp["NOC"].index,y="NOC",trendline="ols",trendline_color_override="red",labels=dict(NOC="NUMBER OF CRASHES",Time="YEAR"))


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return html.Div(children=[
            html.Div(
                [
                    html.A(
                        html.Button("Colab link", id="learn-more-button"),
                        href="https://colab.research.google.com/drive/1_C1xhK54joJyhgqLTgROcuj5r2OqZTw4?usp=sharing",
                    )
                ],
                className="one-third column",
                id="button",
            ),
            # All elements from the top of the page
            html.Div([
                html.Div([
                    html.H1(children='NUMBER OF PLANE CRASHES YEAR-WISE', style={'text-align': 'center', 'backgroundColor': 'white'}),

                    dcc.Graph(
                        id='graph1',
                        figure=fig1
                    ),
                    html.Div(children='''
                        INFERENCE: There are two spikes in the graph , one was during the time of World War-II(1939-1945) and another was when people started using Airlines more frequently to reduce time of travelling.
                '''),
                ], className='six columns'),
                html.Div([
                    html.H1(children='FATALITIES VS ABOARD', style={'text-align': 'center', 'backgroundColor': 'white'}),

                    dcc.Graph(
                        id='graph2',
                        figure=fig2
                    ),
                    html.Div(children='''
                        INFERENCE: From this graph, we can say that more than 60% of people who were aboard have died on plane crashes. The highest deaths was in year 1972.
                '''),
                ], className='six columns'),
            ], className='row'),
            # New Div for all elements in the new 'row' of the page
            html.Div([
                html.Br(),
                html.H1(children='CRASHES BY OPERATORS RESULTING IN HIGHER FATALITY RATES', style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph3',
                    figure=fig3
                ),
                html.Div(children='''
                        INFERENCE: From the graph, Highest crashes was made by AEROFLOT operator and the least crashes was made by INDIAN AIRLINES.
                        8,231 passengers have died in Aeroflot crashes, about five times more than any other airline. From 1946 to 1989, the carrier was involved in 721 incidents. However, from 1995 to 2017, the carrier was involved in 10 incidents.
                '''),
            ], className='row'),

            html.Div([
                html.Br(),
                html.H1(children='CRASHES BY TYPE OF AIRCRAFTS RESULTING IN HIGHER FATALITY RATES',
                        style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph4',
                    figure=fig4
                ),
                html.Div(children='''
                        INFERENCE: Douglas DC-3 is the flight used by US governament during world war-2 and 90% of US flights are of this model during WW2. This is why Douglas DC-3 is having highest nuber of crashes.
                '''),
            ], className='row'),

            html.Div([
                html.Br(),
                html.H1(children='MOST NUMBER OF CRASHES BY AN OPERATOR',
                        style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph5',
                    figure=fig5
                ),
                html.Div(children='''
                        INFERENCE: As Russia and US are two powerhouses of WW2, they are having most number of crashes with respect to Operator
                '''),
            ], className='row'),

            html.Div([
                html.Br(),
                html.H1(children='MOST NUMBER OF CRASHES WITH RESPECT TO TYPE OF FLIGHT',
                        style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph6',
                    figure=fig6
                ),
                html.Div(children='''
                        
                '''),
            ], className='row'),

            html.Div([
                html.Br(),
                html.H1(children='9/11 TRAGEDY', style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph7',
                    figure=fig7
                ),
                html.Div(children='''
                        INFERENCE: The year 2001 had the highest deaths in Ground accounting to about 5641 deaths,This dreadful number of people killed on the ground was due to the tragic event of 9/11, where the Twin Towers were brought down by two planes hijacked by terrorists.
                        Some 2,750 people were killed in New York, 184 at the Pentagon, and 40 in Pennsylvania (where one of the hijacked planes crashed after the passengers attempted to retake the plane); All 19 terrorists died .The Attack was Co-ordinated by Osama-Bin-Laden 
                '''),
            ], className='row'),
            html.Div([
                html.Br(),
                html.H1(children='Scatter Plot Matrix', style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph7',
                    figure=fig8
                ),
                html.Div(children='''
                                INFERENCE: From the above scatter plot matrix, we can observe that Aboard and Fatalities are Highly-Corelated to each other.
                        '''),
            ], className='row'),

            html.Div([
                html.Br(),
                html.H1(children='FATALITIES VS ABOARD TREND', style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph9',
                    figure=fig9
                ),
                html.Div(children='''
                        INFERENCE: Here we are finding the Regression Line using Ordinary Least-Squares approach
Fatalities is the Dependent Variable and Aboard is the Predictor Variable
The Regression line in the above scenario is
  Fatalities= 0.588 * Aboard + 4.0318
                '''),
            ], className='row'),

            html.Div([
                html.Br(),
                html.H1(children='CRASHES TREND', style={'text-align': 'center', 'backgroundColor': 'white'}),

                dcc.Graph(
                    id='graph10',
                    figure=fig10
                ),
                html.Div(children='''
                        INFERENCE: Here We are Predicting the number of Crashes in the Upcoming Years using the Regression Line ,which we have found using OLS approach
The Regression Line in the above Scenario is
Count = 0.788 * Time - 1496.19
                '''),
            ], className='row'),
        ])


if __name__ == '__main__':
    app.run_server(debug=True)