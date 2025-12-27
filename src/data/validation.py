import pandas
import os
import great_expectations as gx
from great_expectations import expectations as gxe

# Создаем контекст
context = gx.get_context()

# Загружаем датасет
df = pandas.read_csv(os.path.abspath("data/raw/UCI_Credit_Card.csv"))

# Создаем датасурс на основе датасета
data_source_name = "df"
data_source = context.data_sources.add_pandas(name=data_source_name)

# Создаем дата_ассет для нашего датасурса
data_asset_name = "df_asset"
data_asset = data_source.add_dataframe_asset(name=data_asset_name)

# Создаем батч для дата_ассета
batch_definition_name = "df_batch_definition"
batch_definition = data_asset.add_batch_definition_whole_dataframe(
    batch_definition_name
)

# Задаем параметры батча
batch_parameters = {"dataframe": df}

# Получаем датафрейм как батч
batch = batch_definition.get_batch(batch_parameters=batch_parameters)

# Создаем сьют для проверок
suite_name = "df_expectation_suite"
suite = gx.ExpectationSuite(name=suite_name)
suite = context.suites.add(suite)

# Создаем правила для проверки
expectations = [
    gxe.ExpectColumnToExist(column="LIMIT_BAL"),
    gxe.ExpectColumnValuesToNotBeNull(column="LIMIT_BAL"),
    gxe.ExpectColumnValuesToBeBetween(column="AGE", max_value=100, min_value=18),
    gxe.ExpectColumnDistinctValuesToBeInSet(
        column="default.payment.next.month", value_set=[0, 1]
    ),
]

for exp in expectations:
    suite.add_expectation(exp)

# Определяем валидирующий объект
definition_name = "df_validation_definition"
validation_definition = gx.ValidationDefinition(
    data=batch_definition, suite=suite, name=definition_name
)

# Добавляем валидацию в контекст
validation_definition = context.validation_definitions.add(validation_definition)

# Производим валидацию
validation_results = validation_definition.run(batch_parameters=batch_parameters)

if validation_results.success:
    print("Все проверки пройдены")
else:
    raise ValueError(
        f"""
Статус проверки: {validation_results.success}\n
{validation_results}
"""
    )
