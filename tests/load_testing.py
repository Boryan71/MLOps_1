import time
import numpy as np
import onnxruntime as rt
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# Функция для вычисления задержки
def measure_latency(session, inputs, iterations=100):
    times = []
    for _ in range(iterations):
        start_time = time.time()
        session.run(None, inputs)
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
    avg_latency = sum(times) / len(times)
    return avg_latency

# Функция для вычисления пропускной способности
def measure_throughput(session, inputs, duration_seconds=10):
    count = 0
    start_time = time.time()
    while True:
        session.run(None, inputs)
        count += 1
        current_time = time.time()
        if current_time - start_time >= duration_seconds:
            break
    throughput = count / duration_seconds
    return throughput

# Загружаем данные из CSV-файла
data = pd.read_csv(os.path.abspath("data/raw/UCI_Credit_Card.csv"))

# Выбираем признаки и целевую переменную
features = data.drop(columns=["ID", "default.payment.next.month"])
target = data["default.payment.next.month"]

# Разделяем данные на тренировочную и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Нормализуем признаки
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Задаем типы инстансов
# На локальном компьютере есть возможность тестирования только на CPU, однако оставлю для возможного тестирования в другой среде
test_cases = [
    {"type": "cpu"},
    {"type": "gpu"}
]

results = {}

# Путь к модели
model_path = os.path.abspath("models/NN_quant.onnx")

for case in test_cases:
    device = case["type"]
    print(f"Тестирование инференса на {device.upper()}.")
    
    # Создаем сесисю
    sess_options = rt.SessionOptions()
    providers = ["CPUExecutionProvider"] if device == "cpu" else ["CUDAExecutionProvider"]
    session = rt.InferenceSession(model_path, sess_options=sess_options, providers=providers)
    input_name = session.get_inputs()[0].name
    
    # Задаем случайные данные для тестирования
    sample_size = 3000
    random_indices = np.random.choice(X_test_scaled.shape[0], size=sample_size, replace=False)
    random_chunk = X_test_scaled[random_indices].astype(np.float32)
    
    latency = measure_latency(session, {input_name: random_chunk}, iterations=100)
    throughput = measure_throughput(session, {input_name: random_chunk}, duration_seconds=10)
    
    results[device] = {
        "latency": latency,
        "throughput": throughput
    }

# Статистика
for key, value in results.items():
    print(f"{key}: Задержка: {value['latency']:.4f} сек, Пропускная способность: {value['throughput']:.2f} запросов/сек")