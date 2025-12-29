# 1 этап 
# Устанавливаем зависимости и подготовка окружения
FROM python:3.11-rc-slim-buster AS base

WORKDIR /app

COPY requirements.txt .

RUN pip install --user --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

#########################################
# 2 этап
# Получение обработанных данных и модели через DVC
FROM base AS dvc_stage

WORKDIR /app

COPY --from=base /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Копируем файлы DVC
COPY . .

# Запускаем DVC pull для загрузки обработанных данных и проверки
RUN dvc pull
RUN dvc repro

########################################
# 3 этап 
# Запускаем приложение FastApi
FROM python:3.11-rc-slim-buster AS final

WORKDIR /app

# Создаем каталог для логов
RUN mkdir -p /logs

# Копируем приложение и предварительно подготовленные данные/модели из предыдущего этапа
COPY --from=base /root/.local /root/.local
COPY --from=dvc_stage /app/src ./src
COPY --from=dvc_stage /app/models/NN_quant.onnx ./models/NN_quant.onnx

ENV PATH=/root/.local/bin:$PATH
# Открываем порт 8000 для внешнего доступа
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]