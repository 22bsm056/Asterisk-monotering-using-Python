import psutil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from collections import deque
import time
import subprocess

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Asterisk Process Monitoring"

# Data storage for live graphs
time_data = deque(maxlen=100)  # Stores time values
cpu_data = deque(maxlen=100)   # Stores CPU usage values
memory_data = deque(maxlen=100)  # Stores memory usage values
invite_data = deque(maxlen=100)  # Stores INVITE packet count over time
invite_rate_data = deque(maxlen=100)  # Stores INVITE packets per second
prev_invite_count = [0]  # Tracks previous invite count for rate calculation

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Asterisk Process Monitoring", style={'textAlign': 'center'}),

    html.Div(id="total-invites", style={"textAlign": "center", "fontSize": "20px", "marginBottom": "20px"}),

    dcc.Graph(id="live-graph-cpu", style={'height': '300px'}),
    dcc.Graph(id="live-graph-memory", style={'height': '300px'}),
    dcc.Graph(id="live-graph-invite", style={'height': '300px'}),
    dcc.Graph(id="live-graph-invite-rate", style={'height': '300px'}),

    dcc.Interval(
        id="update-interval",
        interval=1000,  # Update every second
        n_intervals=0
    )
])

# Helper function to get total INVITE packet count
def get_total_invites():
    try:
        # Command to count INVITE packets in the log
        result = subprocess.run(
            ["grep", "INVITE\\|180 Ringing\\|200 OK", "/var/log/asterisk/full"],
            stdout=subprocess.PIPE,
            text=True
        )
        return len(result.stdout.splitlines())
    except Exception as e:
        return 0

# Callback to update graphs
@app.callback(
    [Output("live-graph-cpu", "figure"),
     Output("live-graph-memory", "figure"),
     Output("live-graph-invite", "figure"),
     Output("live-graph-invite-rate", "figure"),
     Output("total-invites", "children")],
    [Input("update-interval", "n_intervals")]
)
def update_graph(n_intervals):
    # Check for Asterisk process
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'asterisk':
            asterisk = psutil.Process(proc.info['pid'])
            time_data.append(time.strftime('%H:%M:%S'))
            cpu_data.append(asterisk.cpu_percent(interval=0.5))
            memory_data.append(asterisk.memory_info().rss / (1024 * 1024))  # Convert to MB

            # Get total INVITE packet count
            total_invites = get_total_invites()
            invite_data.append(total_invites)

            # Calculate INVITE packets per second
            invite_rate = total_invites - prev_invite_count[0]
            prev_invite_count[0] = total_invites
            invite_rate_data.append(invite_rate)

            # CPU Usage Graph
            cpu_fig = {
                'data': [{
                    'x': list(time_data),
                    'y': list(cpu_data),
                    'type': 'line',
                    'name': 'CPU Usage (%)'
                }],
                'layout': {
                    'title': 'CPU Usage Over Time',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'CPU Usage (%)'},
                    'uirevision': 'constant'  # Keep graph stable while updating
                }
            }

            # Memory Usage Graph
            memory_fig = {
                'data': [{
                    'x': list(time_data),
                    'y': list(memory_data),
                    'type': 'line',
                    'name': 'Memory Usage (MB)'
                }],
                'layout': {
                    'title': 'Memory Usage Over Time',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Memory Usage (MB)'},
                    'uirevision': 'constant'  # Keep graph stable while updating
                }
            }

            # INVITE Packets Graph
            invite_fig = {
                'data': [{
                    'x': list(time_data),
                    'y': list(invite_data),
                    'type': 'line',
                    'name': 'Total INVITE Packets'
                }],
                'layout': {
                    'title': 'Total INVITE Packets Over Time',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Number of INVITE Packets'},
                    'uirevision': 'constant'  # Keep graph stable while updating
                }
            }

            # INVITE Packets Per Second Graph
            invite_rate_fig = {
                'data': [{
                    'x': list(time_data),
                    'y': list(invite_rate_data),
                    'type': 'line',
                    'name': 'INVITE Packets Per Second'
                }],
                'layout': {
                    'title': 'INVITE Packets Per Second Over Time',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Packets Per Second'},
                    'uirevision': 'constant'  # Keep graph stable while updating
                }
            }

            # Display total INVITE packets
            total_invites_text = f"Total INVITE Packets: {total_invites}"

            return cpu_fig, memory_fig, invite_fig, invite_rate_fig, total_invites_text

    # Return empty graphs if the process is not found
    return {}, {}, {}, {}, "Asterisk process not found"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
