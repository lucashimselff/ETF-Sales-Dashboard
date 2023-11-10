import dash
from dash import dcc, html, Input, Output, ALL
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from pages.feature2_backend import find_advantage
from pages.feature2_backend import clean_competitor_data

dash.register_page(__name__)

REGIONS = ["US Equity", "MM Equity", "CN Equity", "BH Equity", "TP Equity"]
#df = pd.read_csv("./Competitor Data.csv")
df_v2 = pd.read_excel("./static/Competitor Data_v2.xlsx", sheet_name=None)
df = df_v2["Competitor Data"]

layout = html.Div(
    [
        # This Div is responsible for the Selection of Graph Type and Axes
        html.Div([ 

            html.Div([
                
                html.Div([
                    html.Img(src="../assets/Icons/IconGraph.svg", className="w-[25px] h-[25px]"),
                    html.Span("Graph Settings", className="text-[18px] font-medium")
                ], className="flex gap-2 items-center pb-2 border-b-2 border-b-bronze"),
                
                dcc.Dropdown(
                    id='graph-type',
                    placeholder="Select a Graph Type",
                    options=[
                        {'label': '3D Scatter Plot', 'value': 'scatter_3d'},
                        {'label': '2D Scatter Plot', 'value': 'scatter'},
                    ],
                ),

                dcc.Dropdown(
                    id='x-variable',
                    placeholder="Select X Variable:",
                    options=[
                        {'label': col, 'value': col} for col in df.columns
                    ],
                ),

                dcc.Dropdown(
                    id='y-variable',
                    placeholder="Select Y Variable:",
                    options=[
                        {'label': col, 'value': col} for col in df.columns
                    ],
                ),

                dcc.Dropdown(
                    id='z-variable',
                    placeholder="Select Z Variable:",
                    options=[
                        {'label': col, 'value': col} for col in df.columns
                    ],
                    #value = 'Avg Dvd Yield'
                ),
                
            ], className="flex flex-col gap-4"),
            
            html.Div([
                
                html.Div([
                    html.Img(src="../assets/Icons/IconCompetitor.svg", className="w-[25px] h-[25px]"),
                    html.Span("Competitor ETFs", className="text-[18px] font-medium")
                ], className="flex gap-2 items-center pb-2 border-b-2 border-b-bronze mb-2"),

                # html.Label('Select Competitor ETFs:'),
                
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
                                style_table={"overflowY": 20},
                                style_cell={"textAlign": "left"},
                                page_size= 20,
                                filter_action="native",
                            ),                    
                                        
                            # dcc.Checklist(
                            #     id={
                            #         "type": "ticker-selection",
                            #         "index": 0
                            #     },
                            #     options=[{"label": html.Span(ticker, className="ml-2"), "value": ticker} for ticker in df_v2[region]["Ticker"]
                            # ], value=[], labelClassName="my-2 ml-2 !flex items-center", inputClassName="min-w-[20px] min-h-[20px] rounded-sm")
                            
                        ], className="bg-aqua/5")
                    ], value=region) for region in REGIONS
                ])            
                
                # dash.dash_table.DataTable(
                #     id="selection-checkbox-grid",
                #     columns=[{"name": 'Ticker', "id": 'Ticker'}],
                #     data=df.to_dict("records"),
                #     column_selectable="multi",
                #     editable=False,
                #     row_selectable="multi",
                #     style_table={"overflowY": 20},
                #     style_cell={"textAlign": "left"},
                #     page_size= 20,
                #     filter_action="native",
                # ),
                # html.Div(id="selection-output"),
            
            ]),
        
        ], className="flex flex-col gap-4 "),
        
        html.Div([
            
            dcc.Graph(id='graph', className="w-full"),#, className="py-8 flex justify-center gap-12"),
            html.Div(
                id='advantages-box',
                className="absolute top-[30%] right-[10px] p-4 border border-gray-medium rounded-lg",
                #style={'position': 'absolute', 'top': '30%', 'right': '10px'}
            )
            # dcc.Graph(id='graph', className="p-8 flex justify-center gap-12")
            # html.Div(id='graph-container', style={'display:none'}, className="p-8 flex justify-center gap-12")
        # ],
         
        ], className="flex justify-center w-full max-h-[]")
        
    ], className="p-8 flex gap-12"
)

