import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
from data import df_pm25, load_models, load_data, predict_data
import pandas as pd

# โหลดโมเดลและข้อมูล
model_pm, model_temp, model_humidity = load_models()
future_pm, future_temp, future_humidity = load_data()
future_pm, future_temp, future_humidity = predict_data(model_pm, model_temp, model_humidity, future_pm, future_temp, future_humidity)

# สร้างแอป Dash
app = dash.Dash(__name__)

# สไตล์สำหรับ Sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "20px",
    "background-color": "#222",
    "color": "white",
    "overflow-y": "auto",
    "transition": "margin-left 0.5s"
}

# สไตล์สำหรับเนื้อหาหลัก
CONTENT_STYLE = {
    "margin-left": "22%",
    "padding": "20px",
    "transition": "margin-left 0.5s"
}

# สไตล์สำหรับปุ่มเก็บ Sidebar
TOGGLE_BUTTON_STYLE = {
    "position": "fixed",
    "top": "10px",
    "left": "22%",
    "z-index": "1000",
    "background-color": "#444",
    "color": "white",
    "border": "none",
    "padding": "10px",
    "cursor": "pointer"
}

app.layout = html.Div([
    # Sidebar
    html.Div(id="sidebar", children=[
        html.H2("ข้อมูลที่ทำนาย", style={"text-align": "center"}),
        html.Div(id="sidebar-content")
    ], style=SIDEBAR_STYLE),

    # ปุ่มเก็บ Sidebar
    html.Button("☰", id="sidebar-toggle", style=TOGGLE_BUTTON_STYLE),

    # เนื้อหาหลัก
    html.Div(id="content", children=[
        html.H1("PM2.5, Temperature & Humidity Forecast Dashboard for Hat Yai"),

        # แผนที่
        html.Div([
            html.H3("PM2.5 Forecast Map"),
            dcc.Graph(id="pm25_map"),
        ], className="container"),

        # ปุ่มกดเลื่อนแสดงกราฟ
        html.Div([
            dcc.Checklist(
                id="graph-toggle",
                options=[
                    {"label": "แสดงกราฟ PM2.5", "value": "pm25"},
                    {"label": "แสดงกราฟอุณหภูมิ", "value": "temp"},
                    {"label": "แสดงกราฟความชื้น", "value": "humidity"},
                ],
                value=["pm25", "temp", "humidity"],  # เริ่มต้นให้แสดงกราฟทั้งหมด
                inline=True,
                style={"margin-bottom": "20px"}
            ),
        ]),

        # Date Picker สำหรับเลือกวันที่
        html.Div([
            dcc.DatePickerRange(
                id="date-picker",
                min_date_allowed=future_pm["datetime"].min(),
                max_date_allowed=future_pm["datetime"].max(),
                start_date=future_pm["datetime"].min(),
                end_date=future_pm["datetime"].max(),
                display_format="YYYY-MM-DD",
                style={"margin-bottom": "20px"}
            ),
        ]),

        # กราฟ PM2.5
        html.Div(id="pm25_forecast_container", children=[
            html.H3("PM2.5 Forecast"),
            dcc.Graph(id="pm25_forecast"),
        ], className="container"),

        # กราฟอุณหภูมิ
        html.Div(id="temp_forecast_container", children=[
            html.H3("Temperature Forecast"),
            dcc.Graph(id="temp_forecast"),
        ], className="container"),

        # กราฟความชื้น
        html.Div(id="humidity_forecast_container", children=[
            html.H3("Humidity Forecast"),
            dcc.Graph(id="humidity_forecast"),
        ], className="container"),

        # ตารางแสดงข้อมูลที่ทำนายทั้งหมด
        html.Div([
            html.H3("ข้อมูลที่ทำนายทั้งหมด"),
            dash_table.DataTable(
                id="prediction-table",
                columns=[
                    {"name": "วันที่และเวลา", "id": "datetime"},
                    {"name": "PM2.5 (มก./ลบ.ม.)", "id": "predicted_pm2_5"},
                    {"name": "อุณหภูมิ (°C)", "id": "predicted_temperature"},
                    {"name": "ความชื้น (%)", "id": "predicted_humidity"}
                ],
                data=[],  # ข้อมูลจะถูกอัปเดตผ่าน Callback
                page_size=10,  # จำนวนแถวต่อหน้า
                page_action="native",  # เปิดใช้งาน Pagination
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "backgroundColor": "#222",
                    "color": "white",
                    "border": "1px solid #444"
                },
                style_header={
                    "backgroundColor": "#444",
                    "fontWeight": "bold"
                }
            )
        ], style={"margin-top": "20px"})
    ], style=CONTENT_STYLE),
])

# ฟังก์ชันสร้างกราฟเส้น
def create_forecast_figure(df, x_col, y_col, title, y_label, line_color, fill_color):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode="lines", 
        line=dict(width=3, color=line_color),
        fill="tozeroy",  # เติมสีใต้เส้น
        fillcolor=fill_color, 
        name=y_label
    ))

    fig.update_layout(
        title=title,
        xaxis_title="DateTime",
        yaxis_title=y_label,
        template="plotly_dark",
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font=dict(size=14)
    )
    
    return fig

# ฟังก์ชันสร้างแผนที่ PM2.5
def create_pm25_map(df):
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="pm25",
        size="pm25",
        hover_name="location",
        hover_data=["pm25", "unit"],
        zoom=12,
        height=500,
        title="PM2.5 Forecast Map for Hat Yai"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font=dict(color="white")
    )
    
    return fig

