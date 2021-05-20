import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from components.functions import results_assessment

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

result_assessment = dcc.Graph(
        id='result_assessment',
        figure=results_assessment(min_value=55, 
                                 your_application_value = 85
                                )
)

slider_age=dcc.RangeSlider(id='slider_age',
                    min=1,
                    max=9,
                    marks={i: '{}-{}'.format(i*10, i*10+9) for i in range(1, 8)},
                    value=[1,8])

slider_revenu=dcc.RangeSlider(id='slider_revenu',
                    min=0,
                    max=1000000,
                    marks={i: '{} $'.format(i) for i in range(0, 1000000,100000)
                            },
                    value=[1,8])

app.layout = html.Div(
    [
    html.Br(),
    result_assessment,
    html.Hr(),
    
    html.Label('Select age range'),
    slider_age, 
    html.Hr(),

    html.Label('Select revenu range'),
    slider_revenu,
    html.Table([
        html.Tr([html.Td(['Age Range Selected']), html.Td(id='age_range_output')]),
        html.Tr([html.Td(['Revenu Range Selected']), html.Td(id='revenu_range_output')]),
    ]), 
    html.Hr()
    ],
    style={'columnCount': 3,
    "background-color":'white',
    "height": "100vh"})

@app.callback(
    Output(component_id='age_range_output', component_property='children'),
    Input('slider_age', 'value'),
    )
def update_output_div(input_value):
    return 'Output: {}'.format(input_value)

@app.callback(
    Output(component_id='revenu_range_output', component_property='children'),
    Input('slider_revenu', 'value')
    )
def update_output_div(input_value):
    return 'Output: {}'.format(input_value)

if __name__ == '__main__':
    app.run_server(debug=True)
   
