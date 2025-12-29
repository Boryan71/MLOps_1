# 1 этап
# Устанавливаем зависимости и подготовку окружения
FROM python:3.11-rc-slim-buster AS base

WORKDIR /app

COPY requirements.txt .

# Установим зависимости глобально
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

#######################################
# 2 этап
# Получение обработанных данных и модели через DVC
FROM base AS dvc_stage

WORKDIR /app

# Копируем исходники
COPY . .

# Загружаем данные и проверяем этапы репроцессинга
RUN dvc pull
RUN dvc repro

######################################
# 3 этап
# Финальный контейнер с приложением FastAPI
FROM dvc_stage AS final

WORKDIR /app

# Создаем каталог для логов
RUN mkdir -p /logs

# Перемещаем нужные компоненты из предыдущих слоев
COPY --from=dvc_stage /app/src ./src
COPY --from=dvc_stage /app/models/NN_quant.onnx ./models/NN_quant.onnx
COPY data ./data

# Открываем порт 8000 для внешнего доступа
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]