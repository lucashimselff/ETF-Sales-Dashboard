import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pages.feature2_backend import find_advantage, clean_competitor_data, select_column

dash.register_page(__name__)

REGIONS = ["US Equity", "MM Equity", "CN Equity", "BH Equity", "TP Equity"]
COLORS = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]

def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    
    return fig

df_v2 = pd.read_excel("./static/Competitor Data_v2.xlsx", sheet_name=None)
df = df_v2["Competitor Data"]
df1 = pd.read_csv("price data/JEPI US Equity.csv") #to get columns for time-series plot

excluded_columns = ["North", "Name", "Primary Exchange", "Ticker", "Parent Comp. Name", "Fund Objective", 
"Fund Geographical Focus", "Fund Asset Class Focus", "General Attribute"] # Remove all non-quantiative columns

layout = html.Div(
    [
        # This Div is responsible for the Selection of Graph Type and Axes
        html.Div([ 
            html.Div([
                html.Div([
                    html.Img(src="../assets/Icons/IconGraph.svg", className="w-[25px] h-[25px]"),
                    html.Span("Graph Settings", className="text-[18px] font-medium")
                ], className="flex gap-2 items-center pb-2 border-b-2 border-b-bronze"),
                
                html.Div([    
                    dcc.Dropdown(
                        id='graph-type',
                        placeholder="Select a Graph Type",
                        options=[
                            {'label': '3D Scatter Plot', 'value': 'scatter_3d'},
                            {'label': '2D Scatter Plot', 'value': 'scatter'},
                            {'label': 'Bar Chart', 'value': "bar_chart"},
                            {'label': 'Time Series Line Plot', 'value': 'time_series'},
                        ],
                    ),
                ]),

                html.Div(id="x-variable-div", children=[
                    dcc.Dropdown(
                        id='x-variable',
                        placeholder="Select X Variable:",
                        options=[
                            {'label': col, 'value': col} for col in df.columns if col not in excluded_columns
                        ],
                    ),
                ]),

                html.Div(id="y-variable-div", children=[  
                    dcc.Dropdown(
                        id='y-variable',
                        placeholder="Select Y Variable:",
                        options=[
                            {'label': col, 'value': col} for col in df.columns if col not in excluded_columns
                        ],
                    ),
                ]),

                html.Div(id="z-variable-div", children=[
                    dcc.Dropdown(
                        id='z-variable',
                        placeholder="Select Z Variable:",
                        options=[
                            {'label': col, 'value': col} for col in df.columns if col not in excluded_columns
                        ],
                    ),
                ]),
                
                html.Div(id="period-div", children=[
                    dcc.Dropdown(
                        id="period",
                        placeholder="Select Time Period",
                        options=[
                            {"label": "1 Month", "value": "30"},
                            {"label": "3 Months", "value": "90"},
                            {"label": "6 Months", "value": "180"},
                            {"label": "1 Year", "value": "365"},
                            {"label": "3 Years", "value": "1095"},
                        ],
                    ),
                ]),
                
                #select the y variable for time-series plot
                html.Div(id="column-div", children=[
                    dcc.Dropdown(
                        id='column',
                        placeholder="Select Variable:",
                        options=[
                            {'label': col, 'value': col} for col in df1.columns
                        ],
                        #value = 'FUND_NET_ASSET_VAL',
                    ),
                ])
                
            ], className="flex flex-col gap-4"),
            
            html.Div([

                html.Div([
                    html.Img(src="../assets/Icons/IconCompetitor.svg", className="w-[25px] h-[25px]"),
                    html.Span("Competitor ETFs", className="text-[18px] font-medium")
                ], className="flex gap-2 items-center pb-2 border-b-2 border-b-bronze mb-2"),
                
                # Stores selected competitors
                dcc.Store(id="selected-competitor-data", data={ "tickers": [] }),
                
                # Displays selected competitors
                html.Div([
                    html.Div(id="selected-competitors", children=[
                    ], className=""),
                ], className="flex flex-col gap-2"),
                
                # Displays Competitors in a Selectable List
                dmc.Accordion([
                    dmc.AccordionItem([
                        dmc.AccordionControl(region, className="py-3 text-aqua font-medium focus:bg-gray-light focus:font-bold"),
                        dmc.AccordionPanel([      
                            dash.dash_table.DataTable(
                                id={ "type": "ticker-selection", "index": 0 },
                                columns=[{"name": 'Ticker', "id": 'Ticker'}],
                                data=df_v2[region].to_dict("records"),
                                column_selectable="multi",
                                editable=False,
                                row_selectable="multi",
                                style_table={"overflowY": 20, "font-size": "16px", "width": "100%", "margin-top": "-1rem"},
                                style_cell={"textAlign": "left", "font-family": "system-ui"},
                                style_header={"border": "none", "visibility": "hidden"},
                                style_filter={"background-color": "transparent", "color": "#AAAAAA"},
                                style_data={"border": "none", "background-color": "transparent"},
                                page_size= 10,
                                filter_action="native",
                            ),
                        ], className="bg-aqua/5")
                    ], value=region) for region in REGIONS
                ])                      
            ]),
        
        ], className="flex flex-col gap-4"),
        
        html.Div([
            html.Div(id="graph-div"),
            html.Div(
                id='advantages-box', 
                className="hidden",
            )
        ], className="w-full flex flex-col")

    ], className="p-8 flex gap-8"
)

