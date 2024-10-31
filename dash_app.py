import dash
from dash import dcc, html, callback, ctx
from dash.dependencies import Input, Output
from dash import dash_table
import plotly.express as px
import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
import osmnx as ox
import plotly.graph_objects as go

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/michelin_by_Jerry_Ng.csv')

def get_points_within_states(states_gdf, points_df, lat_col='Latitude', lon_col='Longitude'):

    paths = {'FRA': 'geojsons/gadm41_FRA_1.json', 'ITA': 'geojsons/gadm41_ITA_1.json', 'GER': 'geojsons/gadm41_DEU_1.json', 'BEL': 'geojsons/gadm41_BEL_1.json','SWI':'geojsons/gadm41_CHE_1.json','GBR': 'geojsons/gadm41_GBR_1.json','NLD':'geojsons/gadm41_NLD_1.json','USA':'geojsons/gadm41_USA_1.json'}
    states_gdf = gpd.read_file(paths[states_gdf])
    # Convert the DataFrame to a GeoDataFrame with Point geometries
    geometry = [Point(xy) for xy in zip(points_df[lon_col], points_df[lat_col])]
    points_gdf = gpd.GeoDataFrame(points_df, geometry=geometry, crs="EPSG:4326")

    # Ensure both GeoDataFrames are in the same CRS
    points_gdf = points_gdf.to_crs(states_gdf.crs)

    # Perform a spatial join to find points within the state geometries
    matched_points = gpd.sjoin(points_gdf, states_gdf, how='inner', predicate='within')

    # Return the result without the geometry column
    return matched_points.drop(columns='geometry'), states_gdf

countries = {
    'France': 'FRA',
    'Germany': 'GER',
    'Italy': 'ITA',
    'Belgium': 'BEL',
    'Switzerland': 'SWI'
    ,'Great Britain': 'GBR'
    ,'Netherlands': 'NLD'
    ,'United States of America': 'USA'
}

cities = {
    'Paris, France': 'paris',
    'London, United Kingdom': 'london',
    'New York, USA': 'newyork'
}

# unique cuisines
unique_cuisines = set()
for idx, row in df.iterrows():
    if not isinstance(row['Cuisine'], float):
        unique_cuisines.update(row['Cuisine'].split(','))
unique_cuisines = [x.strip() for x in unique_cuisines]
unique_cuisines = list(set(unique_cuisines))
unique_cuisines.sort()

# Initialize the Dash app
app = dash.Dash(__name__)

div_style = {
    'border': '2px solid #333',
    'padding': '15px',
    'margin': '20px auto',
    'borderRadius': '8px',
    'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
    'backgroundColor': '#ffffff',
    'maxWidth': '800px',
    'width': '90%',
}

input_div_style = {
    'margin-bottom': '10px',
    'padding': '15px',
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.1)',
    'background-color': '#f9f9f9',
    'font-family': 'Sans-serif',
}

inline_input_div_style = {
    'display': 'flex',
    'margin-bottom': '10px',
    'padding': '15px',
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.1)',
    'background-color': '#f9f9f9',
    'font-family': 'Sans-serif'
}

# Style for the container div
container_style = {
    'display': 'flex',
    'flex-direction': 'row',
    'justify-content': 'space-between',
    'width': '100%',
    'height': '100%'
}

# Style for the input section
input_section_style = {
    'flex': '1',
    'display': 'flex',
    'flex-direction': 'column',
    'padding': '10px',
    'border': '2px solid #333',
    'margin': '20px auto',
    'height': '100%'
}

