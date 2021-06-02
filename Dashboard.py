
# For Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#from specific functions
from components.functions import results_assessment, graph_histogram

# For graph
import plotly.express as px

#for model
from joblib import load
import xgboost
import pandas as pd
import numpy as np



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cachedir = 'Data/'
VERSION_NAME="31may21_sampled_2000"


train = pd.read_csv(cachedir+"train_final_df"+VERSION_NAME+".csv",sep=",")
y_train = pd.read_csv(cachedir+"train_label"+VERSION_NAME+".csv",sep=",")
test = pd.read_csv(cachedir+"test_final_df"+VERSION_NAME+".csv",sep=",")
y_test = pd.read_csv(cachedir+"test_label"+VERSION_NAME+".csv",sep=",")

train = train.set_index("SK_ID_CURR")
y_train = y_train.set_index("SK_ID_CURR")
test = test.set_index("SK_ID_CURR")
y_test = y_test.set_index("SK_ID_CURR")

model = load(cachedir+"modelxgboost1"+VERSION_NAME)

loan_selected_index = test.iloc[0,:].name
test.loc["New_loan",:] = test.loc[loan_selected_index,:]
 

list_features_selection = ['NEW_EXT_SOURCES_PROD','MONTH(DAYS_EMPLOYED_timedelta)',
                            'MONTH(DAYS_LAST_PHONE_CHANGE_timedelta)','NEW_CREDIT_TO_GOODS_RATIO',
                            'AMT_ANNUITY','NEW_EMPLOY_TO_BIRTH_RATIO',
                            'FLAG_EMP_PHONE','FLAG_WORK_PHONE',
                            'FLAG_CONT_MOBILE','FLAG_PHONE']

train_histogram = pd.concat([train,y_train],axis=1)[['age','AMT_CREDIT','AMT_INCOME_TOTAL','TARGET',]+list_features_selection]

result_assessment_model = model.predict_proba(test.loc[[loan_selected_index,"New_loan",],])

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
    value=loan_selected_index,
    searchable=True,
    multi=False,
    optionHeight=30
)

Features_histogram_selection = dcc.Dropdown(id='features_histogram_selection',
    options=[{'label': feat, 'value': feat} for feat in list_features_selection],
    value='NEW_EXT_SOURCES_PROD',
    searchable=True,
    multi=False,
    optionHeight=30
)

################# FIGURES ############################
Histogram = dcc.Graph(
        id='histo_graph',
        figure=graph_histogram(df=train_histogram,
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
                            your_application_value = round(result_assessment_model[1,0],2)*100
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
                
        style={'width': '48%', 'display': 'inline-block'}
                ),
        html.Div([
            html.Label('Selection of the loans'),
            Loans_selection,
            html.Label('Selection of the feature'),
            Features_histogram_selection,
            html.Div([
                html.Div([
                    html.Label('New income for loan applicant'),
                    dcc.Input(
                    id="income_input", 
                    type="number", 
                    placeholder="New income (k$)",
                    min=10, 
                    max=10e5,
                    value=test.loc[loan_selected_index,'AMT_INCOME_TOTAL']
                    )],
                    style={'width': '48%', 'display': 'inline-block','float': 'right'}),
                html.Div([
                    html.Label('New value for days employed'),
                    dcc.Input(
                    id="days_employed_input", type="number", placeholder="Days employed (years)",
                    min=-20, max=40,
                    value=test.loc[loan_selected_index,'MONTH(DAYS_EMPLOYED_timedelta)']
                    )])
            ]
            ),
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
                
    ],style={'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'}),

    html.Div([
            html.Div([result_assessment],style={'width': '15%','display': 'inline-block'}),
            html.Div([Histogram],style={'width': '79%','display': 'inline-block','float': 'right'}),
            ],
            style={'display': 'inline-block',"background-color":'white'}),
])



################### Update Income graph
@app.callback(
    dash.dependencies.Output('histo_graph', 'figure'),
    [dash.dependencies.Input('slider_revenu', 'value'),
     dash.dependencies.Input('slider_age', 'value'),
    dash.dependencies.Input('loans_selection', 'value'),
    dash.dependencies.Input('features_histogram_selection','value')])

def update_graph(revenu_value, age_value,loans_id,feature_selected):

    fig = graph_histogram(df=train_histogram,
                    loan_test_value = test.loc[loans_id,feature_selected],
                    feature_figure_1 = feature_selected,
                    min_revenu_value = revenu_value[0]*10000,
                    max_revenu_value = revenu_value[1]*10000,
                    min_age_value = age_value[0],
                    max_age_value = age_value[1]
                    )

    fig.update_layout(title=feature_selected +'(Revenu : ' + str(revenu_value[0]*10) + " - " + str(revenu_value[1]*10) + "k$ / age :" + str(age_value[0]) + " - " + str(age_value[1]) +")")
    return fig
#########################################

################### Update Income Value
@app.callback(
    dash.dependencies.Output('income_input', 'value'),
    dash.dependencies.Input('loans_selection', 'value'))

def update_income_value(loan_id):

    new_income = test.loc[loan_id,'AMT_INCOME_TOTAL']
    return new_income
#########################################

################### Update Days employed
@app.callback(
    dash.dependencies.Output('days_employed_input', 'value'),
    dash.dependencies.Input('loans_selection', 'value'))

def update_income_value(loan_id):

    new_days_employed = test.loc[loan_id,'MONTH(DAYS_EMPLOYED_timedelta)']
    return new_days_employed
#########################################


################### Update Result Assesment
@app.callback(
    dash.dependencies.Output('result_assessment', 'figure'),
    dash.dependencies.Input('loans_selection', 'value'))

def update_graph(loans_id):

    test.loc["New_loan",:] = test.loc[loans_id,:]
 
    result_assessment_model_updated = np.round(model.predict_proba(test.loc[[loans_id,"New_loan",],]),2)

    fig = results_assessment(min_value=55, 
                            your_application_value = np.round(result_assessment_model_updated[1,0],2)*100
                            )
    fig.update_layout(title='Your application results : ' + str(result_assessment_model_updated[1,0]*100))                        
    return fig
#########################################


dash.dependencies.Input('loans_selection', 'value')
if __name__ == '__main__':
    app.run_server(debug=True)
