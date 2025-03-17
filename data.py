import pandas as pd
import joblib
from pycaret.regression import predict_model

# ข้อมูลสำหรับสถานีเทศบาลนครหาดใหญ่ แยกโรงแรมวีแอล
pm25_data = {
    "location": "สถานีเทศบาลนครหาดใหญ่ แยกโรงแรมวีแอล",
    "pm25": 3.7,
    "unit": "มก./ลบ.ม.",
    "latitude": 7.0084,  # ละติจูดของหาดใหญ่
    "longitude": 100.4767  # ลองจิจูดของหาดใหญ่
}


# สร้าง DataFrame จากข้อมูล
df_pm25 = pd.DataFrame([pm25_data])

# โหลดโมเดล
def load_models():
    model_pm = joblib.load("D:/project-term/modelPM/model_PM25.pkl")
    model_temp = joblib.load("D:/project-term/modelPM/model_temperature.pkl")
    model_humidity = joblib.load("D:/project-term/modelPM/model_humidity.pkl")
    return model_pm, model_temp, model_humidity

# โหลดข้อมูล
def load_data():
    future_pm = pd.read_csv("D:/project-term/pm_2.5/future_pm_data_14days.csv")
    future_temp = pd.read_csv("D:/project-term/pm_2.5/future_temperature_data_14days.csv")
    future_humidity = pd.read_csv("D:/project-term/pm_2.5/future_humidity_data_14days.csv")

    # แปลง datetime
    for df in [future_pm, future_temp, future_humidity]:
        df["datetime"] = pd.to_datetime(df["datetime"])

    return future_pm, future_temp, future_humidity

# พยากรณ์ค่า
def predict_data(model_pm, model_temp, model_humidity, future_pm, future_temp, future_humidity):
    future_pm["predicted_pm2_5"] = predict_model(model_pm, data=future_pm)["prediction_label"]
    future_temp["predicted_temperature"] = predict_model(model_temp, data=future_temp)["prediction_label"]
    future_humidity["predicted_humidity"] = predict_model(model_humidity, data=future_humidity)["prediction_label"]
    return future_pm, future_temp, future_humidity