# Function for updating the Graph depending on the selected Graph Type and Axes
@dash.callback(
    Output("graph", "figure"),
    Input("graph-type", "value"),
    Input("x-variable", "value"),
    Input("y-variable", "value"),
    Input("z-variable", "value"),
    Input({"type": "ticker-selection", "index": ALL }, "derived_virtual_selected_rows")
    #dash.dependencies.Input("selection-checkbox-grid", "derived_virtual_data"),
    #dash.dependencies.Input("selection-checkbox-grid", "derived_virtual_selected_rows"),
)
def update_graph(
    graph_type, x_variable, y_variable, z_variable, selected_ticker_indices #rows, selected_rows
):
    #print(rows)
    #print(selected_rows)
    #print(selected_ticker_indices)
    
    # selected_Tickers = [
    #     rows[row]["Ticker"] for row in selected_rows
    # ] if selected_rows else "None"

    selected_tickers = []
    for region_ind, region_dt in enumerate(selected_ticker_indices):
        for ticker_ind in region_dt:
            region = REGIONS[region_ind]
            ticker = df_v2[region].iloc[ticker_ind]["Ticker"]
            selected_tickers.append(ticker)
    #print(selected_tickers)
    
    #selected_Tickers = [ticker for region in selected_tickers for ticker in region]

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
            width=800,
            height=800,
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
            width=800,
            height=800,
        )

    return figure

@dash.callback(
    Output('selected-div', 'children'),
    Input('checkbox', 'value')
)
def update_selected_div(selected_options):
    if selected_options:
        selected_divs = []
        for option in selected_options:
            selected_divs.append(html.Div(f'Selected Option: {option}', className='selected-opyion'))
        return selected_divs
    else:
        return []
    
    
# Function for updating the advantages box
@dash.callback(
    dash.dependencies.Output('advantages-box', 'children'),
    # dash.dependencies.Input('checkbox', 'value'),
    dash.dependencies.Input("selection-checkbox-grid", "derived_virtual_selected_rows"),
)
def update_advantages_box(selected_options):
    if selected_options is None:
        return
    if len(selected_options) < 2:
        return
    data_frame = pd.read_csv('Competitor Data.csv')
    data_frame = clean_competitor_data(data_frame)

    ticker_values = df.loc[selected_options, "Ticker"].tolist()

    advantages = find_advantage(data_frame, ticker_values[0], ticker_values[1])
    
    if not advantages.empty:
        advantage_list = []
        container_style = {'display': 'flex', 'justify-content': 'space-between'}
        max_value = max(advantages.tolist())
        advantage_list.append(html.H2(ticker_values[0] + " v.s. " + ticker_values[1], style={'font-size': '24px'}))
        # advantage_list.append(html.H2("JEPI US Equity v.s. CQQQ US Equity", style={'font-size': '24px'}))
        for index, value in advantages.items():
            # advantage_list.append(html.P(f'{index}:'))
            # advantage_list.append(html.P(f'{value}% better', style={'text-align': 'right'}))
            if value == max_value and value != float('inf'):
                container = html.Div(style=container_style, children=[
                html.P(f'{index}:', style={'color' : 'green'}),
                html.P(f'{value}% better', style={'text-align': 'right', 'color' : 'green'})
            ])
            else:
                if value == float('inf') or value == -float('inf'):
                    container = html.Div(style=container_style, children=[
                    html.P(f'{index}:'),
                    html.P('data missing', style={'text-align': 'right'})
                ])
                else:
                    container = html.Div(style=container_style, children=[
                        html.P(f'{index}:'),
                        html.P(f'{value}% better', style={'text-align': 'right'})
                    ])
            advantage_list.append(container)
    return advantage_list


# @dash.callback(
#     dash.dependencies.Output('advantages-box', 'children'),
#     dash.dependencies.Input('checkbox', 'value')
# )
# def update_advantages_box(selected_options):
#     data_frame = pd.read_csv('Competitor Data.csv')
#     data_frame = clean_competitor_data(data_frame)

#     # if len(selected_options) == 2:
#     # advantage_label_1 = next((item['label'] for item in options if item['value'] == selected_options[0]), '')
#     # advantage_label_2 = next((item['label'] for item in options if item['value'] == selected_options[1]), '')
#     advantage_value = find_advantage(data_frame, selected_options[0], selected_options[1])
        
