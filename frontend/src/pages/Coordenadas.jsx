import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import Plot from "react-plotly.js";
import "leaflet/dist/leaflet.css";

import { fetchCoordsPreview, fetchGeocodeJobStatus, startGeocodeJob } from "../api/client";
import { downloadAsXlsx } from "../utils/exportXlsx";
import { chartLayout, plotConfig } from "../utils/plotTheme";
import ProgressRing from "../components/ProgressRing";
import Spinner from "../components/Spinner";

const POLL_INTERVAL_MS = 1500;
const MAP_POINT_LIMIT = 1000;
const TABLE_PREVIEW_ROWS = 5;
const DEFAULT_CENTER = [-8.0476, -34.877]; // Recife, PE — fallback map center

const MATCH_TYPES = [
  { key: "cep", color: "#0e6b52", labelKey: "coords_match_cep" },
  { key: "rua_bairro", color: "#1565C0", labelKey: "coords_match_rua_bairro" },
  { key: "bairro", color: "#EF6C00", labelKey: "coords_match_bairro" },
  { key: "nao_encontrado", color: "#9E9E9E", labelKey: "coords_match_nao_encontrado" },
  { key: "erro_geocodificacao", color: "#C62828", labelKey: "coords_match_erro_geocodificacao" },
];

function colorFor(tipoMatch) {
  return MATCH_TYPES.find((m) => m.key === tipoMatch)?.color ?? "#9E9E9E";
}

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

  const stats = useMemo(() => {
    if (!result?.rows?.length) return null;
    const rows = result.rows;
    const counts = Object.fromEntries(MATCH_TYPES.map((m) => [m.key, 0]));
    for (const row of rows) {
      if (row.tipo_match in counts) counts[row.tipo_match] += 1;
    }
    const geocoded = counts.cep + counts.rua_bairro + counts.bairro;
    return {
      total: rows.length,
      geocoded,
      successRate: rows.length ? (100 * geocoded) / rows.length : 0,
      counts,
    };
  }, [result]);

  const mapPoints = useMemo(() => {
    if (!result?.rows?.length) return [];
    return result.rows
      .filter((row) => row.latitude != null && row.longitude != null)
      .slice(0, MAP_POINT_LIMIT);
  }, [result]);

  const mapBounds = useMemo(() => {
    if (!mapPoints.length) return null;
    return mapPoints.map((p) => [p.latitude, p.longitude]);
  }, [mapPoints]);

  const previewColumns = useMemo(() => {
    if (!result?.rows?.length) return [];
    const base = [cepCol, ruaCol, bairroCol].filter(Boolean);
    return [...new Set([...base, "latitude", "longitude", "tipo_match"])].filter(
      (c) => c in result.rows[0]
    );
  }, [result, cepCol, ruaCol, bairroCol]);

  return (
    <div className="page page-coordenadas">
      <div className="page-header">
        <div>
          <span className="page-eyebrow">{t("coords_hero_badge")}</span>
          <h1>{t("coords_title")}</h1>
        </div>
      </div>

      <div className="readme-card">
        <div className="markdown-body">
          <ReactMarkdown>{t("coords_intro")}</ReactMarkdown>
        </div>
      </div>

      <label className="file-input">
        {t("coords_uploader_label")}
        <input type="file" accept=".xlsx,.csv" onChange={handleFileChange} />
      </label>

      {error && <div className="alert alert-error">{error}</div>}

      {loadingPreview && (
        <div className="alert alert-info alert-loading">
          <Spinner size={14} />
          {t("coords_loading_preview")}
        </div>
      )}

      {preview && (
        <>
          <div className="alert alert-success">
            {t("coords_file_loaded", { n_rows: preview.n_rows, n_cols: preview.columns.length })}
          </div>

          <div className="panel">
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
              {isProcessing && <Spinner size={14} />}
              {t("coords_button_start")}
            </button>
          </div>

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

      {result && stats && (
        <>
          <div className="alert alert-success">{t("coords_processing_done")}</div>

          <h3>{t("coords_stats_title")}</h3>
          <div className="metrics-row">
            <div className="metric">
              <span>{t("coords_metric_total")}</span>
              <strong>{stats.total}</strong>
            </div>
            <div className="metric">
              <span>{t("coords_metric_geocoded")}</span>
              <strong>{stats.geocoded}</strong>
            </div>
            <div className="metric">
              <span>{t("coords_metric_success_rate")}</span>
              <strong>{stats.successRate.toFixed(1)}%</strong>
            </div>
            <div className="metric">
              <span>{t("coords_metric_not_found")}</span>
              <strong>{stats.counts.nao_encontrado}</strong>
            </div>
            <div className="metric">
              <span>{t("coords_metric_error")}</span>
              <strong>{stats.counts.erro_geocodificacao}</strong>
            </div>
          </div>

          {mapPoints.length > 0 && (
            <>
              <h3>{t("coords_map_title")}</h3>
              <p className="caption">{t("coords_map_caption", { n: mapPoints.length })}</p>
              <div className="map-card">
                <MapContainer
                  bounds={mapBounds ?? [DEFAULT_CENTER, DEFAULT_CENTER]}
                  boundsOptions={{ padding: [24, 24], maxZoom: 14 }}
                  style={{ height: 420, width: "100%" }}
                >
                  <TileLayer
                    attribution='&copy; OpenStreetMap contributors, &copy; CARTO'
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                  />
                  {mapPoints.map((p, i) => (
                    <CircleMarker
                      key={i}
                      center={[p.latitude, p.longitude]}
                      radius={5}
                      pathOptions={{ color: colorFor(p.tipo_match), fillColor: colorFor(p.tipo_match), fillOpacity: 0.8 }}
                    >
                      <Popup>{t(MATCH_TYPES.find((m) => m.key === p.tipo_match)?.labelKey ?? "coords_match_nao_encontrado")}</Popup>
                    </CircleMarker>
                  ))}
                </MapContainer>
              </div>
              <div className="map-legend">
                {MATCH_TYPES.map((m) => (
                  <span key={m.key} className="map-legend-item">
                    <i style={{ background: m.color }} />
                    {t(m.labelKey)}
                  </span>
                ))}
              </div>
            </>
          )}

          <div className="chart-card">
            <h4>{t("coords_chart_title")}</h4>
            <Plot
              data={[
                {
                  x: MATCH_TYPES.map((m) => t(m.labelKey)),
                  y: MATCH_TYPES.map((m) => stats.counts[m.key]),
                  type: "bar",
                  marker: { color: MATCH_TYPES.map((m) => m.color) },
                  text: MATCH_TYPES.map((m) => stats.counts[m.key]),
                  textposition: "outside",
                },
              ]}
              layout={chartLayout({
                autosize: true,
                xaxis: { title: t("coords_chart_x") },
                yaxis: { title: t("coords_chart_y") },
              })}
              config={plotConfig}
              useResizeHandler
              style={{ width: "100%", height: 320 }}
            />
          </div>

          <h3>{t("coords_table_title")}</h3>
          <p className="caption">{t("coords_table_caption", { n: Math.min(TABLE_PREVIEW_ROWS, result.rows.length) })}</p>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  {previewColumns.map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.slice(0, TABLE_PREVIEW_ROWS).map((row, i) => (
                  <tr key={i}>
                    {previewColumns.map((col) => (
                      <td key={col}>
                        {col === "tipo_match" ? (
                          <span className={`match-badge match-${row[col]}`}>
                            {t(MATCH_TYPES.find((m) => m.key === row[col])?.labelKey ?? row[col])}
                          </span>
                        ) : row[col] === null || row[col] === undefined ? (
                          ""
                        ) : (
                          String(row[col])
                        )}
                      </td>
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
