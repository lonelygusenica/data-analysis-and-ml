# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# %%
import plotly.express as px
import plotly.graph_objects as go

plt.style.use('seaborn-v0_8-pastel')
sns.set_palette("pink")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['axes.facecolor'] = '#fff7f9'


# %%
df_test = pd.read_csv('test.csv', parse_dates=['date'])

# %%
df_test

# %%
df_train = pd.read_csv('train.csv', parse_dates=['date'])

# %%
df_holidays = pd.read_csv('holidays_events.csv', parse_dates=['date'])

# %%
df_oil = pd.read_csv('oil.csv', parse_dates=['date'])

# %%
df_subm = pd.read_csv('sample_submission.csv')

# %%
df_stores = pd.read_csv('stores.csv')

# %%
df_trans = pd.read_csv('transactions.csv', parse_dates=['date'])

# %%
for name, df in {
    "train": df_train,
    "test": df_test,
    "stores": df_stores,
    "oil": df_oil,
    "transactions": df_trans,
    "holidays": df_holidays
}.items():
    print(f"\n{name.upper()} — shape: {df.shape}")
    display(df.head())
    print(df.info())


# %%
def check_missing(df, name):
    miss = df.isna().mean() * 100
    miss = miss[miss > 0].sort_values(ascending=False)
    if not miss.empty:
        print(f"\n{name}: есть пропуски в {len(miss)} колонках")
        display(miss)
    else:
        print(f"\n{name}: нет пропусков")

for n, d in {"train": df_train, "test": df_test, "stores": df_stores,
             "oil": df_oil, "transactions": df_trans, "holidays": df_holidays}.items():
    check_missing(d, n)



# %%
for n, d in {"train": df_train, "test": df_test}.items():
    print(f"{n}: {d.duplicated().sum()} дубликатов")

# %%
fig = px.histogram(df_train, x="sales", nbins=100, color_discrete_sequence=["#ff8fab"])
fig.update_layout(
    title="Распределение продаж",
    xaxis_title="Sales",
    yaxis_title="Количество наблюдений",
    plot_bgcolor="#fff7f9"
)
fig.show()

print("среднее значение продаж:", df_train['sales'].mean())
print("медиана:", df_train['sales'].median())
print("доля нулевых продаж:", (df_train['sales'] == 0).mean())


# %%
daily_sales = (
    df_train.groupby('date')['sales']
    .sum()
    .reset_index()
)

fig = px.line(
    daily_sales,
    x='date', y='sales',
    title='Динамика общих продаж по датам',
    color_discrete_sequence=["#ff69b4"]
)
fig.update_layout(plot_bgcolor="#fff7f9")
fig.show()


# %%
# Слияние train + stores
merged = df_train.merge(df_stores, on='store_nbr', how='left')

# Средние продажи по типам магазинов
type_sales = merged.groupby('type')['sales'].mean().reset_index().sort_values('sales', ascending=False)
fig = px.bar(type_sales, x='type', y='sales', color='type',
             color_discrete_sequence=px.colors.sequential.Pinkyl_r,
             title='Средние продажи по типам магазинов')
fig.update_layout(showlegend=False)
fig.show()

# Кластеры
cluster_sales = merged.groupby('cluster')['sales'].mean().reset_index()
fig = px.bar(cluster_sales, x='cluster', y='sales',
             color_discrete_sequence=["#ff80b0"],
             title='Средние продажи по кластерам')
fig.show()


# %%
family_sales = df_train.groupby('family')['sales'].mean().reset_index().sort_values('sales', ascending=False)

fig = px.bar(family_sales.head(15), x='family', y='sales',
             color='sales', color_continuous_scale='pinkyl',
             title='Топ 15 товаров по средним продажам')
fig.show()

# %%
corr_value = df_train[['sales', 'onpromotion']].corr().iloc[0, 1]
print(f"Корреляция между продажами и промоакциями: {corr_value:.4f}")

# %%
# --- ОБРАБОТКА OIL ---
# Сортируем даты, чтобы корректно применить интерполяцию
df_oil = df_oil.sort_values('date').reset_index(drop=True)

# Добавляем флаг пропуска — может оказаться полезным для модели
df_oil['oil_na_flag'] = df_oil['dcoilwtico'].isna().astype(int)

# Линейная интерполяция по времени. limit_direction='both' заполняет NaN в начале и в конце
df_oil['dcoilwtico'] = df_oil['dcoilwtico'].interpolate(method='linear', limit_direction='both')

