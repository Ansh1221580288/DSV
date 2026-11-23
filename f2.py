import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# Step 1: Load dataset
url = "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv"

df = pd.read_csv(url)

print("Dataset loaded successfully")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

# Step 2: Check required columns
required_columns = [
    'latitude', 'longitude', 'price', 'minimum_nights'
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

# Step 3: Clean dataset
df = df.dropna(subset=required_columns)

df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['minimum_nights'] = pd.to_numeric(
    df['minimum_nights'], errors='coerce'
)

df = df.dropna(subset=['price', 'minimum_nights'])

# Step 4: Create Dash application
app = Dash(__name__)

# Step 5: Create layout
app.layout = html.Div([

    html.H1(
        "Airbnb Data Analysis Dashboard",
        style={'textAlign': 'center', 'color': '#2c3e50'}
    ),

    html.Hr(),

    # Summary statistics
    html.Div([

        html.Div([
            html.H3("Total Listings"),
            html.H2(id='total-listings')
        ]),

        html.Div([
            html.H3("Average Price"),
            html.H2(id='average-price')
        ]),

        html.Div([
            html.H3("Average Minimum Nights"),
            html.H2(id='average-nights')
        ])

    ], style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'textAlign': 'center'
    }),

    html.Hr(),

    # Room type filter
    html.Label("Select Room Type"),

    dcc.Dropdown(
        id='room-filter',
        options=[
                    {'label': 'All Rooms', 'value': 'All'}
                ] + [
                    {'label': str(room), 'value': room}
                    for room in sorted(df['room_type'].dropna().unique())
                ] if 'room_type' in df.columns else [
            {'label': 'All Rooms', 'value': 'All'}
        ],
        value='All',
        clearable=False
    ),

    html.Br(),

    # Price filter
    html.Label("Select Maximum Price"),

    dcc.Slider(
        id='price-filter',
        min=0,
        max=int(df['price'].quantile(0.95)),
        step=10,
        value=int(df['price'].quantile(0.95)),
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Br(),

    # Charts
    html.Div([

        dcc.Graph(id='price-chart'),

        dcc.Graph(id='room-chart')

    ], style={
        'display': 'flex',
        'flexWrap': 'wrap'
    }),

    # Location chart
    dcc.Graph(id='location-chart')

], style={
    'padding': '20px',
    'fontFamily': 'Arial'
})


# Step 6: Create callback
@app.callback(

    Output('total-listings', 'children'),
    Output('average-price', 'children'),
    Output('average-nights', 'children'),
    Output('price-chart', 'figure'),
    Output('room-chart', 'figure'),
    Output('location-chart', 'figure'),

    Input('room-filter', 'value'),
    Input('price-filter', 'value')

)
def update_dashboard(selected_room, max_price):

    filtered_df = df[df['price'] <= max_price].copy()

    if selected_room != 'All' and 'room_type' in df.columns:
        filtered_df = filtered_df[
            filtered_df['room_type'] == selected_room
            ]

    # Summary statistics
    total = len(filtered_df)

    avg_price = (
        filtered_df['price'].mean()
        if total else 0
    )

    avg_nights = (
        filtered_df['minimum_nights'].mean()
        if total else 0
    )

    # Chart 1: Price distribution
    price_fig = px.histogram(
        filtered_df,
        x='price',
        title='Airbnb Price Distribution',
        nbins=30
    )

    # Chart 2: Room type distribution
    if 'room_type' in filtered_df.columns:
        room_fig = px.pie(
            filtered_df,
            names='room_type',
            title='Listings by Room Type'
        )
    else:
        room_fig = px.scatter(title='Room type column unavailable')

    # Chart 3: Geographic distribution
    location_fig = px.scatter_map(
        filtered_df,
        lat='latitude',
        lon='longitude',
        color='price',
        hover_data=['minimum_nights'],
        zoom=10,
        title='Airbnb Listings Location',
        height=600
    )

    return (
        f"{total:,}",
        f"${avg_price:,.2f}",
        f"{avg_nights:.1f}",
        price_fig,
        room_fig,
        location_fig
    )


# Step 7: Run application
if __name__ == '__main__':
    app.run(debug=True)
