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

# Create a dash application
app = dash.Dash(__name__)

launch_sites = spacex_df['Launch Site'].unique()
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=options,
                                    value='ALL',  # Default value
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: str(i) for i in range(0, 10001, 1000)},  # Labels for each step
                                    value=[min_payload, max_payload]  # Initial range

                                ),
                                

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Callback function for updating the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If 'ALL' is selected, use the whole dataframe
    if entered_site == 'ALL':
        # Calculate success and failure counts across all sites
        success_counts = spacex_df['class'].value_counts()
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title='Total Success vs. Failure for All Sites',
            labels={'class': 'Launch Success'},
            color_discrete_map={0: 'red', 1: 'green'}
        )
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts()
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title=f'Success vs. Failure for {entered_site}',
            labels={'class': 'Launch Success'},
            color_discrete_map={0: 'red', 1: 'green'}
        )
    
    return fig


# Callback function for updating the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    min_payload, max_payload = payload_range
    
    # Filter dataframe based on the selected site and payload range
    if selected_site == 'ALL':
        df_filtered = spacex_df
    else:
        df_filtered = spacex_df[spacex_df['Launch Site'] == selected_site]
    
    df_filtered = df_filtered[(df_filtered['Payload Mass (kg)'] >= min_payload) &
                              (df_filtered['Payload Mass (kg)'] <= max_payload)]
    
    # Create scatter plot
    fig = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # Color by Booster Version
        title=f'Payload vs. Launch Success for {selected_site if selected_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Success', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8059)
