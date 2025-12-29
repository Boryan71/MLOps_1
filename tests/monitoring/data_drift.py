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

# Создаем отчет о дрифте данных
report = Report(metrics=[
    DataDriftPreset()
])
snapshot = report.run(reference_data, current_data)
snapshot.save_html("report.html")

print(snapshot.dict())
os.system("report.html")