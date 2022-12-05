# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash_cytoscape as cyto
cyto.load_extra_layouts()
from datetime import date
import plotly.graph_objects as go
from dynamicTimeWarping import dTimeWarp
from forecasting import read_data
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

app = Dash(__name__)

df = pd.read_csv("./data/final_dataset.csv")
data = pd.read_csv("./data/final_dataset.csv")
data['Date'] = pd.to_datetime(data['Date'])
c = data.drop('Date',axis = 1)
cols = df.columns.tolist()[1:]

app = Dash(external_stylesheets=[dbc.themes.DARKLY])
load_figure_template('DARKLY')

app.layout = html.Div(children=[
    html.H1(children='Asset Interdependence', style={"alignContent":"center"}),

    html.Label('Please select the assets for which you would like to visualize interdependence'),
    html.Br(),

    dcc.Dropdown(cols,
                [],
                multi=True,
                id='asset-select',
                style={'color': 'black'}),

    html.Br(),
        
    dcc.Graph(id='line-chart'),

    html.Br(),
    html.Label('Select correlation method for graph'),

    dcc.Dropdown(['Pearson', 'Spearman','Kendall','Dynamic Time Warping'],'Pearson', 
                id='corr-dropdown', style={'color': 'black'}),

    html.Div([
        html.Br(),
        html.Label('Please select a date range for which to identify correlations', id='my-date-picker-range-al'),
        html.Br(),
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed= date(2013, 1, 2),
            max_date_allowed= date(2021, 2, 9),
            initial_visible_month=date(2013, 1, 2)
            ),
    ], id='my-date-picker-range-div', style={'display':'block'}),
    
    html.Br(),
    
    html.Label('Please select the desired shape of the graph'),
    dcc.Dropdown(
    id='dropdown-update-layout',
    style={'color': 'black'},
    value='breadthfirst',
    clearable=False,
    options=[
        {'label': name.capitalize(), 'value': name}
        for name in ['breadthfirst','cola','euler','spread','klay','dagre','grid', 'circle', 'concentric']
    ],
    ),

    html.Br(),

    html.P("Asset Correlations: (Each asset class is represented by different colors)"),
    html.P(id='cytoscape-mouseoverEdgeData-output'),
    cyto.Cytoscape(
        id='cytoscape',
        elements = [],
        layout={'name': 'breadthfirst'},
        style={'width': '100%', 'height': '500px'},
        stylesheet=[
            {
                'selector': 'edge',
                'style': {
                    "line-width": 'data(weight)',
                },
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'color': 'white'
                }
            },
            {
                'selector': '.red',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red'
                }
                    
            },
            {
                'selector': '.blue',
                'style': {
                    'background-color': 'blue',
                    'line-color': 'blue'
                }
            },
            {
                'selector': '.green',
                'style': {
                    'background-color': 'green',
                    'line-color': 'green'
                }
            },
            {
                'selector': '.black',
                'style': {
                    'background-color': 'black',
                    'line-color': 'black'
                }
            },
            {
                'selector': '.purple',
                'style': {
                    'background-color': 'purple',
                    'line-color': 'purple'
                }
            }
        ]
    ),
], style={'margin' : '20px'})

@app.callback(Output('cytoscape', 'layout'),
                  Input('dropdown-update-layout', 'value'))
def update_layout(layout):
    return {
        'name': layout,
        'animate': True
    }

@app.callback(
    Output(component_id='my-date-picker-range-div', component_property='style'),
   [Input(component_id='corr-dropdown', component_property='value')])

def show_hide_element(value):
    if value == 'Dynamic Time Warping':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
              Input('cytoscape', 'mouseoverEdgeData'))
def displayTapNodeData(data):
    if data:
        return f"Correlation between {data['source']} and {data['target']} = {'%.5f'%(data['weight'])}"
    else:
        return ""


@app.callback(
    Output('line-chart', 'figure'),
    Input('asset-select', 'value'))
