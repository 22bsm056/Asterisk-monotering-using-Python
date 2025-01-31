# Asterisk-monotering-using-Python

Asterisk Monitoring Dashboard

Overview

This project provides real-time monitoring of an Asterisk VoIP server using Dash and Plotly. It includes two dashboards:

Process Monitoring Dashboard - Tracks CPU, memory usage, and INVITE packets.

Call Statistics Dashboard - Displays active calls, PJSIP channel stats, jitter analysis, and packet loss.

Features

Real-time tracking of Asterisk process resource usage (CPU, Memory).

Monitoring of SIP INVITE packets and call statistics.

Live updates of PJSIP channel stats, jitter analysis, and endpoint status.

Interactive graphs powered by Dash and Plotly.

Requirements

Python 3

Asterisk VoIP server

Dash, Plotly, psutil, pandas

Installation

Clone the repository:

git clone https://github.com/yourusername/asterisk-monitor.git
cd asterisk-monitor

Install dependencies:

pip install dash plotly psutil pandas

Ensure Asterisk is running and logs are accessible.

Usage

Run the dashboards separately:

Process Monitoring Dashboard

python asterisk_dash1.py

Access at: http://127.0.0.1:8050

Call Statistics Dashboard

python asterisk_dash2.py

Access at: http://127.0.0.1:8051

Dashboards

Process Monitoring Dashboard (asterisk_dash1.py)

Tracks Asterisk CPU and memory usage.

Displays total INVITE packets and rate per second.

Call Statistics Dashboard (asterisk_dash2.py)

Shows active and total calls processed.

PJSIP channel stats with jitter, packet loss analysis.

Displays PJSIP endpoint states.

License

This project is licensed under the MIT License.

Contributors

Your Name (@yourusername)

Acknowledgments

Dash by Plotly for interactive visualizations.

Asterisk for VoIP services.