# На случай, если остались NaN — применяем ffill/bfill и среднее
if df_oil['dcoilwtico'].isna().any():
    df_oil['dcoilwtico'] = df_oil['dcoilwtico'].fillna(method='ffill').fillna(method='bfill')
    df_oil['dcoilwtico'] = df_oil['dcoilwtico'].fillna(df_oil['dcoilwtico'].mean())

# %%
# --- ОБРАБОТКА TRANSACTIONS ---
# Проверяем, где есть пропуски по транзакциям
missing_by_store = df_trans[df_trans['transactions'].isna()] \
    .groupby('store_nbr').size().sort_values(ascending=False).head()
print("Топ магазинов по числу пропусков в transactions:", missing_by_store)

# Добавляем день недели (т.к. трафик зависит от него)
df_trans['dayofweek'] = df_trans['date'].dt.dayofweek

# Считаем медиану по (магазин, день недели)
agg_store_dow = df_trans.groupby(['store_nbr','dayofweek'])['transactions'].median().reset_index().rename(columns={'transactions':'median_tr'})
agg_store = df_trans.groupby('store_nbr')['transactions'].median().reset_index().rename(columns={'transactions':'median_tr_store'})
global_median = df_trans['transactions'].median()

# Добавляем агрегаты
df_trans = df_trans.merge(agg_store_dow, on=['store_nbr','dayofweek'], how='left')
df_trans = df_trans.merge(agg_store, on='store_nbr', how='left')

# Функция заполнения пропусков
def fill_transactions(row):
    if not pd.isna(row['transactions']):
        return row['transactions']
    if not pd.isna(row['median_tr']):
        return row['median_tr']
    if not pd.isna(row['median_tr_store']):
        return row['median_tr_store']
    return global_median

# Добавляем флаг пропуска и применяем заполнение
df_trans['transactions_na_flag'] = df_trans['transactions'].isna().astype(int)
df_trans['transactions'] = df_trans.apply(fill_transactions, axis=1)

# Убираем временные колонки
df_trans.drop(columns=['median_tr', 'median_tr_store'], inplace=True)

# 💬 Почему так:
# Пропуски лучше восстанавливать медианой по схожим условиям (магазин+день недели).
# Это сохраняет закономерность по трафику, но не добавляет шум.


# %%
df_train = df_train.merge(df_stores, on='store_nbr', how='left')
df_train = df_train.merge(df_oil, on='date', how='left')
df_train = df_train.merge(df_trans, on=['date', 'store_nbr'], how='left')

df_train.info()


# %%
df_train['year'] = df_train['date'].dt.year
df_train['month'] = df_train['date'].dt.month
df_train['day'] = df_train['date'].dt.day
df_train['dayofweek'] = df_train['date'].dt.dayofweek
df_train['is_weekend'] = df_train['dayofweek'].isin([5,6]).astype(int)
df_train['weekofyear'] = df_train['date'].dt.isocalendar().week.astype(int)
df_train['quarter'] = df_train['date'].dt.quarter

# %%
for col in ['city', 'state', 'type', 'family']:
    df_train[col] = df_train[col].astype('category')

# %%
print("Пропуски по количественным признакам:")
print(df_train[['dcoilwtico', 'transactions']].isna().sum())

df_train['transactions'] = df_train['transactions'].fillna(0)

# %%
# --- ОБРАБОТКА ПРАЗДНИКОВ ---
hol = df_holidays.copy()
hol['is_holiday'] = 1

# Национальные, региональные и локальные флаги
national = hol[hol['locale']=='National'][['date']].drop_duplicates()
national['is_holiday_national'] = 1

regional = hol[hol['locale']=='Regional'][['date','locale_name']].drop_duplicates().rename(columns={'locale_name':'state'})
regional['is_holiday_regional'] = 1

local = hol[hol['locale']=='Local'][['date','locale_name']].drop_duplicates().rename(columns={'locale_name':'city'})
local['is_holiday_local'] = 1

# Добавляем флаги к df_train
df_train = df_train.merge(national, on='date', how='left')
df_train = df_train.merge(regional, on=['date','state'], how='left')
df_train = df_train.merge(local, on=['date','city'], how='left')

# Заполняем пропуски нулями
for c in ['is_holiday_national','is_holiday_regional','is_holiday_local']:
    if c not in df_train.columns:
        df_train[c] = 0
    else:
        df_train[c] = df_train[c].fillna(0).astype(int)

