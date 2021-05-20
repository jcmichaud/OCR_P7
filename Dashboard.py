import json
import base64
import datetime
import io


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from components.functions import results_assessment, graph_age_income

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

train = pd.read_csv("Data/train20may21.csv")
train = train.set_index("SK_ID_CURR")
y_train = pd.read_csv("Data/y_train20may21.csv")
y_train = y_train.set_index("SK_ID_CURR")

train_complete = pd.concat([train,y_train],axis=1)#[['age','AMT_CREDIT','AMT_INCOME_TOTAL','TARGET']]

result_assessment = dcc.Graph(
    id='result_assessment',
    figure=results_assessment(min_value=55, 
                            your_application_value = 85
                            )
    )

slider_age=dcc.RangeSlider(
    id='slider_age',
    min=18,
    max=70,
    marks={i: '{} years'.format(i) for i in range(18, 70) if i%10==0},
    value=[18,70]
    )

slider_revenu=dcc.RangeSlider(id='slider_revenu',
                    min=0,
                    max=1000000,
                    marks={i: '{} k$'.format(int(i/1000)) for i in range(0, 1000000,100000)
                            },
                    value=[0,1000000])

age_income = dcc.Graph(
        id='age_income_graph',
        figure=graph_age_income(df=train_complete,
                    feature_figure_1 = 'AMT_CREDIT',
                    feature_figure_2 = 'age'
                    )
)

app.layout = html.Div([
    html.Div([
        html.Div([
                html.Label('Select age range'),
                slider_age,
                html.Label('Select revenu range'),
                slider_revenu
                ], 
                style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'}
                ),
        html.Div([
            html.Table([
                html.Tr([html.Td(['Age Range Selected']), html.Td(id='age_range_output')]),
                html.Tr([html.Td(['Revenu Range Selected']), html.Td(id='revenu_range_output')]),
            ])
        ]),
                
    ],style={'columnCount': 2,
        "background-color":'white',
        "height": "100vh"}),

    html.Div([
            html.Br(),
            result_assessment,
            html.Br(),
            age_income,
            html.Br()
            ],
            style={'columnCount': 2,
            "background-color":'white',
            "height": "100vh"}),
])




################ Treatment of Age Slider
@app.callback(
    Output(component_id='age_range_output', component_property='children'),
    Input('slider_age', 'value'),
    )
def update_output_div(input_value):
    return 'Age selected: {}'.format(input_value)
#########################################


################ Treatment of Revenu Slider
@app.callback(
    Output(component_id='revenu_range_output', component_property='children'),
    Input('slider_revenu', 'value')
    )
def update_output_div(input_value):
    return 'Revenu selected: {}'.format(input_value)
#########################################

################### Update Income graph

@app.callback(
    dash.dependencies.Output('age_income_graph', 'figure'),
    [dash.dependencies.Input('slider_revenu', 'value'),
     dash.dependencies.Input('slider_age', 'value')])

def update_graph(revenu_value, age_value):
    dff = train_complete.loc[
        (train_complete['AMT_INCOME_TOTAL']>=revenu_value[0])
        &(train_complete['AMT_INCOME_TOTAL']<=revenu_value[1])
        &(train_complete['age']>=age_value[0])
        &(train_complete['age']>=age_value[1])
                        ,:]

    fig = graph_age_income(df=dff,
                    feature_figure_1 = 'AMT_CREDIT',
                    feature_figure_2 = 'age'
                    )
    return fig



#########################################


if __name__ == '__main__':
        app.run_server(debug=True)
   
