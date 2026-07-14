import io
import json

import pandas as pd
from fastapi import HTTPException, UploadFile


async def read_upload_to_df(file: UploadFile) -> pd.DataFrame:
    contents = await file.read()
    name = (file.filename or "").lower()

    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(contents))
    if name.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(contents))

    raise HTTPException(status_code=400, detail="unsupported_file_type")


def df_records(df: pd.DataFrame) -> list[dict]:
    """Serializes a DataFrame to JSON-safe records.

    `.to_dict(orient="records")` leaves pandas/numpy types in place - NaN
    stays NaN and Timestamp columns stay Timestamps, both of which break
    Starlette's JSONResponse (it calls json.dumps with allow_nan=False).
    Round-tripping through pandas' own to_json() instead turns NaN/NaT into
    null and dates into ISO strings.
    """
    return json.loads(df.to_json(orient="records", date_format="iso"))
