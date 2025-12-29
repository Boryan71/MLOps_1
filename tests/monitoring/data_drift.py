import pandas as pd
from evidently import Report
from evidently import Dataset
from evidently import DataDefinition
from evidently.presets import DataDriftPreset, DataSummaryPreset
import os


# Загружаем базовые данные
reference_data = pd.read_csv(os.path.abspath("data/raw/UCI_Credit_Card.csv"))

# Загружаем новые данные
current_data = pd.read_csv(os.path.abspath("data/raw/UCI_Credit_Card_new.csv"))

# Определяем запуск только из скрипта
if __name__ == "__main__":
    # Создаем отчет о дрифте данных
    report = Report(metrics=[
        DataDriftPreset()
    ])
    snapshot = report.run(reference_data, current_data)
    snapshot.save_html("report.html")
    
    data_drift = snapshot.dict()["metrics"][0]["value"]["share"]
    
    if data_drift >= 0.5:
        print(f"Обнаружен дрифт данных, общее смещение: {data_drift}, допустимая граница: 0.5")
    else: print(f"Дрифт данных не обнаружен, общее смещение: {data_drift}, допустимая граница: 0.5")
    os.system("report.html")