# Function for showing competitors upon selected
@dash.callback(
    [
        Output("selected-competitor-data", "data"),
        Output("selected-competitors", "children"),
        Output("selected-competitors", "className")
    ],
    [
        Input({"type": "ticker-selection", "index": ALL }, "derived_virtual_indices"),
        Input({"type": "ticker-selection", "index": ALL }, "derived_virtual_selected_rows"),
    ],
    State("selected-competitor-data", "data")
)
def show_selected_competitors(visible_rows, selected_ticker_indices, current_selection: dict[str, list[tuple[int, str]]]):
    
    if None in selected_ticker_indices:
        return current_selection, "", "hidden"
    
    ticker_indices = list(map(lambda x: x[0], current_selection["tickers"]))
    ticker_values = list(map(lambda x: x[1], current_selection["tickers"]))
    
    global_ticker_indices = set()

    for region_ind, region_dt in enumerate(selected_ticker_indices):
        region = REGIONS[region_ind]
        
        for ticker_ind in region_dt:
            global_ticker_ind = visible_rows[region_ind][ticker_ind]
            global_ticker_indices.add(global_ticker_ind)
            ticker = df_v2[region].iloc[global_ticker_ind]["Ticker"]
            
            # add new selection
            if ticker not in ticker_values:
                current_selection["tickers"].append((global_ticker_ind, ticker))
    
    # remove deselected options
    deselection = list(set(ticker_indices) - global_ticker_indices)
    new_selection = list(filter(lambda x: x[0] not in deselection, current_selection["tickers"]))
    
    return { "tickers": new_selection }, [html.Div([
        html.Span(ticker, className="text-jade font-medium text-[14px]")
    ], className="px-4 py-2 bg-gray-light rounded-[20px]") for ticker in map(lambda x: x[1], new_selection)], "flex flex-wrap gap-2 mb-2 rounded-lg"

# update selector according to graph-type selected
@dash.callback(
    Output('x-variable-div', 'className'),
    Output('y-variable-div', 'className'),
    Output('z-variable-div', 'className'),
    Output('period-div', 'className'),
    Output('column-div', 'className'),
    Input('graph-type', 'value'),
)
def update_dropdowns(graph_type):
    # Show by default
    x_variable_style = "block"
    y_variable_style = "block"
    z_variable_style = "block"
    period_style = "block"
    column_style = "block"  

    if graph_type == 'scatter_3d':
        period_style = "hidden"
        column_style = "hidden"
        
    elif graph_type == 'scatter':
        z_variable_style = "hidden"
        period_style = "hidden"
        column_style = "hidden"

    elif graph_type == 'bar_chart':
        x_variable_style = "hidden"
        z_variable_style = "hidden"
        period_style = "hidden"
        column_style = "hidden"
    
    elif graph_type == 'time_series':
        x_variable_style = "hidden"
        y_variable_style = "hidden"
        z_variable_style = "hidden"
    
    else:
        x_variable_style = "hidden"
        y_variable_style = "hidden"
        z_variable_style = "hidden"
        period_style = "hidden"
        column_style = "hidden" 

    return x_variable_style, y_variable_style, z_variable_style, period_style, column_style

plot_metric = {
    'Tot Asset US$ (M)' : 'FUND_NET_ASSET_VAL',
    'Avg Dvd Yield' : 'TOT_RETURN_INDEX_GROSS_DVDS',
}    

