import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";

import { fetchCoordsPreview, fetchGeocodeJobStatus, startGeocodeJob } from "../api/client";
import { downloadAsXlsx } from "../utils/exportXlsx";
import ProgressRing from "../components/ProgressRing";

const POLL_INTERVAL_MS = 1500;

export default function Coordenadas() {
  const { t } = useTranslation();

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [cepCol, setCepCol] = useState("");
  const [ruaCol, setRuaCol] = useState("");
  const [bairroCol, setBairroCol] = useState("");
  const [progress, setProgress] = useState(null); // { processed, total }
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const activeJobRef = useRef(null);

  useEffect(() => () => { activeJobRef.current = null; }, []);

  async function handleFileChange(e) {
    const selected = e.target.files?.[0];
    setError(null);
    setResult(null);
    setPreview(null);
    setProgress(null);
    activeJobRef.current = null;
    setFile(selected ?? null);
    if (!selected) return;

    setLoadingPreview(true);
    try {
      const data = await fetchCoordsPreview(selected);
      setPreview(data);
      setCepCol(data.columns[0] ?? "");
      setRuaCol(data.columns[1] ?? data.columns[0] ?? "");
      setBairroCol(data.columns[2] ?? data.columns[0] ?? "");
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message);
    } finally {
      setLoadingPreview(false);
    }
  }

  async function pollJob(jobId) {
    while (activeJobRef.current === jobId) {
      let job;
      try {
        job = await fetchGeocodeJobStatus(jobId);
      } catch (err) {
        setError(err.response?.data?.detail ?? err.message);
        return;
      }
      if (activeJobRef.current !== jobId) return;

      setProgress({ processed: job.processed, total: job.total });
      if (job.status === "done") {
        setResult(job.result);
        return;
      }
      if (job.status === "error") {
        setError(job.error);
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    }
  }

  async function handleStart() {
    setError(null);
    setResult(null);
    try {
      const { job_id, total } = await startGeocodeJob(file, { cepCol, ruaCol, bairroCol });
      activeJobRef.current = job_id;
      setProgress({ processed: 0, total });
      pollJob(job_id);
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message);
    }
  }

  const isProcessing = progress !== null && result === null && !error;

  return (
    <div className="page page-coordenadas">
      <h1>{t("coords_title")}</h1>
      <div className="markdown-body">
        <ReactMarkdown>{t("coords_intro")}</ReactMarkdown>
      </div>

      <label className="file-input">
        {t("coords_uploader_label")}
        <input type="file" accept=".xlsx,.csv" onChange={handleFileChange} />
      </label>

      {error && <div className="alert alert-error">{error}</div>}

      {loadingPreview && (
        <div className="alert alert-info">{t("coords_loading_preview")}</div>
      )}

      {preview && (
        <>
          <div className="alert alert-success">
            {t("coords_file_loaded", { n_rows: preview.n_rows, n_cols: preview.columns.length })}
          </div>

          <h3>{t("coords_select_columns_subheader")}</h3>
          <div className="column-selectors">
            <label>
              {t("coords_select_cep")}
              <select value={cepCol} onChange={(e) => setCepCol(e.target.value)}>
                {preview.columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("coords_select_rua")}
              <select value={ruaCol} onChange={(e) => setRuaCol(e.target.value)}>
                {preview.columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("coords_select_bairro")}
              <select value={bairroCol} onChange={(e) => setBairroCol(e.target.value)}>
                {preview.columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <button disabled={isProcessing} onClick={handleStart}>
            {t("coords_button_start")}
          </button>

          {isProcessing && (
            <div className="progress-card">
              <ProgressRing
                value={progress.total ? progress.processed / progress.total : 0}
                label={`${progress.total ? Math.round((100 * progress.processed) / progress.total) : 0}%`}
              />
              <div>
                <strong>{t("coords_processing_info")}</strong>
                <p>
                  {t("coords_processing_progress", { processed: progress.processed, total: progress.total })}
                </p>
              </div>
            </div>
          )}
        </>
      )}

      {result && (
        <>
          <div className="alert alert-success">{t("coords_processing_done")}</div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  {Object.keys(result.rows[0] ?? {}).map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.slice(0, 5).map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((value, j) => (
                      <td key={j}>{value === null ? "" : String(value)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button onClick={() => downloadAsXlsx(result.rows, "resultado_geocodificado.xlsx")}>
            {t("coords_download_button")}
          </button>
        </>
      )}

      {!file && <div className="alert alert-info">{t("coords_no_file_info")}</div>}
    </div>
  );
}
