# #%%
# ''' Dash Analysis'''

##%%

import pandas as pd 
import matplotlib.pyplot as plt 

# df1_cleaned= pd.read_csv('/Users/gurukshagurnani/Desktop/updated_dataframe.csv',low_memory=False)
url='https://raw.githubusercontent.com/pradhyuman-yadav/dash-guruksha/main/updated_dataframe.csv'
df1_cleaned= pd.read_csv(url,low_memory=False)
df2 = df1_cleaned.copy()

df2['property_type'] = df2['property_type'].astype(str).fillna('Unknown')
clean_neighbourhoods = df2['neighbourhood_cleansed'].dropna().unique()
clean_neighbourhoods = [str(n) for n in clean_neighbourhoods]
max_avail = int(df2['availability_365'].max())

df2['latitude'] = pd.to_numeric(df2['latitude'], errors='coerce')
df2['longitude'] = pd.to_numeric(df2['longitude'], errors='coerce')

fontdict_label = {'font-family': 'serif', 'color': 'darkred', 'font-size': '16px'}
fontdict_title = {'font-family': 'serif', 'color': 'black', 'font-size': '20px'}

#%%
# # %%
# ''' Dash layout'''
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets= external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
my_app = dash.Dash('My app', external_stylesheets= external_stylesheets)
server = app.server

my_app.layout = html.Div([
    html.H1("London Airbnb Exploration", 
            style={
        'text-align': 'center',
        'font-family': 'serif',
        'color': 'black',
        'font-size': '50px'}),
    dcc.Tabs(id="main-tabs", children=[
        dcc.Tab(label='Tab 1: Neighbourhood Dropdown Menu', style= fontdict_title ,children=[
            html.Div([
                dcc.Dropdown(
                    id='neighbourhood-dropdown',
                    options=[{'label': n, 'value': n} for n in clean_neighbourhoods],
                    value=['City of London'],
                    multi=True,
                    placeholder='Select Neighbourhoods'
                ),
                dcc.Graph(id='map-graph'),
            ]),
        ]),
        dcc.Tab(label='Tab 2: Price Slider', style= fontdict_title, children=[
            html.Div([
                dcc.RangeSlider(
                    id='price-slider',
                    min=df2['price'].min(),
                    max=df2['price'].max(),
                    step=5,
                    marks={i: f'£{i}' for i in range(int(df2['price'].min()), int(df2['price'].max()), 100)},
                    value=[df2['price'].min(), df2['price'].max()]
                ),
                dcc.Graph(id='price-distribution-graph'),
            ]),
        ]),
        dcc.Tab(label='Tab 3: Property Type Radio', style= fontdict_title ,children=[
            html.Div([
                html.Label("Select Property Type:",style=fontdict_label),
                dcc.RadioItems(
                    id='property-type-radio',
                    options=[{'label': prop_type, 'value': prop_type} for prop_type in df2['property_type'].unique()[:15]],
                    value=df2['property_type'].unique()[0],
                    inline=True
                ),
                dcc.Graph(id='property-type-graph'),
            ]),
        ]),
        dcc.Tab(label='Tab 4: Overall App', style= fontdict_title, children=[
            html.Div([
                html.Label("Select Property Type:",style=fontdict_label),
                dcc.Dropdown(
                    id='property-type-dropdown',
                    options=[{'label': p_type, 'value': p_type} for p_type in df2['property_type'].unique()],
                    multi=True,
                    placeholder='Select Property Type',
                ),
                html.Label("Select Availability Window:",style=fontdict_label),
                dcc.Dropdown(
                    id='availability-type-dropdown',
                    options=[
                        {'label': 'Next 30 days', 'value': 'availability_30'},
                        {'label': 'Next 60 days', 'value': 'availability_60'},
                        {'label': 'Next 90 days', 'value': 'availability_90'},
                        {'label': 'Next 365 days', 'value': 'availability_365'}
                    ],
                    value='availability_365',  # Default to 365 days
                    clearable=False
                ),
                html.Label("Select Price Range:", style=fontdict_label),
                dcc.RangeSlider(
                    id='price-range-slider',
                    min=df2['price'].min(),
                    max=df2['price'].max(),
                    step=10,
                    marks={i: f'£{i}' for i in range(int(df2['price'].min()), int(df2['price'].max()), 100)},
                    value=[df2['price'].min(), df2['price'].max()],
                ),
                html.Label("Filter by Host Characteristics:",style=fontdict_label),
                dcc.Checklist(
                    id='host-characteristics-checklist',
                    options=[
                        {'label': 'Superhosts', 'value': 'superhost'},
                        {'label': 'Hosts with Profile Picture', 'value': 'profile_pic'},
                        {'label': 'Identity Verified Hosts', 'value': 'identity_verified'},
                    ],
                    value=[],  
                    labelStyle={'display': 'block'}
                ),
                dcc.Graph(id='neighborhood-property-stats-graph'),
            ]),
        ]),
    ])
])


