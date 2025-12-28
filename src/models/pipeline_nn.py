import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump
import os
import tf2onnx
import onnx
import time
import onnxruntime as rt
from onnxruntime.quantization import quantize_dynamic


# Определяем запуск только из скрипта
if __name__ == "__main__":
    # Загружаем данные из CSV-файла
    data = pd.read_csv(os.path.abspath("data/raw/UCI_Credit_Card.csv"))
    
    # Выбираем признаки и целевую переменную
    features = data.drop(columns=['ID', 'default.payment.next.month'])
    target = data['default.payment.next.month']
    
    # Разделяем данные на тренировочную и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    
    # Нормализуем признаки
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Создаем простую нейросеть
    model = Sequential([
        Dense(32, activation='relu', input_shape=(X_train_scaled.shape[1],)),
        Dense(16, activation='relu'),
        # Бинарная классификация
        Dense(1, activation='sigmoid')
    ])

    # Компилируем модель
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    # Обучаем модель
    epoch = 5
    history = model.fit(X_train_scaled, y_train, epochs=epoch, batch_size=32, validation_split=0.2)
    
    # Проверяем качество модели на тестовых данных
    y_pred = (model.predict(X_test_scaled) > 0.5).astype(int)
    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))

    # Сохраняем модель в формате pkl
    model_file = os.path.abspath("models/NN.pkl")
    dump(model, model_file)
    print(f"Модель PKL успешно создана в {model_file}")

    # Экспортируем модель в формат ONNX
    onnx_model_file = os.path.abspath("models/NN.onnx")
    onnx_model, _ = tf2onnx.convert.from_keras(model, output_path=onnx_model_file)
    print(f"Модель ONNX успешно создана в {onnx_model_file}")

    # Сравним показатели
    # Измеряем время инференса обычной модели
    # Количество проверок
    cnt_reload = 10
    start_time = time.time()
    for _ in range(cnt_reload):
        predictions = model.predict(X_test_scaled)
    inference_time_original = (time.time() - start_time) / cnt_reload
    print(f"Среднее время инференса оригинальной модели: {inference_time_original:.5f} секунд.")

    # Загружаем сессию ONNX Runtime
    session = rt.InferenceSession(onnx_model_file)
    input_name = session.get_inputs()[0].name
    
    # Измеряем время инференса ONNX-модели
    start_time_onnx = time.time()
    for _ in range(cnt_reload):
        onnx_predictions = session.run(None, {input_name: X_test_scaled.astype(np.float32)})
    inference_time_onnx = (time.time() - start_time_onnx) / cnt_reload
    print(f"Среднее время инференса ONNX-модели: {inference_time_onnx:.5f} секунд.")

    # Проверка сходимости
    # Предсказываем оригиналом
    original_predictions = model.predict(X_test_scaled)
    
    # Предсказываем через ONNX
    onnx_predictions = session.run(None, {input_name: X_test_scaled.astype(np.float32)})[0]
    
    # Сравниваем результаты
    mse_error = np.mean((original_predictions - onnx_predictions)**2)
    print(f"Средняя квадратичная ошибка между двумя версиями модели: {mse_error}")
    
    if mse_error < 1e-6:
        print("Модели успешно конвертированы и работают одинаково.")
    else:
        print("Ошибка превышает допустимый порог, возможно проблема с конвертацией.")

    # Выполняем квантизацию модели
    onnx_quantized_model_file = os.path.abspath('models/NN_quant.onnx')
    quantize_dynamic(onnx_model_file, onnx_quantized_model_file)

    # Сравним показатели
    print(f"Среднее время инференса ONNX: {inference_time_onnx:.5f} секунд.")

    # Загружаем сессию ONNX Quant
    session = rt.InferenceSession(onnx_quantized_model_file)
    input_name = session.get_inputs()[0].name
    
    # Измеряем время инференса ONNX
    start_time_onnx = time.time()
    for _ in range(cnt_reload):
        onnx_predictions = session.run(None, {input_name: X_test_scaled.astype(np.float32)})
    inference_time_onnx = (time.time() - start_time_onnx) / cnt_reload
    print(f"Среднее время инференса ONNX Quant: {inference_time_onnx:.5f} секунд.")