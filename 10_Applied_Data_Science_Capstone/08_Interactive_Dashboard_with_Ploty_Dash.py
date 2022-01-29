# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Establish the steps
min_range=0
max_range=10000
step_range=1000
marks_range={w:'{} Kg'.format(w) for w in range(min_range,max_range+1,step_range)}

# List of launch sites
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}]
for ls in spacex_df['Launch Site'].unique().tolist(): 
    launch_sites.append({'label': ls, 'value': ls})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=launch_sites, placeholder="Select a Launch Site here", value="ALL", searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_range, 
                                    max=max_range, 
                                    step=step_range,
                                    marks=marks_range,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data = spacex_df[spacex_df['class']==1]
        fig = px.pie(data,
                    names='Launch Site',
                    title='Total Success Launches by Site'
            )
        fig.update_traces(textinfo='label+percent', textposition='auto', textfont_size=10, marker=dict(line=dict(color='#000000', width=2)))
        return fig
    else:
        data = spacex_df[spacex_df['Launch Site']==entered_site].sort_values(by="class", ascending="false")
        data = data['class'].apply(lambda x: "Success" if x==1 else "Failed")
        fig = px.pie(data, 
                    names='class', 
                    title='Total Success Launches for site {}'.format(entered_site),
                    labels={'class':'Outcome'},
                    color='class',
                    color_discrete_map={'Success':'blue','Failed':'red'},
            )
        fig.update_traces(textinfo='label+percent', textposition='auto', textfont_size=10, marker=dict(line=dict(color='#000000', width=2)))
        return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
     Output(component_id='success-payload-scatter-chart',component_property='figure'),
     [Input(component_id='site-dropdown',component_property='value'),Input(component_id="payload-slider", component_property="value")]
)
def update_scattergraph(site_dropdown,payload_slider):
    low, high = payload_slider
    if site_dropdown == 'ALL':
        data=spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)].sort_values(by="class", ascending="false")
        data['class'] = data['class'].apply(lambda x: "Success" if x==1 else "Failed")
        fig = px.scatter(
                        data, x="Payload Mass (kg)", y="class",
                        title="Correlation between Payload and Success for all Sites",
                        color="Booster Version",
                        size='Payload Mass (kg)',
                        labels={'class':'Outcome'},
                        hover_data=['Payload Mass (kg)']
            )
        return fig
    else:
        data=spacex_df.loc[spacex_df['Launch Site'] == site_dropdown]
        data=data[data['Payload Mass (kg)'].between(low, high)].sort_values(by="class", ascending="false")
        data['class'] = data['class'].apply(lambda x: "Success" if x==1 else "Failed")
        fig = px.scatter(
                        data, x="Payload Mass (kg)", y="class",
                        title='Correlation between Payload and Success for {} site'.format(site_dropdown),
                        color="Booster Version",
                        size='Payload Mass (kg)',
                        hover_data=['Payload Mass (kg)'],
                        labels={'class':'Outcome'}
            )
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
