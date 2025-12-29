from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import onnxruntime as rt
from prometheus_client import Counter, Histogram, make_asgi_app
from starlette.responses import PlainTextResponse
import logging
import os
from data_drift_detector import DataDriftDetector


# Настройка логгирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Метрика для подсчета количества запросов
REQUEST_COUNTER = Counter('total_requests', 'Total number of incoming requests')

# Метрика для измерения времени обработки запросов
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency distribution')

# Загружаем ONNX-модель
MODEL_PATH = "models/NN_quant.onnx"
session = rt.InferenceSession(MODEL_PATH)

app = FastAPI()

# Интеграция Prometheus
prometheus_app = make_asgi_app()
app.mount("/metrics", prometheus_app)

# Определяем схему входных данных (один клиент)
class SingleClient(BaseModel):
    LIMIT_BAL: float
    SEX: int
    EDUCATION: int
    MARRIAGE: int
    AGE: int
    PAY_0: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float


# Определяем схему входных данных (список клиентов)
class MultipleClients(BaseModel):
    clients: list[SingleClient]
    
# Функция для предсказания
@REQUEST_LATENCY.time()
def predict_proba(dataframe):
    REQUEST_COUNTER.inc()
    input_data = dataframe.to_numpy().astype(np.float32)
    result = session.run(None, {"dense_input": input_data})
    logger.info("Метрика записана в Prometheus")
    return result[0].reshape(-1)

# Функция для предсказания
def predict_proba(dataframe):
    input_data = dataframe.to_numpy().astype(np.float32)
    result = session.run(None, {"dense_input": input_data})
    return result[0].reshape(-1)

@app.post("/predict/")
def predict_multiple_clients(input_data: MultipleClients):
    try:
        # Формируем датафрейм из списка клиентов
        df = pd.DataFrame([client.dict() for client in input_data.clients])

        # Прогоняем модель и получаем прогнозы
        predictions = predict_proba(df)

        # Логируем успешное предсказание
        logger.info("Прогноз выполнен успешно")

        # Возвращаем список вероятностей дефолта для каждого клиента
        return [
            {"client_id": idx, "default_probability": f"{prob * 100}%"}
            for idx, prob in enumerate(predictions)
        ]

    except Exception as e:
        logger.error(f"An error occurred during prediction: {str(e)}")
        return {"error": str(e)}

# Функция для переобучения модели
def retrain_model():
    logger.info("Начало переобучения модели...")
    os.system("python /app/src/models/pipeline_nn.py")
    logger.info("Модель переобучена успешно!")

# Функция для проверки дрифта данных
def check_data_drift():
    reference_data = pd.read_csv(os.path.abspath("data/raw/UCI_Credit_Card.csv"))
    current_data = pd.read_csv(os.path.abspath("data/raw/UCI_Credit_Card_new.csv"))

    detector = DataDriftDetector(df_prior = reference_data, df_post = current_data)
    data_drift = detector.calculate_drift()["numerical"]["AGE"]["ks_2sample_test_p_value"]
    return data_drift

# End-point для приема GET-запроса от Airflow DAG
@app.get("/check-data-drift/")
def check_data_drift_endpoint():
    data_drift_value = check_data_drift()
    logger.info(f"Доля дрифта данных: {data_drift_value}")
    return {"data_drift": data_drift_value}

# End-point для переобучения модели
@app.get("/retrain-model/")
def retrain_model_endpoint():
    retrain_model()
    return {"status": "OK"}