import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { MapContainer, TileLayer, CircleMarker, Circle, Popup } from "react-leaflet";
import Plot from "react-plotly.js";
import "leaflet/dist/leaflet.css";

import { fetchClusterPeriods, runCluster } from "../api/client";
import { chartLayout, plotConfig } from "../utils/plotTheme";

const CORES = [
  "#C62828", "#1565C0", "#2E7D32", "#EF6C00", "#6A1B9A",
  "#00838F", "#AD1457", "#4527A0", "#0277BD", "#9E9D24",
  "#8E24AA", "#43A047", "#E53935", "#039BE5",
];
const NOISE_COLOR = "#9E9E9E";
const DEFAULT_CENTER = [-8.0476, -34.877]; // Recife, PE — fallback map center before a result is available

function corFor(clusterId) {
  return clusterId === -1 ? NOISE_COLOR : CORES[clusterId % CORES.length];
}

function mean(values) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

export default function Clusterizador() {
  const { t } = useTranslation();

  const [file, setFile] = useState(null);
  const [periods, setPeriods] = useState(null);
  const [ano, setAno] = useState(null);
  const [semanas, setSemanas] = useState([]);
  const [epsKm, setEpsKm] = useState(0.3);
  const [minSamples, setMinSamples] = useState(5);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [stabilityLoading, setStabilityLoading] = useState(false);

  async function handleFileChange(e) {
    const selected = e.target.files?.[0];
    setError(null);
    setResult(null);
    setPeriods(null);
    setFile(selected ?? null);
    if (!selected) return;

    try {
      const data = await fetchClusterPeriods(selected);
      setPeriods(data.periods);
      const first = data.periods[0];
      setAno(first?.ano ?? null);
      setSemanas(first ? first.semanas.slice(0, 1) : []);
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message);
    }
  }

  async function handleProcess(includeStability = false) {
    if (includeStability) setStabilityLoading(true);
    else setProcessing(true);
    setError(null);
    try {
      const data = await runCluster(file, {
        epsKm,
        minSamples,
        ano,
        semanas,
        includeStability,
      });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message);
    } finally {
      setProcessing(false);
      setStabilityLoading(false);
    }
  }

  const anosDisponiveis = periods?.map((p) => p.ano) ?? [];
  const semanasDisponiveis = periods?.find((p) => p.ano === ano)?.semanas ?? [];

  const center = useMemo(() => {
    if (!result?.points?.length) return null;
    return [mean(result.points.map((p) => p.latitude)), mean(result.points.map((p) => p.longitude))];
  }, [result]);

  const complementares = useMemo(() => {
    if (!result?.summary?.length) return null;
    const casos = result.summary.map((s) => s.n_casos);
    const total = casos.reduce((a, b) => a + b, 0);
    const maiorIdx = casos.indexOf(Math.max(...casos));
    const media = mean(casos);
    const ordenados = [...casos].sort((a, b) => a - b);
    const mediana =
      ordenados.length % 2 === 0
        ? (ordenados[ordenados.length / 2 - 1] + ordenados[ordenados.length / 2]) / 2
        : ordenados[(ordenados.length - 1) / 2];
    const desvio = Math.sqrt(mean(casos.map((c) => (c - media) ** 2)));
    return {
      total,
      maiorCluster: result.summary[maiorIdx].cluster,
      maiorQtd: casos[maiorIdx],
      media,
      mediana,
      desvio,
    };
  }, [result]);

  const tendencia = useMemo(() => {
    if (!result?.points?.length) return [];
    const counts = new Map();
    for (const p of result.points) {
      counts.set(p.semana_epi, (counts.get(p.semana_epi) ?? 0) + 1);
    }
    return [...counts.entries()]
      .map(([semana, casos]) => ({ semana, casos, num: Number(semana.replace("S", "")) }))
      .sort((a, b) => a.num - b.num);
  }, [result]);

  return (
    <div className="page page-clusterizador">
      <h1>{t("cluster_title")}</h1>

      <label className="file-input">
        {t("cluster_upload_label")}
        <input type="file" accept=".xlsx,.csv" onChange={handleFileChange} />
      </label>

      {error && <div className="alert alert-error">{error}</div>}

      {periods && (
        <div className="cluster-layout">
          <aside className="cluster-sidebar">
            <h3>{t("cluster_sidebar_header")}</h3>

            <label>
              {t("cluster_eps_label")}
              <input
                type="range"
                min={0.05}
                max={5}
                step={0.05}
                value={epsKm}
                onChange={(e) => setEpsKm(Number(e.target.value))}
              />
              <span>{epsKm.toFixed(2)} km</span>
              <small>{t("cluster_eps_help")}</small>
            </label>

            <label>
              {t("cluster_min_samples_label")}
              <input
                type="range"
                min={2}
                max={20}
                step={1}
                value={minSamples}
                onChange={(e) => setMinSamples(Number(e.target.value))}
              />
              <span>{minSamples}</span>
            </label>

            <label>
              {t("cluster_year_label")}
              <select
                value={ano ?? ""}
                onChange={(e) => {
                  const newAno = Number(e.target.value);
                  setAno(newAno);
                  setSemanas(periods.find((p) => p.ano === newAno)?.semanas.slice(0, 1) ?? []);
                }}
              >
                {anosDisponiveis.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </label>

            <label>
              {t("cluster_weeks_label")}
              <select
                multiple
                value={semanas}
                onChange={(e) => setSemanas([...e.target.selectedOptions].map((o) => o.value))}
              >
                {semanasDisponiveis.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <button disabled={processing || !semanas.length} onClick={() => handleProcess(false)}>
              {processing ? "..." : t("cluster_button_apply")}
            </button>
          </aside>

          <main className="cluster-main">
            {result && (
              <h3>
                {t("cluster_header_period", { year: ano, weeks: semanas.join(", ") })}
              </h3>
            )}

            <div className="map-card">
              <MapContainer center={center ?? DEFAULT_CENTER} zoom={12} style={{ height: 500, width: "100%" }}>
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors, &copy; CARTO'
                  url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                />
                {result?.summary.map((s) => (
                  <Circle
                    key={`circle-${s.cluster}`}
                    center={[s.lat_media, s.lon_media]}
                    radius={epsKm * 1000}
                    pathOptions={{ color: corFor(s.cluster), fill: false, weight: 2, opacity: 0.5 }}
                  />
                ))}
                {result?.points.map((p, i) => (
                  <CircleMarker
                    key={i}
                    center={[p.latitude, p.longitude]}
                    radius={6}
                    pathOptions={{
                      color: corFor(p.cluster),
                      fillColor: corFor(p.cluster),
                      fillOpacity: p.cluster !== -1 ? 0.9 : 0.6,
                    }}
                  >
                    <Popup>
                      {p.cluster !== -1 ? `Cluster ${p.cluster}` : "Ruído (isolado)"}
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>

            {result && (
              <>
                {result.summary.length > 0 ? (
                  <>
                    <h3>{t("cluster_stats_title")}</h3>
                    <div className="table-wrapper">
                      <table>
                        <thead>
                          <tr>
                            <th>Cluster</th>
                            <th>{t("cluster_metric_total_cases")}</th>
                            <th>Semanas</th>
                            <th>Lat</th>
                            <th>Lon</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.summary.map((s) => (
                            <tr key={s.cluster}>
                              <td>{s.cluster}</td>
                              <td>{s.n_casos}</td>
                              <td>{s.semanas.join(", ")}</td>
                              <td>{s.lat_media.toFixed(5)}</td>
                              <td>{s.lon_media.toFixed(5)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="metrics-row">
                      <div className="metric">
                        <span>{t("cluster_metric_n_clusters")}</span>
                        <strong>{result.summary.length}</strong>
                      </div>
                      <div className="metric">
                        <span>{t("cluster_metric_noise")}</span>
                        <strong>{result.n_noise}</strong>
                      </div>
                    </div>

                    {complementares && (
                      <>
                        <h4>{t("cluster_stats_comp_title")}</h4>
                        <div className="metrics-row">
                          <div className="metric">
                            <span>{t("cluster_metric_total_cases")}</span>
                            <strong>{complementares.total}</strong>
                          </div>
                          <div className="metric">
                            <span>{t("cluster_metric_biggest_cluster_id")}</span>
                            <strong>{complementares.maiorCluster}</strong>
                          </div>
                          <div className="metric">
                            <span>{t("cluster_metric_biggest_cluster_cases")}</span>
                            <strong>{complementares.maiorQtd}</strong>
                          </div>
                          <div className="metric">
                            <span>{t("cluster_metric_mean_cases")}</span>
                            <strong>{complementares.media.toFixed(2)}</strong>
                          </div>
                          <div className="metric">
                            <span>{t("cluster_metric_median_cases")}</span>
                            <strong>{complementares.mediana.toFixed(2)}</strong>
                          </div>
                          <div className="metric">
                            <span>{t("cluster_metric_sd_cases")}</span>
                            <strong>{complementares.desvio.toFixed(2)}</strong>
                          </div>
                        </div>
                      </>
                    )}

                    <div className="chart-card">
                      <h4>{t("cluster_plot_cases_bar_title")}</h4>
                      <Plot
                        data={[
                          {
                            x: result.summary.map((s) => s.cluster),
                            y: result.summary.map((s) => s.n_casos),
                            type: "bar",
                            marker: { color: result.summary.map((s) => corFor(s.cluster)) },
                            text: result.summary.map((s) => s.n_casos),
                            textposition: "outside",
                          },
                        ]}
                        layout={chartLayout({
                          autosize: true,
                          xaxis: { title: t("cluster_plot_cases_bar_x") },
                          yaxis: { title: t("cluster_plot_cases_bar_y") },
                        })}
                        config={plotConfig}
                        useResizeHandler
                        style={{ width: "100%", height: 340 }}
                      />
                    </div>

                    <div className="chart-card">
                      <h4>{t("cluster_plot_centers_title")}</h4>
                      <Plot
                        data={[
                          {
                            x: result.summary.map((s) => s.lon_media),
                            y: result.summary.map((s) => s.lat_media),
                            mode: "markers",
                            type: "scatter",
                            text: result.summary.map((s) => `Cluster ${s.cluster}`),
                            marker: {
                              size: result.summary.map((s) => Math.max(10, s.n_casos)),
                              color: result.summary.map((s) => corFor(s.cluster)),
                              line: { width: 1, color: "#fff" },
                            },
                          },
                        ]}
                        layout={chartLayout({
                          autosize: true,
                          xaxis: { title: t("cluster_plot_centers_x") },
                          yaxis: { title: t("cluster_plot_centers_y") },
                        })}
                        config={plotConfig}
                        useResizeHandler
                        style={{ width: "100%", height: 340 }}
                      />
                    </div>

                    <div className="chart-card">
                      <h4>{t("cluster_plot_trend_title")}</h4>
                      <Plot
                        data={[
                          {
                            x: tendencia.map((d) => d.semana),
                            y: tendencia.map((d) => d.casos),
                            mode: "lines+markers",
                            type: "scatter",
                            line: { shape: "spline", width: 3, color: "#0e6b52" },
                            marker: { color: "#0e6b52" },
                          },
                        ]}
                        layout={chartLayout({
                          autosize: true,
                          xaxis: { title: t("cluster_plot_trend_x") },
                          yaxis: { title: t("cluster_plot_trend_y") },
                        })}
                        config={plotConfig}
                        useResizeHandler
                        style={{ width: "100%", height: 340 }}
                      />
                    </div>
                  </>
                ) : (
                  <div className="alert alert-info">{t("cluster_info_no_clusters")}</div>
                )}

                <section className="cluster-advanced">
                  <h3>{t("cluster_advanced_title")}</h3>
                  <p className="caption">{t("cluster_advanced_caption")}</p>
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={showAdvanced}
                      onChange={(e) => setShowAdvanced(e.target.checked)}
                    />
                    {t("cluster_advanced_toggle")}
                  </label>

                  {showAdvanced && (
                    <>
                      {!result.silhouette ? (
                        <div className="alert alert-info">{t("cluster_info_silhouette_not_defined")}</div>
                      ) : (
                        <div className="panel">
                          <h4>{t("cluster_silhouette_title")}</h4>
                          <p className="caption">{t("cluster_silhouette_caption")}</p>
                          <div className="metric">
                            <span>{t("cluster_silhouette_metric")}</span>
                            <strong>{result.silhouette.global_score.toFixed(3)}</strong>
                          </div>
                          <p>{silhouetteInterpretation(result.silhouette.global_score, t)}</p>
                          <p>{t("cluster_silhouette_explanation")}</p>

                          <h5>{t("cluster_silhouette_dist_title")}</h5>
                          <Plot
                            data={groupByCluster(result.silhouette.per_cluster).map((g) => ({
                              y: g.values,
                              type: "box",
                              name: `${g.cluster}`,
                              boxpoints: "all",
                              marker: { color: corFor(g.cluster) },
                            }))}
                            layout={chartLayout({
                              autosize: true,
                              xaxis: { title: t("cluster_silhouette_label_cluster") },
                              yaxis: { title: t("cluster_silhouette_label_value") },
                              showlegend: false,
                            })}
                            config={plotConfig}
                            useResizeHandler
                            style={{ width: "100%", height: 340 }}
                          />
                        </div>
                      )}

                      <div className="panel">
                        <h4>{t("cluster_ari_title")}</h4>
                        <p className="caption">{t("cluster_ari_caption")}</p>
                        <button disabled={stabilityLoading} onClick={() => handleProcess(true)}>
                          {stabilityLoading ? t("cluster_ari_spinner") : t("cluster_ari_button")}
                        </button>
                        <p>{t("cluster_ari_help")}</p>

                        {result.stability && (
                          <>
                            <h5>{t("cluster_ari_results_title")}</h5>
                            <div className="metrics-row">
                              {result.stability.map((r, i) => {
                                const best = Math.max(...result.stability.map((x) => x.ari));
                                return (
                                  <div className="metric" key={i}>
                                    <span>
                                      {r.parametro} = {r.variacao}
                                    </span>
                                    <strong>{r.ari.toFixed(3)}</strong>
                                    {r.ari === best && <em>{t("cluster_ari_best_result")}</em>}
                                  </div>
                                );
                              })}
                            </div>
                            <h5>{t("cluster_ari_interp_title")}</h5>
                            <p>
                              {ariInterpretation(
                                Math.max(...result.stability.map((x) => x.ari)),
                                t
                              )}
                            </p>
                          </>
                        )}
                      </div>
                    </>
                  )}
                </section>
              </>
            )}
          </main>
        </div>
      )}

      {!periods && <div className="alert alert-info">{t("cluster_info_upload_start")}</div>}
    </div>
  );
}

function groupByCluster(perCluster) {
  const map = new Map();
  for (const { cluster, silhouette } of perCluster) {
    if (!map.has(cluster)) map.set(cluster, []);
    map.get(cluster).push(silhouette);
  }
  return [...map.entries()].map(([cluster, values]) => ({ cluster, values }));
}

function silhouetteInterpretation(score, t) {
  if (score >= 0.7) return t("cluster_silhouette_interp_high");
  if (score >= 0.5) return t("cluster_silhouette_interp_good");
  if (score >= 0.3) return t("cluster_silhouette_interp_mid");
  return t("cluster_silhouette_interp_low");
}

function ariInterpretation(best, t) {
  if (best >= 0.8) return t("cluster_ari_interp_high");
  if (best >= 0.65) return t("cluster_ari_interp_mid");
  return t("cluster_ari_interp_low");
}
