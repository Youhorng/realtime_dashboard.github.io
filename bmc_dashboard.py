# Import Libraries
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import folium

# Load Data
df = pd.read_csv("ndvi_ndwi_data_cleaned.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# Defining the latitude and longitude
latitude = 13.58111
longitude = 102.97959

# Polygons from the Request Builder
coordinates = [
  [13.477398, 102.365067],
  [13.477398, 102.683824],
  [13.391907, 102.697564],
  [13.35984, 103.412019],
  [13.883059, 103.434002],
  [14.016346, 103.326834],
  [13.952378, 103.208674],
  [14.117593, 103.20043],
  [14.221457, 103.052043],
  [13.661633, 102.540933],
  [13.613586, 102.620622],
  [13.554836, 102.340113],
  [13.477398, 102.365067]
]

# Create Folium map
my_map = folium.Map(location=[latitude, longitude], zoom_start=9)

# Create polygon
polygon = folium.Polygon(locations=coordinates, color="blue", fill=True, fill_color="blue", weight=2)

# Add polygon to map
polygon.add_to(my_map)

# Save the map to an HTML file
map_path = 'map.html'
my_map.save(map_path)

# Read the HTML file and embed it in an Iframe
with open(map_path, 'r') as f:
    map_html = f.read()

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='NDVI and NDWI Data Visualization', style={'textAlign': 'center'}),

    html.Div(
        html.Iframe(
            id='folium-map',
            srcDoc=map_html,
            width='100%',
            height='600'
        ),
        style={'textAlign': 'center'}
    ),

    html.Div(
        dcc.Dropdown(
            id='feature-selector',
            options=[
                {'label': 'NDVI Mean', 'value': 'ndvi_mean'},
                {'label': 'NDWI Mean', 'value': 'ndwi_mean'}
            ],
            value='ndvi_mean'
        ),
        style={'width': '50%', 'margin': 'auto'}
    ),

    html.Div(
        dcc.Graph(id='line-plot')
    ),

    html.Div(
        dcc.Graph(id='bar-plot')
    ),

    html.Div(
        dcc.Graph(id='box-plot')
    ),

    html.Div(
        dcc.Graph(id='box-plot-month')
    )
])

# Define the callback
@app.callback(
    [Output('line-plot', 'figure'),
     Output('bar-plot', 'figure'),
     Output('box-plot', 'figure'),
     Output('box-plot-month', 'figure')],
    [Input('feature-selector', 'value')]
)
def update_graphs(selected_feature):
    avg_month = df.groupby('year_month')[['ndvi_mean', 'ndwi_mean']].mean().reset_index()
    quarter = df.groupby(['year', 'quarter'])[[selected_feature]].mean().reset_index()

    # Line plot
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=avg_month['year_month'], y=avg_month['ndvi_mean'], mode='lines+markers', name='NDVI Mean', line=dict(color='Green')))
    line_fig.add_trace(go.Scatter(x=avg_month['year_month'], y=avg_month['ndwi_mean'], mode='lines+markers', name='NDWI Mean', line=dict(color='Blue')))
    line_fig.update_layout(title='NDVI and NDWI Mean Over Time')

    # Bar plot
    bar_fig = go.Figure()
    for quarter_value in quarter['quarter'].unique():
        quarter_data = quarter[quarter['quarter'] == quarter_value]
        bar_fig.add_trace(go.Bar(x=quarter_data['year'], y=quarter_data[selected_feature], name=f'Q{quarter_value}', marker_color=px.colors.qualitative.Set2[quarter_value-1]))
    bar_fig.update_layout(title=f'{selected_feature} Mean by Quarter')

    # Box plot with hue for quarters
    box_fig = go.Figure()
    for quarter_value in df['quarter'].unique():
        quarter_data = df[df['quarter'] == quarter_value]
        box_fig.add_trace(go.Box(x=quarter_data['year'], y=quarter_data['ndvi_mean'], name=f'Q{quarter_value}', marker_color=px.colors.qualitative.Set2[quarter_value-1]))
    box_fig.update_layout(title='NDVI Mean Distribution by Year and Quarter', boxmode='group')

    # Box plot by month
    box_month_fig = go.Figure()
    for month_value in df['month'].unique():
        month_data = df[df['month'] == month_value]
        box_month_fig.add_trace(go.Box(x=month_data['year'], y=month_data['ndvi_mean'], name=f'Month {month_value}', marker_color=px.colors.qualitative.Plotly[month_value % len(px.colors.qualitative.Plotly)]))
    box_month_fig.update_layout(title='NDVI Mean Distribution by Month', boxmode='group')

    return line_fig, bar_fig, box_fig, box_month_fig

if __name__ == '__main__':
    app.run_server(debug=True)