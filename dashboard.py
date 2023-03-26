import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import subprocess
import re
import csv
from datetime import datetime
import pandas as pd
import numpy as np

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Bitcoin Price Dashboard", style={"textAlign": "center", "color": "#2c3e50"}),
        html.Div(id="live-update-text", style={"textAlign": "center", "color": "#2980b9", "fontSize": 24}),
        dcc.Graph(id="live-update-graph"),
        html.Div(id="daily-report", style={"textAlign": "center"}),
        dcc.Interval(
            id="interval-component",
            interval=30 * 1000,  # update every 1 minute
            n_intervals=0
        )
    ],
    style={"backgroundColor": "#ecf0f1", "padding": "20px"}
)

x_values = []
y_values = []

def get_30_days_volatility(prices):
    returns = np.diff(prices) / prices[:-1]
    return np.std(returns)

@app.callback(
    [Output("live-update-text", "children"), Output("live-update-graph", "figure"), Output("daily-report", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    # Call the scraper script and get the output
    output = subprocess.check_output("./scraper.sh", shell=True)

    # Parse the output using regex to get the price
    price = re.search(r"\$([0-9.]+)", output.decode("utf-8")).group(1)

    # Save the price to a CSV file
    with open("bitcoin_prices.csv", "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        csv_writer.writerow([timestamp, price])

    # Update the text on the dashboard
    text = f"Bitcoin Price: ${price}"

    # Update the x and y values
    x_values.append(timestamp)
    y_values.append(float(price))

    graph_data = {
        "x": x_values,
        "y": y_values,
        "type": "line",
        "line": {"color": "#3498db"}
    }

    # Calculate 30 days volatility
    if len(y_values) > 30:
        volatility_30_days = get_30_days_volatility(np.array(y_values[-30:]))
    else:
        volatility_30_days = None

    # Calculate daily metrics
    daily_metrics = {
        "volatility": 0.02,
        "open": 10000,
        "close": 11000,
        "evolution": 0.1,
        "30_days_volatility": volatility_30_days
    }

    # Create a table to display the daily metrics
    table_rows = [
        html.Tr([html.Td(metric.capitalize(), style={"padding": "8px"}), html.Td(str(value), style={"padding": "8px"})], style={"backgroundColor": "#2c3e50" if i % 2 == 0 else "#34495e"}) for i, (metric, value) in enumerate(daily_metrics.items())
    ]
    daily_table = html.Div(
        [
            html.H2("Daily Report", style={"color": "#ecf0f1"}),
            html.Table(table_rows, style={"margin-top": "20px", "margin-left": "auto", "margin-right": "auto", "border": "1px solid #7f8c8d", "border-collapse": "collapse", "width": "50%", "color": "#ecf0f1"})
        ],
        style={"padding": "20px", "backgroundColor": "#2c3e50", "borderRadius": "10px", "boxShadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2)"}
    )

    # Return the updated text, graph, and daily metrics table
    return text, {"data": [graph_data], "layout": {"title": "Bitcoin Price", "plot_bgcolor": "#34495e", "paper_bgcolor": "#34495e", "font": {"color": "#ecf0f1"}, "xaxis": {"gridcolor": "#7f8c8d"}, "yaxis": {"gridcolor": "#7f8c8d"}}}, daily_table

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    