# Function for updating the Graph depending on the selected Graph Type and Axes
@dash.callback(
    Output("graph-div", "children"),
    Input("graph-type", "value"),
    Input("x-variable", "value"),
    Input("y-variable", "value"),
    Input("z-variable", "value"),
    Input("period", "value"),
    Input("column", "value"),
    Input("selected-competitor-data", "data"),
    prevent_initial_call=True
)
def update_graph(
    graph_type, x_variable, y_variable, z_variable, time_period, column, selection
):
    selected_tickers = list(map(lambda x: x[1], selection["tickers"]))
    
    figure = {}
    if graph_type == "scatter_3d":
        figure = px.scatter_3d(
            df[df["Ticker"].isin(selected_tickers)],
            x=x_variable,
            y=y_variable,
            z=z_variable,
            color="Ticker",
        ).update_layout(
            scene=dict(
                xaxis_title=x_variable,
                yaxis_title=y_variable,
                zaxis_title=z_variable,
            ),
            margin={"l":0,"r":0,"t":0,"b":0},
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.05
            )
        )

    elif graph_type == "scatter":
        figure = px.scatter(
            df[df["Ticker"].isin(selected_tickers)],
            x=x_variable,
            y=y_variable,
            color="Ticker",
        ).update_layout(
            xaxis_title=x_variable,
            yaxis_title=y_variable,
            margin={"t":0,"b":0},
        )
    
    elif graph_type == "bar_chart":
        if y_variable is None:
            return
        figure = px.bar(
            df[df["Ticker"].isin(selected_tickers)],
            x="Ticker",
            y=y_variable,
            color="Ticker",
        ).update_layout(
            xaxis_title="ETF Tickers",
            yaxis_title=y_variable,
            margin={"t":0,"b":0},
        )
        
    elif graph_type == "time_series":
        if time_period is None or column is None:
            return
        period = int(time_period)
        figure = go.Figure()
        for ind, ticker in enumerate(selected_tickers):
            etf_data = select_column(ticker, column)[:period]
            etf_data["Date"] = pd.to_datetime(etf_data["Date"])
            etf_trace = go.Scatter(
                x=etf_data["Date"],
                y=etf_data[column],
                name=ticker,
                mode="lines",
                line=dict(color=COLORS[ind])
            )
            figure.add_trace(etf_trace)
        figure.update_layout(
            xaxis_title='Date',
            yaxis_title=column,
            margin={"t":0,"b":0}
        )
    return dcc.Graph(id="graph", figure=figure, className="h-[560px] -mt-4 border-b-2 border-bronze pb-3")
    

@dash.callback(
    Output("advantages-box", "className"),
    Input({"type": "ticker-selection", "index": ALL }, "derived_virtual_selected_rows")
)
def hide_advantages_box(selected_ticker_indices):
    if None in selected_ticker_indices:
        return "hidden"

    selected = [competitor for region in selected_ticker_indices for competitor in region]
    if len(selected) < 2:
        return "hidden"
    else:
        return "self-center pt-2 w-fit"

