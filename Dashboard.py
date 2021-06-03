
# For Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#from specific functions
from components.functions import results_assessment, graph_histogram

# For graph
import plotly.express as px
import shap

#for model
from joblib import load
import xgboost
import pandas as pd




external_stylesheets = ['bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cachedir = 'Data/'
VERSION_NAME="3juin21_v4_sampled_2500"


train = pd.read_csv(cachedir+"train_final_df"+VERSION_NAME+".csv",sep=",")
y_train = pd.read_csv(cachedir+"train_label"+VERSION_NAME+".csv",sep=",")
test = pd.read_csv(cachedir+"test_final_df"+VERSION_NAME+".csv",sep=",")
y_test = pd.read_csv(cachedir+"test_label"+VERSION_NAME+".csv",sep=",")

train = train.set_index("SK_ID_CURR")
y_train = y_train.set_index("SK_ID_CURR")
test = test.set_index("SK_ID_CURR")
y_test = y_test.set_index("SK_ID_CURR")

model = load(cachedir+"modelxgboost3"+VERSION_NAME)

loan_selected_index = test.iloc[0,:].name
test.loc["New_loan",:] = test.loc[loan_selected_index,:]
 

list_features_selection = ['age','AMT_CREDIT','NEW_CREDIT_TO_ANNUITY_RATIO',
                            'NEW_EXT_SOURCES_PROD','NEW_EXT_SOURCES_MEAN',
                            'MONTH(DAYS_LAST_PHONE_CHANGE_timedelta)',
                            'AMT_ANNUITY','NEW_EMPLOY_TO_BIRTH_RATIO']

train_histogram = pd.concat([train,y_train],axis=1)[['TARGET','AMT_INCOME_TOTAL']+list_features_selection]

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

ratio_value_input = dcc.Input(
                    id="ratio_input", 
                    type="number", 
                    placeholder="New credit to annuity ratio",
                    min=0,
                    value=round(test.loc[loan_selected_index,'NEW_CREDIT_TO_ANNUITY_RATIO'],2)
                    )

NEW_EXT_SOURCES_MEAN_value_input =dcc.Input(
                    id="NEW_EXT_SOURCES_MEAN_input", type="number", placeholder="NEW_EXT_SOURCES_MEAN",
                    min=0, 
                    max=1 ,
                    value=round(test.loc[loan_selected_index,'NEW_EXT_SOURCES_MEAN'],3)
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
    html.Header([
        html.Div([
                html.Label('Select age range'),
                slider_age,
                html.Hr(className="light"),

                html.Label('Select revenu range'),
                slider_revenu
                ],                
        style={
            'width': '48%', 
            'display': 'inline-block',
            'margin-top': '1.5rem',
            'margin-bottom': '1.5rem'
            }
                ),
        html.Div([
            html.Label('Selection of the loans'),
            Loans_selection,
            html.Hr(className="light"),

            html.Label('Selection of the feature'),
            Features_histogram_selection,
            html.Hr(className="light"),
            
            html.Div([              
                html.Label('New credit to annuity ratio'),
                html.Br(),
                ratio_value_input
                ],
                style={
                    'width': '50%', 
                    'display': 'inline-block',
                    'float': 'right'
                    }
                ),
            html.Div([        
                html.Label('New value EXT Sources mean'),
                html.Br(),
                NEW_EXT_SOURCES_MEAN_value_input
                ],
                style={'width': '30%', 'display': 'inline-block'}
                )],                
            style={
                'width': '48%', 
                'display': 'inline-block',
                'float': 'right'
                }
            )
            ],
        style={
            'marginBottom': 5, 
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px'
                }
            ),

    html.Div([
            html.Div([result_assessment],style={'width': '39%','display': 'inline-block'}),
            html.Div([Histogram],style={'width': '60%','display': 'inline-block','float': 'right'}),
            ],
            style={'display': 'inline-block',"background-color":'white'}),
            ])



################### Update ratio graph
@app.callback(
    dash.dependencies.Output('histo_graph', 'figure'),
    [dash.dependencies.Input('slider_revenu', 'value'),
     dash.dependencies.Input('slider_age', 'value'),
    dash.dependencies.Input('loans_selection', 'value'),
    dash.dependencies.Input('features_histogram_selection','value'),
    dash.dependencies.Input('ratio_input', 'value'),
    dash.dependencies.Input('NEW_EXT_SOURCES_MEAN_input', 'value')])

