from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# Подгружаем модель
MODEL_PATH = "models/LinearRegr.pkl"
model = joblib.load(MODEL_PATH)


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

app = FastAPI()

@app.post("/predict/")
async def predict_multiple_clients(input_data: MultipleClients):
    try:
        # Формируем датафрейм из списка клиентов
        df = pd.DataFrame([client.dict() for client in input_data.clients])
        
        # Прогоняем модель и собираем прогнозы
        predictions = model.predict_proba(df)[:, 1]
        
        # Возвращаем список вероятностей дефолта для каждого клиента
        return [
            {"client_id": idx, "default_probability": f"{prob * 100:.2f}%"} 
            for idx, prob in enumerate(predictions)
        ]
    
    except Exception as e:
        return {"error": str(e)}