# Function for updating the advantages box
@dash.callback(
    Output('advantages-box', 'children'),
    Input({"type": "ticker-selection", "index": ALL }, "derived_virtual_selected_rows")
)
def update_advantages_box(selected_ticker_indices):
    if None in selected_ticker_indices:
        return

    ticker_values = []
    for region_ind, region_dt in enumerate(selected_ticker_indices):
        for ticker_ind in region_dt:
            region = REGIONS[region_ind]
            ticker = df_v2[region].iloc[ticker_ind]["Ticker"]
            ticker_values.append(ticker)

    if len(ticker_values) < 2:
        return
    
    data_frame = clean_competitor_data(df)
    advantages = find_advantage(data_frame, ticker_values[0], ticker_values[1:])

    unbiased_metrics = ["Expense Ratio", "Beta 1Y-M", "Beta 3Y"]
    
    if advantages:
        competitor_list = []
        for competitor, advantage in advantages.items():
            max_value = max(advantage.tolist())
            competitor_section = [html.P(html.Strong(competitor))]

            for column, value in advantage.items():
                if value == max_value and value != float('inf'):
                    column_value_div = html.Div(
                        children=[
                            html.P(f"{column}:", style={"text-align": "left"}),
                            html.P(f"{value}% better", style={"text-align": "right", "color": "green"})
                        ],
                        style={"display": "flex", "justify-content": "space-between"}
                    )
                    competitor_section.append(column_value_div)
                else:
                    if value == float('inf') or value == -float('inf') or np.isnan(value):
                        pass
                    else:
                        if value > 0:
                            if column not in unbiased_metrics:
                                column_value_div = html.Div(
                                    children=[
                                        html.P(f"{column}:", style={"text-align": "left"}),
                                        html.P(f"{value}% better", style={"text-align": "right", "color": "green"})
                                    ],
                                    style={"display": "flex", "justify-content": "space-between"}
                                ) 
                            else:
                                if column == "Expense Ratio":
                                    column_value_div = html.Div(
                                        children=[
                                            html.P(f"{column}:", style={"text-align": "left"}),
                                            html.P(f"{value}% higher", style={"text-align": "right", "color": "red"})
                                        ],
                                        style={"display": "flex", "justify-content": "space-between"}
                                    ) 
                                else:
                                    column_value_div = html.Div(
                                        children=[
                                            html.P(f"{column}:", style={"text-align": "left"}),
                                            html.P(f"{value}% higher", style={"text-align": "right"})
                                        ],
                                        style={"display": "flex", "justify-content": "space-between"}
                                    ) 

                        elif value == 100:
                            pass

                        else:
                            value = - value
                            if column not in unbiased_metrics:
                                column_value_div = html.Div(
                                    children=[
                                        html.P(f"{column}:", style={"text-align": "left"}),
                                        html.P(f"{value}% worse", style={"text-align": "right", "color": "red"})
                                    ],
                                    style={"display": "flex", "justify-content": "space-between"}
                                )
                            else:
                                if column == "Expense Ratio":
                                    column_value_div = html.Div(
                                        children=[
                                            html.P(f"{column}:", style={"text-align": "left"}),
                                            html.P(f"{value}% lower", style={"text-align": "right", "color": "green"})
                                        ],
                                        style={"display": "flex", "justify-content": "space-between"}
                                    )
                                else:
                                    column_value_div = html.Div(
                                        children=[
                                            html.P(f"{column}:", style={"text-align": "left"}),
                                            html.P(f"{value}% lower", style={"text-align": "right"})
                                        ],
                                        style={"display": "flex", "justify-content": "space-between"}
                                    )

                        competitor_section.append(column_value_div)

            modal_competitors = [df[df['Ticker'] == ticker_values[0]].drop(columns = ["North"]),
                df[df['Ticker'] == competitor].drop(columns = ["North"])]
            
            competitor_section.append(html.Div(
                children=[
                dmc.Button(
                    "View Data",
                    id = "open",
                    className="bg-bronze text-white font-bold py-2 px-4 rounded-full mx-auto",
                    style = {"padding": "10px", "margin": "5px", "width": "100%"}
                ),
                # Add a Modal to display actual data as a table between Competitor and main ETF:
                dmc.Modal(
                    title = f"{ticker_values[0]} vs. {competitor}",
                    id="modal",
                    zIndex=10000,
                    size = "100%",
                    children=[
                        dag.AgGrid(
                            id='competitor-table',
                            rowData= pd.concat(modal_competitors).to_dict("records"),
                            columnDefs = [{"headerName": i, "field": i.replace(".", ""), "sortable": True} 
                                for i in pd.concat(modal_competitors).columns],
                        ),
                        dmc.Group(
                        [
                            dmc.Button("Submit", id="modal-submit-button"),
                            dmc.Button(
                                "Close",
                                color="red",
                                variant="outline",
                                id="modal-close-button",
                            ),
                        ],
                        position="right",
                        ),
                    ]),
                ],
            ))

            competitor_list.append(html.Div(competitor_section, style={"marginRight": "20px", "padding": "10px"}))

        container = html.Div(
            children=[
                html.H2(
                html.Strong(f"Comparing {ticker_values[0]} to:"),
                style={"text-align": "center", "font-size": "24px"}
            ),
                html.Div(competitor_list, style={"display": "flex", "justify-content": "space-between"})
            ]
        )

    return container

@dash.callback(
    Output("modal", "opened"),
    Input("open", "n_clicks"),
    Input("modal-close-button", "n_clicks"),
    Input("modal-submit-button", "n_clicks"),
    State("modal", "opened"),
    prevent_initial_call=True,
)
def modal_demo(nc1, nc2, nc3, opened):
    return not opened