# Обрабатываем transferred (если есть)
if 'transferred' in df_holidays.columns:
    trans = df_holidays[['date','transferred']].drop_duplicates()
    df_train = df_train.merge(trans, on='date', how='left')
    df_train['transferred'] = df_train['transferred'].fillna(False).astype(bool)
else:
    df_train['transferred'] = False

# 💬 Почему оставляем три флага:
# Разные праздники могут влиять по-разному. Например, локальные — только на один город,
# а национальные — на все магазины. Слияние в один флаг "is_holiday_final" теряет эту информацию.
# Поэтому три признака дают модели больше гибкости.


# %%
df_train.head()

# %%
df_train = df_train.sort_values(['store_nbr', 'family', 'date'])

# Создаём лаги продаж (на 1, 7, 14 и 28 дней)
for lag in [1, 7, 14, 28]:
    df_train[f'lag_{lag}'] = df_train.groupby(['store_nbr', 'family'])['sales'].shift(lag)

# %%
for window in [7, 14, 28]:
    df_train[f'roll_mean_{window}'] = (
        df_train.groupby(['store_nbr', 'family'])['sales']
        .shift(1)
        .rolling(window=window)
        .mean()
    )
    df_train[f'roll_std_{window}'] = (
        df_train.groupby(['store_nbr', 'family'])['sales']
        .shift(1)
        .rolling(window=window)
        .std()
    )

# %%
lag_cols = [col for col in df_train.columns if col.startswith('lag_') or col.startswith('roll_')]
df_train[lag_cols] = df_train[lag_cols].fillna(0)

# Проверяем готовую таблицу
print("Размер таблицы после добавления фич:", df_train.shape)
df_train.info()

# %%
df_train.head()

# %%


# %%


# %%


# %%


# %%


# %%
df_oil['dcoilwtico'] = df_oil['dcoilwtico'].interpolate(limit_direction='both')

df_train = df_train.merge(df_stores, on='store_nbr', how='left')
df_train = df_train.merge(df_oil, on='date', how='left')
df_train = df_train.merge(df_trans, on=['date', 'store_nbr'], how='left')

df_train.info()

# %%
df_train.head()

# %%
df_train['year'] = df_train['date'].dt.year
df_train['month'] = df_train['date'].dt.month
df_train['day'] = df_train['date'].dt.day
df_train['dayofweek'] = df_train['date'].dt.dayofweek
df_train['is_weekend'] = df_train['dayofweek'].isin([5,6]).astype(int)
df_train['weekofyear'] = df_train['date'].dt.isocalendar().week.astype(int)
df_train['quarter'] = df_train['date'].dt.quarter


# %%
# Категориальные признаки — сразу приводим к category
for col in ['city', 'state', 'type', 'family']:
    df_train[col] = df_train[col].astype('category')

# Пропуски в численных данных
print("Пропуски по количественным признакам:")
print(df_train[['dcoilwtico', 'transactions']].isna().sum())

# Заполним transactions 0 (если данных нет — продаж не было)
df_train['transactions'] = df_train['transactions'].fillna(0)

# %%
# Подготовим копию holidays и создадим флаги
holidays = df_holidays.copy()
holidays['is_holiday'] = 1

# Разделяем по типам locale
national = holidays[holidays['locale'] == 'National'][['date', 'is_holiday']]
regional = holidays[holidays['locale'] == 'Regional'][['date', 'locale_name', 'is_holiday']].rename(columns={'locale_name': 'state'})
local = holidays[holidays['locale'] == 'Local'][['date', 'locale_name', 'is_holiday']].rename(columns={'locale_name': 'city'})

# Мёрджим
df_train = df_train.merge(national, on='date', how='left')
df_train = df_train.merge(regional, on=['date', 'state'], how='left', suffixes=('', '_regional'))
df_train = df_train.merge(local, on=['date', 'city'], how='left', suffixes=('', '_local'))

# Объединяем все флаги в один
df_train['is_holiday_final'] = df_train[['is_holiday', 'is_holiday_regional', 'is_holiday_local']].max(axis=1)
df_train['is_holiday_final'] = df_train['is_holiday_final'].fillna(0).astype(int)

# Убираем промежуточные колонки
df_train.drop(columns=['is_holiday', 'is_holiday_regional', 'is_holiday_local'], inplace=True)

# %%
df_train.head()

# %%