def update_figure(selected_asset):
    fig = go.Figure()
    for x in selected_asset:
        forecast = read_data(x)
        forecast.reset_index(inplace=True) 
        fig.add_trace(go.Scatter(x=df["Date"], y=df[x],mode='lines',name=f"Historical-{x}"))
        fig.add_trace(go.Scatter(x=forecast["Date"], y=forecast["prediction"],mode='lines',name=f"Forecasted-{x}"))
    fig.update_layout(title='Asset Forecasting',
                        xaxis_title='Date',
                        yaxis_title='Asset Price')
    return fig

@app.callback(
    Output('cytoscape', 'elements'),
    Input('asset-select', 'value'),
    Input('corr-dropdown', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
    )
def update_elements(asset_name,corr_method,start_date,end_date):
    

    final_dict_list = []
    if corr_method == 'Pearson':
        edges = pd.read_csv("./data/pearsonCorrEdges.csv")
    elif corr_method == 'Spearman':
        edges = pd.read_csv("./data/spearmanCorrEdges.csv")
    elif corr_method == 'Kendall':
        edges = pd.read_csv("./data/kendallCorrEdges.csv")
    elif corr_method == 'Dynamic Time Warping':
        edges = pd.read_csv("./data/kendallCorrEdges.csv")


    for asset in asset_name:

        asset_edges = None
        if corr_method == 'Dynamic Time Warping':
            if start_date is None or end_date is None:
                raise PreventUpdate
            dat1 = start_date
            dat2 = end_date
            asset_edges = dTimeWarp(dat1,dat2,asset,data,c,edges)
            color_dict = {}
            temp_dict = {}
            color_list = ["red", "blue", "green", "purple", "white", "red", "red", "red"]
            i = 0

            if ":" in asset:
                color = asset[-2:]
            else:
                color = "commodity"
                
            for edge in asset_edges:
                temp = ""
                if ":" in edge[0]:
                    temp = edge[0][-2:]
                else:
                    temp = "commodity"

                if temp in temp_dict:
                    if temp_dict[temp] == 3:
                        continue
                    temp_dict[temp] += 1
                else:
                    temp_dict[temp] = 1
                    color_dict[temp] = color_list[i]
                    i += 1
                
                final_dict_list.append({'data': {'id': edge[0], 'label': edge[0],'style': {'color':'white'}}, 'classes': color_dict[temp]})
                final_dict_list.append({'data': {'source': asset, 'target': edge[0], 'weight': edge[1]}})
                final_dict_list.append({'data': {'id': asset, 'label': asset,'style': {'color':'white'}}, 'classes': color_dict[color]})
        else:
            asset_edges = edges.loc[edges['asset_1'] == asset]
            asset_edges = asset_edges.sort_values(by=['correlation'], ascending=False)
            temp_dict = {}
            color_dict = {}
            color_list = ["red", "blue", "green", "purple", "white", "red", "red", "red"]
            i = 0

            color = None

            if ":" in asset:
                color = asset[-2:]
            else:
                color = "commodity"
            
            for index, row in asset_edges.iterrows():
                
                temp = ""

                if ":" in row["asset_2"]:
                    temp = row["asset_2"][-2:]
                else:
                    temp = "commodity"
                if temp in temp_dict:
                    if temp_dict[temp] == 3:
                        continue
                    temp_dict[temp] += 1
                else:
                    temp_dict[temp] = 1
                    color_dict[temp] = color_list[i]
                    i += 1
                
                final_dict_list.append({'data': {'id': row['asset_2'], 'label': row['asset_2']}, 'classes': color_dict[temp]})
                final_dict_list.append({'data': {'source': asset, 'target': row['asset_2'], 'weight': row['correlation']}})
                if color != color_dict.keys():
                    final_dict_list.append({'data': {'id': asset, 'label': asset,'style': {'color':'white'}}, 'classes': 'red'})
                else:
                    final_dict_list.append({'data': {'id': asset, 'label': asset,'style': {'color':'white'}}, 'classes': color_dict[color]})

    return final_dict_list

if __name__ == '__main__':
    app.run_server(debug=True)