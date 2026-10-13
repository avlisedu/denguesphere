"""Concordância entre o geocodificador local (OSM) e o Nominatim usado pelo
DengueSphere, na amostra de 2021 já geocodificada pelo software (dataset/baserecife.xlsx)."""
from pathlib import Path

import numpy as np
import pandas as pd

from geocodificar import GeocodificadorLocal

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "resultados"


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    ref = pd.read_excel(RAIZ.parent / "dataset" / "baserecife.xlsx")
    geo = GeocodificadorLocal()
    local = pd.DataFrame([geo.geocodificar(r, b) for r, b in zip(ref.nome_logradouro_residencia, ref.no_bairro_residencia)])
    ref["dist_km"] = haversine_km(ref.latitude, ref.longitude, local.latitude, local.longitude)
    ref["tipo_local"] = local.tipo_match

    linhas = []
    for (fonte, tipo), g in ref.groupby(["fonte_coordenada", "tipo_local"]):
        d = g.dist_km.dropna()
        linhas.append({
            "fonte_nominatim": fonte, "tipo_local": tipo, "n": len(g),
            "mediana_m": d.median() * 1000, "p75_m": d.quantile(.75) * 1000, "p90_m": d.quantile(.9) * 1000,
            "pct_ate_250m": (d <= .25).mean() * 100, "pct_ate_500m": (d <= .5).mean() * 100,
            "pct_ate_1km": (d <= 1).mean() * 100,
        })
    tab = pd.DataFrame(linhas).round(1)
    tab.to_csv(SAIDA / "tab_validacao_geocodificacao.csv", index=False)
    print(tab.to_string())
    exato = ref[(ref.fonte_coordenada == "endereco_exato") & ref.tipo_local.isin(["rua_bairro", "rua_vizinha", "rua_cidade"])]
    print("\nambos no nível de rua: n=%d mediana=%.0f m p90=%.0f m <=500m=%.1f%%" % (
        len(exato), exato.dist_km.median() * 1000, exato.dist_km.quantile(.9) * 1000, (exato.dist_km <= .5).mean() * 100))
