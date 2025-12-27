import numpy as np
import pandas as pd
import os
import sys
import subprocess
from datetime import datetime, timedelta
sys.path.append(os.path.abspath("."))
from src.data.make_dataset import load_data


# Создадим функцию для рассчета PSI
def calculate_psi(expected, actual):
    # Определяем количество бинов 
    bins = len(set(expected))
    
    # Создадим единый список бинов для обоих наборов данных
    _, cut_points = pd.qcut(pd.concat([expected, actual]), q=bins, retbins=True, duplicates="drop")
    
    # Получим категориальный тип данных с общими границами бинов
    expected_bins = pd.cut(expected, bins=cut_points, include_lowest=True)
    actual_bins = pd.cut(actual, bins=cut_points, include_lowest=True)
    
    # Подсчитаем и нормализуем частоту появления значений в каждом бине
    exp_counts = expected_bins.value_counts(normalize=True, sort=False)
    act_counts = actual_bins.value_counts(normalize=True, sort=False)
    
    # Рассчитываем PSI
    psi_value = ((exp_counts - act_counts) * np.log(exp_counts / act_counts)).sum()
    return psi_value


# Определяем запуск только из скрипта
if __name__ == "__main__":
    # Определим данные
    # За новый набор возмём 1% от тестовых данных (определно вручную, для наличия хоть сколько-нибудь значимого дрифта)
    path = os.path.abspath("data/raw/UCI_Credit_Card.csv")
    old_path = f"{path}_{datetime.today().date() - timedelta(days=1)}"
    
    df_old = load_data(path)
    df_new = df_old.sample(frac=0.01, random_state=42)

    # Выбираем признак, по которому будем рассчитывать PSI
    df_expected = df_old['AGE']
    df_actual = df_new['AGE']
    
    # Рассчитываем PSI
    psi_result = calculate_psi(df_expected, df_actual)
    print("PSI:", psi_result)
    
    # Если метрика PSI > 0.1, определим это как значимый дрифт и переобучим модель с переподнятием контейнера приложения
    if psi_result > 0.1:
        # Переименовывем старый набор и сохраняем новый
        os.rename(path, old_path)
        print(f"Старый набор данных сохранен под именем {old_path}")
        df_new.to_csv(path, index=False)
        print(f"Новый набор данных сохранен под именем {path}")

        # Запускаем DVC-пайплайн для обработки новых данных и сборки новой модели
        output = subprocess.check_output("dvc repro -f", text=True, shell=True)
        print(output)
        output = subprocess.check_output("docker-compose up --build", text=True, shell=True)
        print(output)
        






