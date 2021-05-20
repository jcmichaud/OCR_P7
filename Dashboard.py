import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from result_assessment import result_assessment

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

result_assessment = dcc.Graph(
        id='result_assessment',
        figure=result_assessment(min_value=55, 
                                 your_application_value = 85
                                )
)

app.layout = html.Div([html.Br(),result_assessment, html.Br(),html.Br(), html.Br()],style={"background-color":'black',"height": "100vh"})



if __name__ == '__main__':
    app.run_server(debug=True)
   