#     if not advantage_value.empty:
#         advantage_list = []
#         container_style = {'display': 'flex', 'justify-content': 'space-between'}
            
#         advantage_list.append(html.Div(style=container_style, children=[
#             # html.P(f'{advantage_label_1} vs {advantage_label_2}:'),
#             html.P(f'{advantage_value}% better', style={'text-align': 'right'})
#         ]))
            
#         return advantage_list

# dash.register_page(__name__)


# df = pd.read_csv("./Competitor Data.csv")

# columnDefs = [
#     {"field": "Ticker", "checkboxSelection": True},
# ]

# defaultColDef = {
#     "flex": 1,
#     "minWidth": 150,
#     "sortable": True,
#     "resizable": True,
#     "filter": True,
# }

# layout = html.Div(
#     [
#         # Displays Competitors in a Selectable List
#         dash.dash_table.DataTable(
#             id="selection-checkbox-grid",
#             columns=[{"name": 'Ticker', "id": 'Ticker'}],
#             data=df.to_dict("records"),
#             column_selectable="multi",
#             editable=False,
#             row_selectable="multi",
#             style_table={"overflowY": 20},
#             style_cell={"textAlign": "left"},
#         ),
#         html.Div(id="selection-output"),

#         # This Div is responsible for the Selection of Graph Type and Axes
#         html.Div(
#             [
#                 html.H1("Select a Graph Type:"),
#                 dcc.Dropdown(
#                     id="graph-type",
#                     options=[
#                         {"label": "3D Scatter Plot", "value": "scatter_3d"},
#                         {"label": "2D Scatter Plot", "value": "scatter"},
#                     ],
#                     value="scatter_3d",
#                 ),

#                 html.Label("Select X Variable:"),
#                 dcc.Dropdown(
#                     id="x-variable",
#                     options=[{"label": col, "value": col} for col in df.columns],
#                     value="Expense Ratio",
#                 ),

#                 html.Label("Select Y Variable:"),
#                 dcc.Dropdown(
#                     id="y-variable",
#                     options=[{"label": col, "value": col} for col in df.columns],
#                     value="Avg Dvd Yield",
#                 ),

#                 html.Label("Select Z Variable:"),
#                 dcc.Dropdown(
#                     id="z-variable",
#                     options=[{"label": col, "value": col} for col in df.columns],
#                     value="Alpha 3Y",
#                 ),
#             ],
#             className="p-4 flex flex-col gap-4 w-[20%] border border-gray-medium rounded-lg",
#         ),
#         dcc.Graph(id="graph", className="p-8 flex justify-center gap-12"),
#     ],
#     className="p-8 flex justify-center gap-12",
# )


# @dash.callback(
#     dash.dependencies.Output("graph", "figure"),
#     dash.dependencies.Input("graph-type", "value"),
#     dash.dependencies.Input("x-variable", "value"),
#     dash.dependencies.Input("y-variable", "value"),
#     dash.dependencies.Input("z-variable", "value"),
#     dash.dependencies.Input("selection-checkbox-grid", "derived_virtual_data"),
#     dash.dependencies.Input("selection-checkbox-grid", "derived_virtual_selected_rows"),
# )
# def update_graph(
#     graph_type, x_variable, y_variable, z_variable, rows, selected_rows
# ):
#     selected_Tickers = [
#         rows[row]["Ticker"] for row in selected_rows
#     ] if selected_rows else "None"

#     if graph_type == "scatter_3d":
#         figure = px.scatter_3d(
#             df[df["Ticker"].isin(selected_Tickers)],
#             x=x_variable,
#             y=y_variable,
#             z=z_variable,
#             color="Ticker",
#         ).update_layout(
#             scene=dict(
#                 xaxis_title=x_variable,
#                 yaxis_title=y_variable,
#                 zaxis_title=z_variable,
#             ),
#             width=800,
#             height=800,
#         )

#     elif graph_type == "scatter":
#         figure = px.scatter(
#             df[df["Ticker"].isin(selected_Tickers)],
#             x=x_variable,
#             y=y_variable,
#             color="Ticker",
#         ).update_layout(
#             xaxis_title=x_variable,
#             yaxis_title=y_variable,
#             width=800,
#             height=800,
#         )

#     return figure


