from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.services.clustering import (
    available_periods,
    executar_clusterizacao,
    prepare_dataframe,
    silhouette_analysis,
    stability_analysis,
    summarize_clusters,
)
from app.utils import df_records, read_upload_to_df

router = APIRouter(prefix="/cluster", tags=["cluster"])


@router.post("/periods")
async def periods(file: UploadFile):
    df = await read_upload_to_df(file)
    try:
        df = prepare_dataframe(df)
    except ValueError:
        raise HTTPException(status_code=400, detail="missing_dt_notificacao_column")

    return {"n_rows": len(df), "periods": available_periods(df)}


@router.post("/process")
async def process(
    file: UploadFile,
    eps_km: float = Form(0.3),
    min_samples: int = Form(5),
    ano: int = Form(...),
    semanas: list[str] = Form(...),
    include_stability: bool = Form(False),
):
    df = await read_upload_to_df(file)
    try:
        df = prepare_dataframe(df)
    except ValueError:
        raise HTTPException(status_code=400, detail="missing_dt_notificacao_column")

    df_filtro = df[(df["ano_epi"] == ano) & (df["semana_epi"].isin(semanas))].copy()
    if df_filtro.empty:
        raise HTTPException(status_code=400, detail="empty_period")

    df_validos = df_filtro.dropna(subset=["latitude", "longitude"]).copy()
    if df_validos.empty:
        raise HTTPException(status_code=400, detail="no_valid_coordinates")

    df_cluster = executar_clusterizacao(df_validos, eps_km, min_samples)

    response = {
        "n_points": len(df_cluster),
        "n_noise": int((df_cluster["cluster"] == -1).sum()),
        "points": df_records(df_cluster[["latitude", "longitude", "cluster", "semana_epi", "ano_epi"]]),
        "summary": summarize_clusters(df_cluster),
        "silhouette": silhouette_analysis(df_cluster),
        "stability": stability_analysis(df_validos, eps_km, min_samples) if include_stability else None,
    }
    return response
