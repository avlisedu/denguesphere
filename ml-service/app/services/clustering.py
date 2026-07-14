"""DBSCAN spatial clustering service for dengue case data.

Ported from the original Streamlit page (pages/clusterizador.py). Map
rendering (folium) is dropped here — the frontend draws the map itself
(react-leaflet) from the point list this module returns.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics import adjusted_rand_score, silhouette_samples, silhouette_score

from app.utils import df_records

EARTH_RADIUS_KM = 6371.0088


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes column names and adds semana_epi/ano_epi columns (S01-S52 +
    ISO year), vectorized over the whole column instead of row-by-row —
    row-wise pd.to_datetime calls do not scale past a few thousand rows.
    """
    df = df.rename(columns={"lat": "latitude", "long": "longitude"}).copy()
    if "dt_notificacao" not in df.columns:
        raise ValueError("missing_dt_notificacao_column")

    parsed = pd.to_datetime(df["dt_notificacao"], errors="coerce", dayfirst=True)
    iso = parsed.dt.isocalendar()
    mask = parsed.notna()

    semana_epi = pd.Series([None] * len(df), index=df.index, dtype=object)
    ano_epi = pd.Series([None] * len(df), index=df.index, dtype=object)
    semana_epi.loc[mask] = iso.loc[mask, "week"].astype(int).map(lambda w: f"S{w:02d}")
    ano_epi.loc[mask] = iso.loc[mask, "year"].astype(int)

    df["semana_epi"] = semana_epi
    df["ano_epi"] = ano_epi
    return df


def available_periods(df: pd.DataFrame) -> list[dict]:
    """List of {ano, semanas[]} available in the dataset, for the UI's
    year/week selectors."""
    periods = []
    for ano in sorted(df["ano_epi"].dropna().unique()):
        semanas = sorted(df.loc[df["ano_epi"] == ano, "semana_epi"].dropna().unique())
        periods.append({"ano": int(ano), "semanas": semanas})
    return periods


def executar_clusterizacao(df: pd.DataFrame, eps_km: float, min_samples: int) -> pd.DataFrame:
    """Runs DBSCAN with haversine metric. eps_km is converted to radians."""
    eps = eps_km / EARTH_RADIUS_KM
    coords = np.radians(df[["latitude", "longitude"]])
    db = DBSCAN(eps=eps, min_samples=min_samples, algorithm="ball_tree", metric="haversine")
    df = df.copy()
    df["cluster"] = db.fit_predict(coords)
    return df


def summarize_clusters(df_cluster: pd.DataFrame) -> list[dict]:
    if df_cluster["cluster"].max() < 0:
        return []

    resumo = (
        df_cluster[df_cluster["cluster"] != -1]
        .groupby("cluster")
        .agg(
            n_casos=("latitude", "count"),
            semanas=("semana_epi", lambda x: sorted(set(x))),
            lat_media=("latitude", "mean"),
            lon_media=("longitude", "mean"),
        )
        .reset_index()
        .sort_values("n_casos", ascending=False)
    )
    return df_records(resumo)


def silhouette_analysis(df_cluster: pd.DataFrame) -> dict | None:
    df_sil = df_cluster[df_cluster["cluster"] != -1].copy()
    if df_sil["cluster"].nunique() < 2:
        return None

    coords_rad = np.radians(df_sil[["latitude", "longitude"]].values)
    labels = df_sil["cluster"].values

    global_score = silhouette_score(coords_rad, labels, metric="haversine")
    per_point = silhouette_samples(coords_rad, labels, metric="haversine")
    df_sil["silhouette"] = per_point

    return {
        "global_score": float(global_score),
        "per_cluster": [
            {"cluster": int(cluster_id), "silhouette": float(value)}
            for cluster_id, value in zip(df_sil["cluster"], df_sil["silhouette"])
        ],
    }


def stability_analysis(
    df_base: pd.DataFrame,
    eps_km: float,
    min_samples: int,
    eps_fatores=(0.9, 1.1),
    delta_minpts=(-1, 1),
) -> list[dict]:
    """ARI-based robustness check: how much do cluster labels change under
    small perturbations of eps/min_samples."""
    df_base = df_base.sort_index()
    df_ref = executar_clusterizacao(df_base, eps_km, min_samples).sort_index()
    labels_ref = df_ref["cluster"].to_numpy()

    resultados = []
    for f in eps_fatores:
        df_var = executar_clusterizacao(df_base, eps_km * f, min_samples).sort_index()
        ari = adjusted_rand_score(labels_ref, df_var["cluster"].to_numpy())
        resultados.append({"parametro": "eps", "variacao": f"{f:.2f}x", "ari": float(ari)})

    for d in delta_minpts:
        m_var = min_samples + d
        if m_var >= 2:
            df_var = executar_clusterizacao(df_base, eps_km, m_var).sort_index()
            ari = adjusted_rand_score(labels_ref, df_var["cluster"].to_numpy())
            resultados.append({"parametro": "min_samples", "variacao": str(m_var), "ari": float(ari)})

    return resultados
