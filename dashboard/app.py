import redis
import json
import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html
import os

REDIS_IP = os.getenv('REDIS_IP', '0.0.0.0')

redis_client = redis.StrictRedis(host=REDIS_IP, port=6379, decode_responses=True)

def get_redis_data():
    data = redis_client.get('lucascarvalho-proj3-output')
    if data:
        return json.loads(data)
    return {}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Dashboard de Monitoramento'),
    dcc.Interval(
        id='interval-component',
        interval=10000,  
        n_intervals=0
    ),
    dcc.Graph(id='cpu-usage-graph'),
    dcc.Graph(id='memory-usage-graph'),
    dcc.Graph(id='network-usage-graph')
])

@app.callback(
    [dash.dependencies.Output('cpu-usage-graph', 'figure'),
     dash.dependencies.Output('memory-usage-graph', 'figure'),
     dash.dependencies.Output('network-usage-graph', 'figure')],
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    data = get_redis_data()

    if not data:
        return dash.no_update, dash.no_update, dash.no_update

    # CPU
    cpu_data = {k: v for k, v in data.items() if 'cpu_percent' in k}
    cpu_df = pd.DataFrame({'CPU Core': list(cpu_data.keys()), 'Utilização (%)': list(cpu_data.values())})
    cpu_fig = px.bar(cpu_df, x='CPU Core', y='Utilização (%)', title='CPU usage per core')
    cpu_fig.update_yaxes(range=[0, 100])

    # Memory
    memory_data = {k: v for k, v in data.items() if 'memory' in k}
    memory_df = pd.DataFrame({'Métrica': list(memory_data.keys()), 'Valor (%)': list(memory_data.values())})
    memory_fig = px.bar(memory_df, x='Métrica', y='Valor (%)', title='Percentage of memory caching content')
    memory_fig.update_yaxes(range=[0, 100])

    # Network
    network_data = {k: v for k, v in data.items() if 'network' in k}
    network_df = pd.DataFrame({'Métrica': list(network_data.keys()), 'Valor (%)': list(network_data.values())})
    network_fig = px.bar(network_df, x='Métrica', y='Valor (%)', title='Percentage of outgoing traffic bytes')
    network_fig.update_yaxes(range=[0, 100])

    return cpu_fig, memory_fig, network_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