graph_style = {
    'flex': '3',
    'display': 'flex',
    'justify-content': 'center',
    'align-items': 'center',
    'padding': '10px',
    'border': '2px solid #333',
    'box-sizing': 'border-box',
    'width': '100%',
    'height': '100%',
    'overflow': 'hidden'
}

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='General Analysis', children=[
            html.Div(children=[
    html.H1('Michelin Restaurants around the world', style={'text-align':'center'}),
    html.Div([
        html.Div([
            html.Div([
                html.P('Select star rating'),
                dcc.Checklist(options=['3 Stars', '2 Stars', '1 Star', 'Bib Gourmand', 'Selected Restaurants'], id='star-selection', inline=True),
            ], style=input_div_style),
            html.Div([
                html.P('Select cuisine type'),
                dcc.Dropdown(options=unique_cuisines, id='cuisine-selection', multi=True)
                ], style=input_div_style),
            html.Div([
                html.P('Focus on a country'),
                dcc.Dropdown(options=[{'label': k, 'value':v} for k, v in countries.items()], id='country-selection')
                ], style=input_div_style
            ),
            html.Div([
                html.P('Restaurants available:'),
                html.P('',id='number-of-restaurants')
            ], style=inline_input_div_style
            ),
            html.Div([
                html.Div(id='restaurant-details'),
            ], style=input_div_style)
        ], style=input_section_style),
        html.Div([
            dcc.Graph(
                figure={},
                id='map'
            )
        ],
        style=graph_style)
    ], style=container_style)
])
        ]),
        dcc.Tab(label='City Analysis', children=[
            html.H1('Plan a trip around the city', style={'text-align':'center'}),
            html.Div([
            html.Div([
                html.Div([
                    html.P('Select a city'),
                    dcc.Dropdown(
                    id='city-dropdown',
                    options=[{'label': city, 'value': city} for city in cities.keys()],
                    value='Paris, France',  # Default value
                )],style=input_div_style),
                html.Br(),
                html.P('Nearest points of tourism'),
                dash_table.DataTable(data=[], columns=[] ,id='map-selection', style_cell_conditional=[
                {'if': {'column_id': 'name'},
                'width': '30%'},
                {'if': {'column_id': 'tourism'},
                'width': '30%'}
                ],
                style_cell={'text-align':'center', 'font-family': 'Sans-serif'})
            ],style=input_section_style),
            html.Div([
                dcc.Graph(id='city-map'),
            ], style=graph_style)
            ], style=container_style)
        ])
    ])
])

@callback(
    Output(component_id='map', component_property='figure'),
    Output(component_id='number-of-restaurants', component_property='children'),
    Input(component_id='star-selection', component_property='value'),
    Input(component_id='cuisine-selection', component_property='value'),
    Input(component_id='country-selection', component_property='value')
)
def update_graph(star, cuisine, country):
    if country == None or country == []:
        if (star is None or star == []) and (cuisine is None or cuisine == []):
            fig = px.scatter_map(df, 'Latitude', 'Longitude', text='Name', color='Award', map_style='open-street-map', zoom=4, width=1100, height=800, hover_data = ['Name'])
            num = df.shape[0]
        else:        
            if star and not cuisine:
                filtered_df = df[df['Award'].isin(star)]
            elif not star and cuisine:
                filtered_df = df[df['Cuisine'].str.contains('|'.join(cuisine),na=False)]
            elif star and cuisine:
                filtered_df = df[(df['Award'].isin(star))&(df['Cuisine'].str.contains('|'.join(cuisine),na=False))]
            num = filtered_df.shape[0]
            fig = px.scatter_map(filtered_df, 'Latitude', 'Longitude', text='Name', color='Award', map_style='open-street-map', zoom=4, width=1100, height=800, hover_data = ['Name'])
        if str(num) != '0':
            return fig, str(num)
        else:
            return px.scatter_map(df, 'Latitude', 'Longitude', text='Name', color='Award', map_style='open-street-map', zoom=4, width=1100, height=800, hover_data = ['Name']), str(num) + '. Choose a different country, cuisine or Rating'
    else:
        country_df, country_gdf = get_points_within_states(country, df)
        if (star is None or star == []) and (cuisine is None or cuisine == []):
            fig = px.scatter_map(country_df, 'Latitude', 'Longitude', text='Name', color='Award', map_style='open-street-map', zoom=4, hover_name='NAME_1', width=1100, height=800, hover_data = ['Name'])
            num = country_df.shape[0]
        else:        
            if star and not cuisine:
                filtered_df = country_df[country_df['Award'].isin(star)]
            elif not star and cuisine:
                filtered_df = country_df[country_df['Cuisine'].str.contains('|'.join(cuisine),na=False)]
            elif star and cuisine:
                filtered_df = country_df[(country_df['Award'].isin(star))&(country_df['Cuisine'].str.contains('|'.join(cuisine),na=False))]
            num = filtered_df.shape[0]
            fig = px.scatter_map(filtered_df, 'Latitude', 'Longitude', text='Name', color='Award', map_style='open-street-map', zoom=4, width=1100, height=800, hover_data = ['Name'])
        fig.update_layout(
            map={
                "style": "open-street-map",
                "zoom": 5,
                "layers": [
                    {
                        "source": json.loads(country_gdf.geometry.to_json()),
                        "below": "traces",
                        "type": "line",
                        "color": "black",
                        "line": {"width": 1},
                    }
                ],
            },
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
        )
        if str(num) != '0':
            return fig, str(num)
        else:
            return px.scatter_map(df, 'Latitude', 'Longitude', text='Name', color='Award', map_style='open-street-map', zoom=4, width=1100, height=800), str(num) + '. Choose a different country, cuisine or Rating'

