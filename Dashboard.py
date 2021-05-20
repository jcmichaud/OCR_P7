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

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8'))
                ,sep=",")
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing the file:' + filename + '.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


result_assessment = dcc.Graph(
        id='result_assessment',
        figure=results_assessment(min_value=55, 
                                 your_application_value = 85
                                )
)

slider_age=dcc.RangeSlider(id='slider_age',
                    min=18,
                    max=70,
                    marks={i: '{} years'.format(i) for i in range(18, 70) if i%10==0},
                    value=[18,70])

slider_revenu=dcc.RangeSlider(id='slider_revenu',
                    min=0,
                    max=1000000,
                    marks={i: '{} k$'.format(int(i/1000)) for i in range(0, 1000000,100000)
                            },
                    value=[1,8])

upload_files = dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    )


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
    html.Hr(), 
    upload_files,

    html.Div(id='output-data-upload'),
    ],
    style={'columnCount': 3,
    "background-color":'white',
    "height": "100vh"})




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


######################   uploading file  
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
#########################################





if __name__ == '__main__':
    app.run_server(debug=True)
   
