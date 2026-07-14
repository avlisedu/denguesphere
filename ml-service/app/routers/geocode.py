import threading

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.services.geocoding import geocode_dataframe
from app.services.jobs import job_store
from app.utils import df_records, read_upload_to_df

router = APIRouter(prefix="/geocode", tags=["geocode"])


@router.post("/preview")
async def preview(file: UploadFile):
    df = await read_upload_to_df(file)
    return {
        "columns": list(df.columns),
        "n_rows": len(df),
        "sample": df_records(df.head(5)),
    }


@router.post("/process")
async def process(
    file: UploadFile,
    cep_col: str = Form(...),
    rua_col: str = Form(...),
    bairro_col: str = Form(...),
):
    df = await read_upload_to_df(file)
    job_id = job_store.create(total=len(df))

    def run():
        try:
            enriched = geocode_dataframe(
                df, cep_col, rua_col, bairro_col,
                on_progress=lambda done, _total: job_store.update_progress(job_id, done),
            )
            job_store.complete(job_id, {"n_rows": len(enriched), "rows": df_records(enriched)})
        except Exception as exc:  # noqa: BLE001 - report any failure back to the polling client
            job_store.fail(job_id, str(exc))

    threading.Thread(target=run, daemon=True).start()
    return {"job_id": job_id, "total": len(df)}


@router.get("/process/{job_id}")
def process_status(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job_not_found")
    return job