@callback(
    Output(component_id='restaurant-details', component_property='children'),
    Input(component_id='map', component_property='clickData'),
)
def get_details(click):
    if not click:
        return None
    else:
        restaurant_name = click['points'][0]['text']
        data = df[df['Name']==restaurant_name].iloc[0]
        restaurant_details = html.Div([html.P(data['Name'], style={'text-align':'center'}), html.P(data['Description']), html.P('Website: {}'.format(data['WebsiteUrl']))])
        return restaurant_details

# city callback
@app.callback(
    Output('city-map', 'figure'),
    Input('city-dropdown', 'value'),
)
def update_map(selected_city):
    if selected_city:
        city_mappings = {'Paris, France': 'cities/paris.gpkg', 'London, United Kingdom': 'cities/london.gpkg', 'New York, USA': 'cities/newyork.gpkg'}
        centers = {'Paris, France': {'lat': 48.85625, 'lon': 2.34375}, 'London, United Kingdom': {'lat': 51.5072 ,'lon': 0.1277}, 'New York, USA': {'lat':40.7128 , 'lon': -74.0060}}
        gdf = gpd.read_file(city_mappings[selected_city])
        gdf = gdf[gdf['tourism'] != 'nan']
        city_restaurants = df[df['Location']==selected_city][['Name', 'Latitude', 'Longitude']]
        city_restaurants['name'] = city_restaurants['Name']
        city_restaurants.drop('Name', axis=1, inplace=True)
        city_restaurants['geometry'] = city_restaurants.apply(lambda x: Point(x['Longitude'], x['Latitude']),axis=1)
        city_restaurants['tourism'] = 'restaurant'
        city_restaurants = city_restaurants[['name', 'geometry', 'tourism']]
        gdf = pd.concat([gdf, city_restaurants], ignore_index=True)
        gdf['size'] = gdf['tourism'].map({'restaurant':1, 'attraction':1, 'museum': 1, 'gallery': 1, 'artwork': 1})
        gdf = gdf[gdf['tourism']=='restaurant']
        fig = px.scatter_map(gdf, gdf['geometry'].y, gdf['geometry'].x, text='name', color='tourism', map_style='open-street-map', zoom=12, width=1100, height=800, opacity=0.8, size='size', center=centers[selected_city])
        return fig

@app.callback(
    Output(component_id='map-selection', component_property='data'),
    Output(component_id='map-selection', component_property='columns'),
    Output(component_id='city-map', component_property='figure', allow_duplicate=True),
    Input(component_id='city-map', component_property='clickData'),
    Input('city-dropdown', 'value'),
    Input('city-map', 'figure'),
    prevent_initial_call=True
)
def get_closest_tourist_places(location, selected_city, figure):
    if location and ctx.triggered_id == 'city-map':
        selected_location_latitude = location['points'][0]['lat']
        selected_location_longitude = location['points'][0]['lon']
        reference_point = Point(selected_location_longitude, selected_location_latitude)
        city_mappings = {'Paris, France': 'cities/paris.gpkg', 'London, United Kingdom': 'cities/london.gpkg', 'New York, USA': 'cities/newyork.gpkg'}
        gdf = gpd.read_file(city_mappings[selected_city])
        gdf = gdf[(gdf['tourism'] != 'nan')&(gdf['name'] != 'nan')]
        city_restaurants = df[df['Location']==selected_city][['Name', 'Latitude', 'Longitude']]
        city_restaurants['name'] = city_restaurants['Name']
        city_restaurants.drop('Name', axis=1, inplace=True)
        city_restaurants['geometry'] = city_restaurants.apply(lambda x: Point(x['Longitude'], x['Latitude']),axis=1)
        city_restaurants['tourism'] = 'restaurant'
        city_restaurants = city_restaurants[['name', 'geometry', 'tourism']]
        gdf = pd.concat([gdf, city_restaurants], ignore_index=True)
        gdf['size'] = gdf['tourism'].map({'restaurant':1, 'attraction':1, 'museum': 1, 'gallery': 1, 'artwork': 1})

        # Function to calculate distances
        gdf['distance'] = gdf.geometry.distance(reference_point)
        nearest_tourist_locations = gdf[gdf['tourism']!='restaurant'].nsmallest(10, 'distance')
        gdf = pd.concat([gdf[gdf['tourism']=='restaurant'], nearest_tourist_locations], ignore_index=True)
        figure = px.scatter_map(gdf, gdf['geometry'].y, gdf['geometry'].x, text='name', color='tourism', map_style='open-street-map', zoom=12, width=1100, height=800, opacity=0.8, size='size', center={'lon':selected_location_longitude, 'lat':selected_location_latitude})
        table_df = nearest_tourist_locations[['name', 'tourism']]
        return table_df.to_dict('records'), [{"name": i, "id": i} for i in table_df.columns], figure
    else:
        return None, None, figure

# # Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
