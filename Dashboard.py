
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from joblib import load
import pandas as pd
from components.functions import results_assessment, graph_age_income

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cachedir = cachedir = 'Data/'
VERSION_NAME="28may21_sampled_1000"

train = load(cachedir+"train_final_df"+VERSION_NAME)
y_train = load(cachedir+"train_label"+VERSION_NAME)
test = load(cachedir+"test_final_df"+VERSION_NAME)
y_test = load(cachedir+"test_label"+VERSION_NAME)

#train = pd.read_csv("Data/train20may21.csv")
#y_train = pd.read_csv("Data/y_train20may21.csv")
#test = pd.read_csv("Data/test20may21.csv")
# #y_test = pd.read_csv("Data/y_test20may21.csv")

#train = train.set_index("SK_ID_CURR")=
#y_train = y_train.set_index("SK_ID_CURR")
#test = test.set_index("SK_ID_CURR")
#y_test = y_test.set_index("SK_ID_CURR")





train_histogram = pd.concat([train,y_train],axis=1)[['age','AMT_CREDIT','AMT_INCOME_TOTAL','TARGET','NEW_EXT_SOURCES_PROD']]

################# INTERACTIONS #########################
slider_age=dcc.RangeSlider(
    id='slider_age',
    min=18,
    max=70,
    marks={i: '{} years'.format(i) for i in range(18, 70) if i%10==0},
    value=[18,70]
    )

slider_revenu=dcc.RangeSlider(id='slider_revenu',
                    min=0,
                    max=100,
                    marks={i: '{} k$'.format(int(i*10)) for i in range(0, 100) if i%10==0
                            },
                    value=[0,100])


Loans_selection = dcc.Dropdown(id='loans_selection',
    options=[{'label': SK_ID, 'value': SK_ID} for SK_ID in y_test.index],
    value=[],
    searchable=True,
    multi=False,
    optionHeight=30
)  

################# FIGURES ############################
Histogram = dcc.Graph(
        id='histo_graph',
        figure=graph_age_income(df=train_histogram,
                    loan_test_value=0,
                    feature_figure_1 = 'NEW_EXT_SOURCES_PROD',
                    min_revenu_value = 0,
                    max_revenu_value = 1000000,
                    min_age_value = 0,
                    max_age_value = 99
                    )
)

result_assessment = dcc.Graph(
    id='result_assessment',
    figure=results_assessment(min_value=55, 
                            your_application_value = 85
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
                
        style={'width': '48%', 'display': 'inline-block','float': 'right'}
                ),
        html.Div([
            html.Label('Selection of the loans'),
            Loans_selection,
            html.Div([
                html.Div([
                    html.Label('New income for loan applicant'),
                    dcc.Input(
                    id="income_input", type="number", placeholder="New income (k$)",
                    min=10, max=10e5
                    )],
                    style={'width': '48%', 'display': 'inline-block'}),
                html.Div([
                    html.Label('New value for days employed'),
                    dcc.Input(
                    id="days_employed_input", type="number", placeholder="Days employed (days)",
                    min=0, max=40*365
                    )],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]
            ),
        ],style={'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'}),
                
    ],style={'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'}),

    html.Div([
            html.Div([result_assessment],style={'width': '20%'}),
            html.Div([Histogram],style={'width': '70%'}),
            ],
            style={'display': 'inline-block',"background-color":'white'}),
])



################### Update Income graph
@app.callback(
    dash.dependencies.Output('histo_graph', 'figure'),
    [dash.dependencies.Input('slider_revenu', 'value'),
     dash.dependencies.Input('slider_age', 'value'),
    dash.dependencies.Input('loans_selection', 'value')])

def update_graph(revenu_value, age_value,loans_id):

    fig = graph_age_income(df=train_histogram,
                    loan_test_value = test.loc[loans_id,'NEW_EXT_SOURCES_PROD'],
                    feature_figure_1 = 'NEW_EXT_SOURCES_PROD',
                    min_revenu_value = revenu_value[0]*10000,
                    max_revenu_value = revenu_value[1]*10000,
                    min_age_value = age_value[0],
                    max_age_value = age_value[1]
                    )

    fig.update_layout(title='NEW_EXT_SOURCES_PROD (Revenu : ' + str(revenu_value[0]*10) + " - " + str(revenu_value[1]*10) + "k$ / age :" + str(age_value[0]) + " - " + str(age_value[1]) +")")
    return fig
#########################################

################### Update Result Assesment
@app.callback(
    dash.dependencies.Output('result_assessment', 'figure'),
    dash.dependencies.Input('loans_selection', 'value'))

def update_graph(loans_id):

    fig = results_assessment(min_value=55, 
                            your_application_value = y_test.loc[loans_id,'TARGET']*100
                            )
    return fig
#########################################


if __name__ == '__main__':
        app.run_server(debug=True)
   
