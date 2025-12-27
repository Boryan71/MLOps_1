import pandas as pd
import os
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler


raw_path = os.path.abspath("data/raw/UCI_Credit_Card.csv")
processed_path = os.path.abspath("data/processed/preprocessed_data.csv")


# Создаем функцию для загрузки датасета
def load_data(data_path=raw_path):
    df = pd.read_csv(data_path)
    return df


# Создадим функцию, которая будет производить разведывательный анализ датасета
def explore_data(df):
    # Находим количсество пропусков в данных
    print("Количество пропусков:")
    print(df.isna().sum())

    # Оцениваем процентное распределение целевой переменной
    target_distribution = (
        df["default.payment.next.month"].value_counts(normalize=True) * 100
    )
    print("\nРаспределение целевой переменной (%):")
    print(target_distribution)

    # Выводим статистику по числовым признакам
    numeric_columns = df.select_dtypes(include=["float", "int"]).columns
    print("\nСтатистика по числовым признакам:")
    print(df[numeric_columns].describe())

    # Выведем значения категориальных признаков
    categorical_columns = df.select_dtypes(exclude=["float", "int"]).columns
    if len(categorical_columns) > 0:
        print("\nКатегоричные признаки:")
        for col in categorical_columns:
            print(f"{col}: {df[col].unique()}")


# Создадим функцию, которая будет предобрабатывать данные
def preprocess_data(df):
    # Удаляем столбец ID
    df.drop(columns=["ID"], inplace=True)

    # Производим биннинг возраста
    bins = [20, 30, 40, 50, float("inf")]
    labels = ["Молодые", "Средний возраст", "Взрослые", "Старшие"]
    df["AGE_GROUP"] = pd.cut(df["AGE"], bins=bins, labels=labels)

    # Выполняем OHE-обработку категориальных признаков
    cat_cols = ["SEX", "MARRIAGE", "EDUCATION"]
    df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    # Нормализуем числовые признаки
    scaler = MinMaxScaler()
    num_cols = (
        ["LIMIT_BAL"]
        + [f"BILL_AMT{i}" for i in range(1, 7)]
        + [f"PAY_AMT{i}" for i in range(1, 7)]
    )
    df_scaled = scaler.fit_transform(df_encoded[num_cols])
    df_encoded[num_cols] = df_scaled

    return df_encoded


# Определяем запуск только из скрипта
if __name__ == "__main__":
    # Посмотрим на наш датасет
    df = load_data()
    print(f"Размер таблицы: {df.shape}")
    print("Первые строки:")
    print(df.head())
    print("Типы данных:")
    print(df.dtypes)

    # Выполняем анализ датасета
    explore_data(df)

    # Обрабатываем данные и сохраняем датасет
    df_processed = preprocess_data(df)
    output_path = Path(processed_path)
    df_processed.to_csv(output_path, index=False)
    print(f"\nДанные успешно сохранены в {output_path}.")