# Callback สำหรับควบคุมการแสดงกราฟ
@app.callback(
    [Output("pm25_forecast_container", "style"),
     Output("temp_forecast_container", "style"),
     Output("humidity_forecast_container", "style")],
    [Input("graph-toggle", "value")]
)
def toggle_graphs(selected_graphs):
    # กำหนดสไตล์การแสดงผลของแต่ละกราฟ
    pm25_style = {"display": "block"} if "pm25" in selected_graphs else {"display": "none"}
    temp_style = {"display": "block"} if "temp" in selected_graphs else {"display": "none"}
    humidity_style = {"display": "block"} if "humidity" in selected_graphs else {"display": "none"}
    return pm25_style, temp_style, humidity_style

# Callback สำหรับกรองข้อมูลตามวันที่ที่เลือกและแสดงข้อมูลใน Sidebar
@app.callback(
    [Output("pm25_forecast", "figure"),
     Output("temp_forecast", "figure"),
     Output("humidity_forecast", "figure"),
     Output("sidebar-content", "children"),
     Output("prediction-table", "data")],  # เพิ่ม Output สำหรับตาราง
    [Input("date-picker", "start_date"),
     Input("date-picker", "end_date")]
)
def update_graphs(start_date, end_date):
    # กรองข้อมูลตามวันที่ที่เลือก
    filtered_pm = future_pm[(future_pm["datetime"] >= start_date) & (future_pm["datetime"] <= end_date)]
    filtered_temp = future_temp[(future_temp["datetime"] >= start_date) & (future_temp["datetime"] <= end_date)]
    filtered_humidity = future_humidity[(future_humidity["datetime"] >= start_date) & (future_humidity["datetime"] <= end_date)]

    # สร้างกราฟ
    pm25_fig = create_forecast_figure(filtered_pm, "datetime", "predicted_pm2_5", 
                                      "PM2.5 Forecast", "PM2.5", 
                                      "#ff1493", "rgba(255, 20, 147, 0.3)")  # สีชมพูอ่อน
    temp_fig = create_forecast_figure(filtered_temp, "datetime", "predicted_temperature", 
                                      "Temperature Forecast", "Temperature (°C)", 
                                      "#ff7f0e", "rgba(255, 127, 14, 0.3)")  # สีส้มอ่อน
    humidity_fig = create_forecast_figure(filtered_humidity, "datetime", "predicted_humidity", 
                                          "Humidity Forecast", "Humidity (%)", 
                                          "#1f77b4", "rgba(31, 119, 180, 0.3)")  # สีฟ้าอ่อน

    # สร้างข้อมูลสำหรับ Sidebar
    sidebar_content = html.Div([
        html.H4("ข้อมูลที่ทำนาย"),
        html.H5("PM2.5"),
        html.P(f"ค่าเฉลี่ย: {filtered_pm['predicted_pm2_5'].mean():.2f} มก./ลบ.ม."),
        html.P(f"ค่าสูงสุด: {filtered_pm['predicted_pm2_5'].max():.2f} มก./ลบ.ม."),
        html.P(f"ค่าต่ำสุด: {filtered_pm['predicted_pm2_5'].min():.2f} มก./ลบ.ม."),
        html.H5("อุณหภูมิ"),
        html.P(f"ค่าเฉลี่ย: {filtered_temp['predicted_temperature'].mean():.2f} °C"),
        html.P(f"ค่าสูงสุด: {filtered_temp['predicted_temperature'].max():.2f} °C"),
        html.P(f"ค่าต่ำสุด: {filtered_temp['predicted_temperature'].min():.2f} °C"),
        html.H5("ความชื้น"),
        html.P(f"ค่าเฉลี่ย: {filtered_humidity['predicted_humidity'].mean():.2f} %"),
        html.P(f"ค่าสูงสุด: {filtered_humidity['predicted_humidity'].max():.2f} %"),
        html.P(f"ค่าต่ำสุด: {filtered_humidity['predicted_humidity'].min():.2f} %"),
    ])

    # สร้างข้อมูลสำหรับตาราง
    combined_data = pd.merge(filtered_pm, filtered_temp, on="datetime")
    combined_data = pd.merge(combined_data, filtered_humidity, on="datetime")
    combined_data = combined_data[["datetime", "predicted_pm2_5", "predicted_temperature", "predicted_humidity"]]

    # แปลงคอลัมน์ datetime และลบ "T"
    combined_data["datetime"] = combined_data["datetime"].astype(str).str.replace("T", " ")

    table_data = combined_data.to_dict("records")

    return pm25_fig, temp_fig, humidity_fig, sidebar_content, table_data

# Callback สำหรับเก็บ/เปิด Sidebar
@app.callback(
    [Output("sidebar", "style"),
     Output("content", "style"),
     Output("sidebar-toggle", "style")],
    [Input("sidebar-toggle", "n_clicks")],
    [dash.dependencies.State("sidebar", "style"),
     dash.dependencies.State("content", "style"),
     dash.dependencies.State("sidebar-toggle", "style")]
)
def toggle_sidebar(n_clicks, sidebar_style, content_style, toggle_style):
    if n_clicks is None:
        return sidebar_style, content_style, toggle_style

    if sidebar_style.get("margin-left", "0px") == "0px":
        sidebar_style["margin-left"] = "-20%"
        content_style["margin-left"] = "2%"
        toggle_style["left"] = "2%"
    else:
        sidebar_style["margin-left"] = "0px"
        content_style["margin-left"] = "22%"
        toggle_style["left"] = "22%"

    return sidebar_style, content_style, toggle_style

@app.callback(dash.Output("pm25_map", "figure"), dash.Input("pm25_map", "id"))
def update_pm25_map(_):
    return create_pm25_map(df_pm25)

if __name__ == "__main__":
    app.run_server(debug=True)