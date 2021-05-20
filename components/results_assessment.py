import plotly.graph_objects as go
import pandas as pd

#Result figure


def results_assessment(min_value=55,your_application_value = 85):

  label_min_value = str(min_value)+"%"
  label_your_application_value = str(your_application_value)+"%"

  if min_value < your_application_value: 

      values = [0,
                min_value,
                your_application_value-min_value,
                100 - your_application_value
                ]

      labels = ["Passed",
                label_min_value,
                label_your_application_value,
                "  "               
                ]

      color_label = ['green',
                     'black',
                     'black',
                     'black',
                    ]

      colors_pie = ['white',
                'darkgreen',
                'lightgreen',
                'whitesmoke'
                ]

      colors_line = ['black',
                'black',
                'black',
                'black'
                ]

      parents=["", 
               "Passed", 
               "Passed", 
               "Passed"]

      text = ["Results",            
              'Minimum result to accept the loan',
              'Your result',
              '']

      rotation = 90   #90-(100 - your_application_value)*360/100


  elif min_value > your_application_value: 
      #values = [100-min_value, min_value-your_application_value,your_application_value]
      #colors = ['darkorange',"bisque",'white']
      #labels = [str(your_application_value)+"%",str(min_value)+"%",'']
      #text = ['Your result','Minimum result to accept the loan','']
      #annotations = [dict(text='Minimum', x=0.6, y=-0.05, font_size=20, font_color="bisque", showarrow=False)]
      #rotation = -your_application_value/100*360

      values = [0,
                your_application_value,
                min_value-your_application_value,
                100 - min_value
                ]

      labels = ["Failled",             
                label_your_application_value,
                label_min_value,
                "  "               
                ]
      color_label = ['red',
                     'black',
                     'black',
                     'black',
                    ]

      colors_pie = ['white',
                'darkorange',
                "bisque",
                'whitesmoke'
                ]

      colors_line = ['black',
                'black',
                'black',
                'black'
                ]

      parents=["", 
               "Failled", 
               "Failled", 
               "Failled"]

      text = ["Results",
              'Your result',            
              'Minimum result to accept the loan',
              '']

      rotation = 90  

      # Use `hole` to create a donut-like pie char
  fig = go.Figure(go.Sunburst(
                  labels=labels,
                  parents=parents,
                  values=values,
                  ))

  fig.update_traces(name="Pie chart result",
                    rotation = rotation,
                    hoverinfo="text",
                    text=text,
                    textinfo='label',
                    insidetextorientation='horizontal',
                    sort=False,
                    textfont_size=20,
                    marker=dict(colors=colors_pie, line=dict(color=colors_line, width=2)),
                    textfont=dict(size=[50,20,20,20],color=color_label),
                    opacity=0.7
                   )

  fig.update_layout(title_text="Your application result",
                    title_xref='paper',
                    width=400,
                    height=400)
  return fig
