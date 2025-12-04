import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import mean_absolute_error, mean_squared_error
import statsmodels.api as sm
import statsmodels.formula.api as smf
from prophet import Prophet


def metricas(y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return mae, rmse, mape


# =====================================================
# 1. CARREGAR BASE
# =====================================================
df = pd.read_excel("baserecife.xlsx")

df["dt_sintomas"] = pd.to_datetime(df["dt_diagnostico_sintoma"], errors="coerce")
df = df.dropna(subset=["dt_sintomas"])

df["ano_epi"] = df["dt_sintomas"].dt.isocalendar().year
df["semana_epi"] = df["dt_sintomas"].dt.isocalendar().week

semanal = (
    df.groupby(["ano_epi", "semana_epi"])
      .size()
      .reset_index(name="casos")
)

semanal["data_semana"] = pd.to_datetime(
    semanal["ano_epi"].astype(str) + "-W" + semanal["semana_epi"].astype(str) + "-1",
    format="%G-W%V-%u"
)

semanal = semanal.sort_values("data_semana").reset_index(drop=True)
print("Série semanal criada:")
print(semanal.head())


# =====================================================
# 2. CRIAÇÃO DOS LAGS
# =====================================================
base = semanal.copy()

lags = [1,2,3,4,6,8,12]

for lag in lags:
    base[f"lag_{lag}"] = base["casos"].shift(lag)

base = base.dropna().reset_index(drop=True)


# =====================================================
# 3. TREINO / TESTE
# =====================================================
split = int(len(base) * 0.80)

train = base.iloc[:split]
test = base.iloc[split:]

X_train = train.drop(columns=["casos", "data_semana"])
y_train = train["casos"]

X_test = test.drop(columns=["casos", "data_semana"])
y_test = test["casos"]

print("Tamanho treino:", len(train), " | Tamanho teste:", len(test))


# =====================================================
# 4. MODELOS
# =====================================================
resultados = {}

formula = "casos ~ " + " + ".join([f"lag_{l}" for l in lags])

# GLM Poisson
glm_pois = smf.glm(formula, data=train, family=sm.families.Poisson()).fit()
pred_pois = glm_pois.predict(test)
resultados["GLM Poisson"] = metricas(y_test, pred_pois)

# GLM Binomial Negativa
glm_nb = smf.glm(formula, data=train, family=sm.families.NegativeBinomial()).fit()
pred_nb = glm_nb.predict(test)
resultados["GLM Binomial Negativa"] = metricas(y_test, pred_nb)

# SARIMA(52)
serie_y = semanal["casos"]
train_s = serie_y.iloc[:split]
test_s = serie_y.iloc[split:]

modelo_sarima = sm.tsa.statespace.SARIMAX(
    train_s,
    order=(2,1,2),
    seasonal_order=(1,1,1,52),
    enforce_stationarity=False,
    enforce_invertibility=False
).fit()

pred_sarima = modelo_sarima.forecast(len(test_s))
resultados["SARIMA(52)"] = metricas(test_s, pred_sarima)

# Prophet
prophet_df = semanal[["data_semana", "casos"]].rename(
    columns={"data_semana": "ds", "casos": "y"}
)

train_p = prophet_df.iloc[:split]
test_p = prophet_df.iloc[split:]

m = Prophet(weekly_seasonality=False, yearly_seasonality=True)
m.fit(train_p)

future = m.make_future_dataframe(periods=len(test_p), freq="W")
forecast = m.predict(future)

pred_prophet = forecast["yhat"].iloc[-len(test_p):].values
resultados["Prophet"] = metricas(test_p["y"], pred_prophet)

# =====================================================
# 5. ESCOLHA DO MELHOR MODELO
# =====================================================
print("\n===== MÉTRICAS =====")
for modelo, valores in resultados.items():
    print(f"{modelo}:  MAE={valores[0]:.2f}  RMSE={valores[1]:.2f}  MAPE={valores[2]:.2f}%")

melhor_modelo = min(resultados, key=lambda k: resultados[k][1])
print("\nMelhor modelo:", melhor_modelo)

# =====================================================
# 6. PREVISÃO FUTURA DE 26 SEMANAS
# =====================================================
n_future = 26
future_values = []

if melhor_modelo == "GLM Binomial Negativa":
    modelo_final = glm_nb

elif melhor_modelo == "GLM Poisson":
    modelo_final = glm_pois

elif melhor_modelo == "SARIMA(52)":
    modelo_final = modelo_sarima

elif melhor_modelo == "Prophet":
    modelo_final = m


# Previsão recursiva via GLM
if melhor_modelo in ["GLM Poisson", "GLM Binomial Negativa"]:

    last = base.iloc[-1:].copy()

    for i in range(n_future):

        pred_value = modelo_final.predict(last).iloc[0]
        future_values.append(pred_value)

        new_row = last.copy()
        new_row["lag_1"] = pred_value

        for lag in lags[1:]:
            if lag == 6:
                new_row["lag_6"] = last["lag_4"].iloc[0]
            elif lag == 8:
                new_row["lag_8"] = last["lag_6"].iloc[0]
            elif lag == 12:
                new_row["lag_12"] = last["lag_8"].iloc[0]
            else:
                new_row[f"lag_{lag}"] = last[f"lag_{lag-1}"].iloc[0]

        last = new_row.copy()


elif melhor_modelo == "SARIMA(52)":
    future_values = modelo_final.forecast(n_future).values

elif melhor_modelo == "Prophet":
    df_future = modelo_final.make_future_dataframe(periods=n_future, freq="W")
    forecast_future = modelo_final.predict(df_future)
    future_values = forecast_future["yhat"].iloc[-n_future:].values


# =====================================================
# 7. GRÁFICO FINAL
# =====================================================
datas_futuras = pd.date_range(
    start=semanal["data_semana"].iloc[-1],
    periods=n_future + 1,
    freq="W"
)[1:]

plt.figure(figsize=(12,6))
plt.plot(semanal["data_semana"], semanal["casos"], label="Histórico")
plt.plot(datas_futuras, future_values, label=f"Previsão 26 semanas ({melhor_modelo})", linestyle="--")
plt.title("Previsão de Dengue - 26 semanas")
plt.xlabel("Data")
plt.ylabel("Casos")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
