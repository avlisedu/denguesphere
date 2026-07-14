import io
import json

import pandas as pd
from fastapi import HTTPException, UploadFile


async def read_upload_to_df(file: UploadFile) -> pd.DataFrame:
    contents = await file.read()
    name = (file.filename or "").lower()

    if name.endswith(".csv"):
        return _read_csv_robust(contents)
    if name.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(contents))

    raise HTTPException(status_code=400, detail="unsupported_file_type")


def _read_csv_robust(contents: bytes) -> pd.DataFrame:
    """Excel's "Save as CSV" on Brazilian locales writes Latin-1
    (cp1252-ish) encoding with ';' separators instead of the UTF-8/','
    pandas.read_csv assumes by default - without this, such a file raises
    a UnicodeDecodeError that surfaces to users as a bare 500. sep=None
    with the python engine auto-detects the delimiter; encoding is tried
    UTF-8 first, then Latin-1.
    """
    last_error = None
    for encoding in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(contents), sep=None, engine="python", encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error


def df_records(df: pd.DataFrame) -> list[dict]:
    """Serializes a DataFrame to JSON-safe records.

    `.to_dict(orient="records")` leaves pandas/numpy types in place - NaN
    stays NaN and Timestamp columns stay Timestamps, both of which break
    Starlette's JSONResponse (it calls json.dumps with allow_nan=False).
    Round-tripping through pandas' own to_json() instead turns NaN/NaT into
    null and dates into ISO strings.
    """
    return json.loads(df.to_json(orient="records", date_format="iso"))