def update_graph(revenu_value, age_value,loans_id,feature_selected,new_ratio_value,new_NEW_EXT_SOURCES_MEAN):

    fig = graph_histogram(df=train_histogram,
                    loan_test_value = test.loc[loans_id,feature_selected],
                    feature_figure_1 = feature_selected,
                    min_revenu_value = revenu_value[0]*10000,
                    max_revenu_value = revenu_value[1]*10000,
                    min_age_value = age_value[0],
                    max_age_value = age_value[1]
                    )
    
    
    if feature_selected=='NEW_CREDIT_TO_ANNUITY_RATIO':
        fig.add_shape(type="line", yref="paper",
            x0=new_ratio_value, 
            y0=0, 
            x1=new_ratio_value, 
            y1=0.70,
            line=dict(color="green",
                    dash="dash",
                    width=3),
                    name="New credit to annuity ratio"
        )

    if feature_selected=='NEW_CREDIT_TO_ANNUITY_RATIO':
        fig.add_shape(type="line", yref="paper",
            x0=new_ratio_value, 
            y0=0, 
            x1=new_ratio_value, 
            y1=0.70,
            line=dict(color="green",
                    dash="dash",
                    width=3),
                    name="New credit to annuity ratio"
        )
        

    elif feature_selected=='NEW_EXT_SOURCES_MEAN':
        fig.add_shape(type="line", yref="paper",
            x0=new_NEW_EXT_SOURCES_MEAN, 
            y0=0, 
            x1=new_NEW_EXT_SOURCES_MEAN, 
            y1=0.70,
            line=dict(color="green",
                    dash="dash",
                    width=3),
                    name="New value for EXT_SOURCES_MEAN"
        )                    

    fig.update_layout(title=feature_selected +'(Revenu : ' + str(revenu_value[0]*10) + " - " + str(revenu_value[1]*10) + "k$ / age :" + str(age_value[0]) + " - " + str(age_value[1]) +")")
    
    
    return fig
#########################################

################### Update ratio Value
@app.callback(
    dash.dependencies.Output('ratio_input', 'value'),
    dash.dependencies.Input('loans_selection', 'value'))

def update_ratio_value(loan_id):

    new_ratio = round(test.loc[loan_id,'NEW_CREDIT_TO_ANNUITY_RATIO'],3)
    return new_ratio
#########################################

################### Update EXT_SOURCES_MEAN
@app.callback(
    dash.dependencies.Output('NEW_EXT_SOURCES_MEAN_input', 'value'),
    dash.dependencies.Input('loans_selection', 'value'))

def update_ratio_value(loan_id):

    new_NEW_EXT_SOURCES_MEAN = round(test.loc[loan_id,'NEW_EXT_SOURCES_MEAN'],3)
    return new_NEW_EXT_SOURCES_MEAN
#########################################


################### Update Result Assesment
@app.callback(
    dash.dependencies.Output('result_assessment', 'figure'),
    [dash.dependencies.Input('loans_selection', 'value'),
    dash.dependencies.Input('ratio_input', 'value'),
    dash.dependencies.Input('NEW_EXT_SOURCES_MEAN_input', 'value')])

def update_graph(loans_id,new_ratio_value,new_NEW_EXT_SOURCES_MEAN):

    test.loc["New_loan",:] = test.loc[loans_id,:]
    test.loc["New_loan",'NEW_CREDIT_TO_ANNUITY_RATIO']=new_ratio_value
    test.loc["New_loan",'NEW_EXT_SOURCES_MEAN']=new_NEW_EXT_SOURCES_MEAN
    result_assessment_model_updated = round(model.predict_proba(test.loc[[loans_id,"New_loan"],:])[1,0]*100,0)

    fig = results_assessment(min_value=55, 
                            your_application_value = result_assessment_model_updated
                            )
                      
    fig.update_layout(title='Your application results : ' + str(result_assessment_model_updated) + "%")

   
    return fig



#########################################


dash.dependencies.Input('loans_selection', 'value')
if __name__ == '__main__':
    app.run_server(debug=True)
