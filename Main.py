import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output


app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

## Data processing

df_agri = pd.read_csv("Agri_Land.csv")
df_for = pd.read_csv("Forest_Land.csv")

df_for = df_for.iloc[3:].reset_index(drop=True)
df_for.columns = df_for.iloc[0]
df_for = df_for[1:].reset_index(drop=True)
df_for.columns.name = None

df_agri = df_agri.iloc[3:].reset_index(drop=True)
df_agri.columns = df_agri.iloc[0]
df_agri = df_agri[1:].reset_index(drop=True)
df_agri.columns.name = None

# List of recognized countries
# sourced from Chat_GPT
south_american_countries = [
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"
]
def filter_countries(data):
    """Filters the dataset to keep only recognized countries."""
    return data[data['Country Name'].isin(south_american_countries)]

df_for = filter_countries(df_for)
df_agri = filter_countries(df_agri)

# Dictionary to reference datasets
# chat_GPT
datasets = {
    "Forest Land": df_for,
    "Agricultural Land": df_agri
}

app.layout = dbc.Container(
    [
        dbc.Row( html.H1(
                        "Farms vs. Forest: South America",
                        style={"textAlign": "center"}),),
                html.H3("Explore how agriculture land and Forest areas have changed over time in South America"
                        ,
                        style={"textAlign": "center"}
                        ),
        dbc.Row([
            dbc.Col(
                    dcc.Graph(id="my-choropleth", figure={}),
                width=6,
            ),
            dbc.Col(
                dcc.Graph(
                    id = "my-line-chart",
                    figure ={}
                )
            )
            ]
        ),
        dbc.Col([dbc.Label(
                            "Select Years:",
                            className="fw-bold",
                            style={"textDecoration": "underline", "fontSize": 20},
                        ),
                        dcc.Slider(
                            id="years-slider",
                            step=1,
                            value= 2005,
                            marks={
                                ## list made with Chat_GBT
                                 1990: "'90",
                                 1991: "'91",
                                 1992: "'92",
                                 1993: "'93",
                                 1994: "'94",
                                 1995: "'95",
                                 1996: "'96",
                                 1997: "'97",
                                 1998: "'98",
                                 1999: "'99",
                                 2000: "2000",
                                 2001: "'01",
                                 2002: "'02",
                                 2003: "'03",
                                 2004: "'04",
                                 2005: "'05",
                                 2006: "'06",
                                 2007: "'07",
                                 2008: "'08",
                                 2009: "'09",
                                 2010: "'10",
                                 2011: "'11",
                                 2012: "'12",
                                 2013: "'13",
                                 2014: "'14",
                                 2015: "'15",
                                 2016: "'16",
                                 2017: "'17",
                                 2018: "'18",
                                 2019: "'19",
                                 2020: "'20",
                                 2021: "'21",
                                 2022: "'22",
                            },
                        ),
        ],
            width = 12,
        ),
        dbc.Row(
            dbc.Col(
                dcc.RadioItems(
                    id = "dataset-toggle",
                    options=[
                        ## Chat_GPT debugged using multiple data sets with dictionaries
                        {"label": "Forest Land", "value": "Forest Land"},
                        {"label": "Agricultural Land", "value": "Agricultural Land"}
                    ],
                    value = "Agricultural Land",
                )
            )
        ),
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id = "country-dropdown",
                    options=[{'label': country, 'value': country} for country in df_agri['Country Name'].unique()],
                    value = "Brazil",
                    style = {"color" :"Black"}
                ),
             width = 2
            ),
            dbc.Col(dcc.Graph(id="my-bar-graph", figure={})
            ),
            ]
        ),
        dbc.Row(
            html.A('Lear how to help!!', href = 'https://www.globalforestgeneration.org', target = '_blank', style = {'fontSize':'40px',"textAlign": "center"})
        )
    ]
)


@app.callback(
    Output("my-choropleth","figure"),
    Output("my-line-chart", "figure"),
    Input("years-slider", "value"),
    Input("dataset-toggle","value"),
    Input("my-choropleth","clickData")
)

def update_map(selected_year, data, clickData):
    df_selected = datasets[data]
    if str(data) == "Forest Land":
        color = "Greens"
    else:
        color = "oranges"
    fig_map = px.choropleth(
        df_selected,
        locations= "Country Code",
        color = selected_year,
        scope="south america",
        hover_name = "Country Name",
        color_continuous_scale= color,
    )
    ## Chat_GPT helped make the line graph changed based on click
    # If a country is clicked, show line chart
    if clickData:
        # Get the clicked country information
        country = clickData['points'][0]['location']
        country_name = df_selected[df_selected['Country Code'] == country]['Country Name'].values[0]

        # Fetch data for the selected country
        country_data_agri = df_agri[df_agri['Country Name'] == country_name].iloc[:, 3:]
        country_data_for = df_for[df_for['Country Name'] == country_name].iloc[:, 3:]

        # make a data frame for the line graph
        df_line = pd.DataFrame({
            'Year': country_data_agri.columns,
            'Agricultural Land': country_data_agri.values.flatten(),
            'Forest Land': country_data_for.values.flatten(),
        })

        fig_line = px.line(df_line, x='Year', y=['Agricultural Land', 'Forest Land'],
                           title=f"Land Use for {country_name}",
                           labels={'Year': 'Year', 'value': 'Percentage of Land'})
        fig_line.update_layout(
            yaxis=dict(
            range=[0, 100]
        )

        )



    else:
        fig_line = px.line(pd.DataFrame({'Year': [], 'Agricultural Land': [], 'Forest Land': []}),
                           x='Year', y=['Agricultural Land', 'Forest Land'],
                           title="Select a Country to See the Data")

    return fig_map, fig_line


@app.callback(
    Output("my-bar-graph", "figure"),
    Input("country-dropdown", "value"),
    Input("years-slider", "value"),

)
def update_bar(country, year):
    ## data selecting build with Chat_GPT
    country_data_agri = df_agri[df_agri['Country Name'] == country].iloc[:, 3:]
    country_data_for = df_for[df_for['Country Name'] == country].iloc[:, 3:]
    agri_value = country_data_agri[(year)].values[0]
    for_value = country_data_for[(year)].values[0]

    fig = px.bar(
        x = ["Forest Area", "Agricultural Area"],
        y = [for_value, agri_value],
        title = f"Land Use for {country} in {year}"
    )
    fig.update_layout(
         yaxis=dict(
            title="Percentage of Land",
            range=[0, 100]
        )
    )
    return fig






if __name__ == "__main__":
    app.run_server(debug=True)



