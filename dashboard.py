import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import subprocess
import re
import csv
from datetime import datetime

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Bitcoin Price Dashboard", style={"textAlign": "center", "color": "#2c3e50"}),
        html.Div(id="live-update-text", style={"textAlign": "center", "color": "#2980b9", "fontSize": 24}),
        dcc.Graph(id="live-update-graph"),
        html.Div(id="daily-report", style={"textAlign": "center"}),
        dcc.Interval(
            id="interval-component",
            interval=30 * 1000,  # update every 30 seconds
            n_intervals=0
        )
    ],
    style={"backgroundColor": "#34495e", "padding": "20px", "borderRadius": "10px"}
)

x_values = []
y_values = []
daily_metrics = {}

@app.callback(
    [Output("live-update-text", "children"), Output("live-update-graph", "figure"), Output("daily-report", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    global daily_metrics

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
        "line": {"color": "#e74c3c", "width": 2.5},
        "name": "Price",
        "marker": {"color": "#e74c3c", "size": 8}
    }

    # Update the daily report once every 24 hours (i.e., every 288 intervals, where each interval is 5 minutes)
    if n % 288 == 0:
        daily_metrics = {
            "volatility": 0.02,
            "open": 10000,
            "close": 11000,
            "evolution": 0.1
        }
    # Create a table to display the daily metrics
    table_rows = [
        html.Tr([html.Td(metric.capitalize(), style={"padding": "5px"}), html.Td(str(value), style={"padding": "5px"})]) for metric, value in daily_metrics.items()
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
    app.run_server(debug=True,host='0.0.0.0')
    

