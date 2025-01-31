import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import subprocess

app = dash.Dash(__name__)

# Function to execute Asterisk commands
def run_asterisk_command(command):
    try:
        result = subprocess.run(['asterisk', '-rx', command], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return None

# Function to parse core call stats
def parse_core_call_stats():
    output = run_asterisk_command("core show calls")
    if output is None:
        return 0, 0
    lines = output.split("\n")
    active_calls, total_calls = 0, 0
    for line in lines:
        if "active call" in line:
            active_calls = int(line.split()[0])
        if "calls processed" in line:
            total_calls = int(line.split()[0])
    return active_calls, total_calls

# Function to parse PJSIP channel stats
def parse_pjsip_channelstats():
    output = run_asterisk_command("pjsip show channelstats")
    if output is None or "No objects found" in output:
        return pd.DataFrame()
    lines = output.split("\n")
    data = []
    for line in lines[3:]:  # Skip headers
        parts = line.split()
        if len(parts) >= 10:
            data.append({
                "ChannelId": parts[1],
                "Recv Count": int(parts[4]),
                "Lost Pct": float(parts[6]),
                "Recv Jitter": float(parts[7]),
                "Trans Count": int(parts[8]),
                "Trans Jitter": float(parts[11])
            })
    return pd.DataFrame(data)

# Function to parse PJSIP endpoints
def parse_pjsip_endpoints():
    output = run_asterisk_command("pjsip show endpoints")
    if output is None:
        return pd.DataFrame()
    lines = output.split("\n")
    endpoints = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[0] != "Endpoint:":
            endpoints.append({
                "Endpoint": parts[0],
                "State": parts[1]
            })
    return pd.DataFrame(endpoints)

app.layout = html.Div([
    html.H1("Asterisk Monitoring Dashboard"),
    html.Div(id="total-active-calls"),
    html.Div(id="total-calls-processed"),
    dcc.Graph(id="channel-stats"),
    dcc.Graph(id="endpoint-status"),
    dcc.Graph(id="jitter-analysis"),
    dcc.Graph(id="packet-loss-analysis"),
    dcc.Graph(id="trans-recv-analysis"),
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
])

@app.callback(
    [Output("total-active-calls", "children"),
     Output("total-calls-processed", "children"),
     Output("channel-stats", "figure"),
     Output("endpoint-status", "figure"),
     Output("jitter-analysis", "figure"),
     Output("packet-loss-analysis", "figure"),
     Output("trans-recv-analysis", "figure")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    active_calls, total_calls = parse_core_call_stats()
    df_stats = parse_pjsip_channelstats()
    df_endpoints = parse_pjsip_endpoints()
    
    if df_stats.empty and df_endpoints.empty:
        return f"Active Calls: {active_calls}", f"Total Calls Processed: {total_calls}", {}, {}, {}, {}, {}
    
    # Bar chart for PJSIP channel statistics
    fig_stats = {
        "data": [
            go.Bar(x=df_stats["ChannelId"], y=df_stats.get("Recv Count", []), name="Recv Count", marker=dict(color='blue')),
            go.Bar(x=df_stats["ChannelId"], y=df_stats.get("Trans Count", []), name="Trans Count", marker=dict(color='red'))
        ],
        "layout": go.Layout(title="PJSIP Channel Stats", xaxis={"title": "ChannelId"}, yaxis={"title": "Value"})
    }
    
    # Bar chart for endpoint statuses
    fig_endpoints = {
        "data": [go.Bar(x=df_endpoints["Endpoint"], y=[1]*len(df_endpoints), text=df_endpoints["State"], name="Endpoint Status")],
        "layout": go.Layout(title="PJSIP Endpoint Status", xaxis={"title": "Endpoint"}, yaxis={"title": "Status"})
    }
    
    # Line chart for jitter analysis
    fig_jitter = {
        "data": [
            go.Scatter(x=df_stats["ChannelId"], y=df_stats.get("Recv Jitter", []), mode='lines+markers', name="Recv Jitter", line=dict(color='green')),
            go.Scatter(x=df_stats["ChannelId"], y=df_stats.get("Trans Jitter", []), mode='lines+markers', name="Trans Jitter", line=dict(color='orange'))
        ],
        "layout": go.Layout(title="Jitter Analysis", xaxis={"title": "ChannelId"}, yaxis={"title": "Jitter (ms)"})
    }
    
    # Line chart for packet loss analysis
    fig_packet_loss = {
        "data": [
            go.Scatter(x=df_stats["ChannelId"], y=df_stats.get("Lost Pct", []), mode='lines+markers', name="Packet Loss %", line=dict(color='red'))
        ],
        "layout": go.Layout(title="Packet Loss Analysis", xaxis={"title": "ChannelId"}, yaxis={"title": "Loss Percentage (%)"})
    }
    
    # Line chart for transmitted and received packets per minute
    fig_trans_recv = {
        "data": [
            go.Scatter(x=df_stats["ChannelId"], y=df_stats.get("Trans Count", []), mode='lines+markers', name="Trans Count", line=dict(color='blue')),
            go.Scatter(x=df_stats["ChannelId"], y=df_stats.get("Recv Count", []), mode='lines+markers', name="Recv Count", line=dict(color='green'))
        ],
        "layout": go.Layout(title="Transmitted and Received Packets Per Minute", xaxis={"title": "ChannelId"}, yaxis={"title": "Packet Count"})
    }
    
    return f"Active Calls: {active_calls}", f"Total Calls Processed: {total_calls}", fig_stats, fig_endpoints, fig_jitter, fig_packet_loss, fig_trans_recv

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)