#CALLBACK FOR neigbourhood dropdown
@my_app.callback(
    Output('map-graph', 'figure'),
    Input('neighbourhood-dropdown', 'value')
)
def update_map(selected_neighbourhoods):
    if selected_neighbourhoods is None:
        return dash.no_update
    filtered_df = df2[df2['neighbourhood_cleansed'].isin(selected_neighbourhoods)]
    fig = px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude', color='price',
                            size='number_of_reviews', hover_name='name', zoom=10,
                            mapbox_style='open-street-map')
    fig.update_layout(
        width=1000,  
        height=1000,  
        margin={"r":0,"t":0,"l":0,"b":0}  # Adjust margins to fit the layout
    )
    return fig


# call back for price range slider 
@my_app.callback(
    Output('price-distribution-graph', 'figure'),
    [Input('price-slider', 'value'), Input('neighbourhood-dropdown', 'value')]
)
def update_graph(selected_price_range, selected_neighbourhoods):
    if selected_neighbourhoods is None or selected_price_range is None:
        return dash.no_update
    
    filtered_df = df2[df2['neighbourhood_cleansed'].isin(selected_neighbourhoods)]
    filtered_df = filtered_df[(filtered_df['price'] >= selected_price_range[0]) & 
                              (filtered_df['price'] <= selected_price_range[1])]

    fig = px.histogram(filtered_df, x='price', nbins=50)
    
    fig.update_layout(
        title='Price Distribution',
        xaxis_title='Price (£)',
        yaxis_title='Count',
        bargap=0.1
    )
    
    return fig


#Callback for Property type Radio Items
@my_app.callback(
    Output('property-type-graph','figure'),
    [Input('property-type-radio','value')
     ]
)
def update_property_type_graph(selected_property_type):
    filtered_df= df2[df2['property_type']== selected_property_type]
    fig = px.bar(
       filtered_df.groupby('neighbourhood_cleansed').size().reset_index(name='count'),
       x='neighbourhood_cleansed',
       y='count',
       title=f"Count of listings by neighbourhood for {selected_property_type}"

    )
    fig.update_layout(
        xaxis_title='Neighbourhood',
        yaxis_title='Number of Listings',
        xaxis={'categoryorder':'total descending'}
    )

    return fig

# #callback for entire app
@my_app.callback(
    Output('neighborhood-property-stats-graph', 'figure'),
    [
        Input('property-type-dropdown', 'value'),
        Input('availability-type-dropdown', 'value'),
        Input('host-characteristics-checklist', 'value'),
        Input('price-range-slider', 'value')
    ]
)

def update_neighborhood_property_stats(selected_property_types, selected_availability_window, selected_host_characteristics, price_range):
    filtered_df = df2.copy()

    # Filter based on selected property types
    if selected_property_types:
        filtered_df = filtered_df[filtered_df['property_type'].isin(selected_property_types)]

    # Filter based on host characteristics
    if 'superhost' in selected_host_characteristics:
        filtered_df = filtered_df[filtered_df['host_is_superhost'] == 't']
    if 'profile_pic' in selected_host_characteristics:
        filtered_df = filtered_df[filtered_df['host_has_profile_pic'] == 't']
    if 'identity_verified' in selected_host_characteristics:
        filtered_df = filtered_df[filtered_df['host_identity_verified'] == 't']

    # Filter by price range
    filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

    # Group by neighborhood and calculate the metrics
    neighborhood_stats = filtered_df.groupby('neighbourhood_cleansed').agg({
        selected_availability_window: 'mean',
        'price': 'mean',
        'id': 'size'  # Count of properties
    }).reset_index().rename(columns={
        selected_availability_window: 'avg_availability',
        'price': 'avg_price',
        'id': 'count'
    })

    # Formatting averages
    neighborhood_stats['avg_availability'] = neighborhood_stats['avg_availability'].apply(lambda x: f"{round(x)} days")
    neighborhood_stats['avg_price'] = neighborhood_stats['avg_price'].apply(lambda x: f"£{x:.2f}")

    # Create the bar chart
    fig = px.bar(
        neighborhood_stats,
        x='neighbourhood_cleansed',
        y='count',
        color='avg_price',
        hover_data=['avg_availability'],
        title='Property Count, Average Price, and Availability by Neighborhood'
    )

    # Customize the layout
    fig.update_layout(
        xaxis_title='Neighborhood',
        yaxis_title='Count of Properties',
        coloraxis_colorbar_title='Average Price',
    )
    return fig


if __name__ == '__main__':
    my_app.run_server(debug=True,
                      port=8080,
                      host='0.0.0.0')




''' END HERE '''
#%%


