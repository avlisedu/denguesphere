import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 120_000,
});

export function fetchCoordsPreview(file) {
  const form = new FormData();
  form.append("file", file);
  return api.post("/geocode/preview", form).then((r) => r.data);
}

// Geocoding hits Nominatim at ~1 request/second, so it runs as a
// background job on the ml-service: this kicks it off and returns a
// job_id immediately instead of blocking on the whole batch.
export function startGeocodeJob(file, { cepCol, ruaCol, bairroCol }) {
  const form = new FormData();
  form.append("file", file);
  form.append("cep_col", cepCol);
  form.append("rua_col", ruaCol);
  form.append("bairro_col", bairroCol);
  return api.post("/geocode/process", form).then((r) => r.data);
}

export function fetchGeocodeJobStatus(jobId) {
  return api.get(`/geocode/process/${jobId}`).then((r) => r.data);
}

export function fetchClusterPeriods(file) {
  const form = new FormData();
  form.append("file", file);
  return api.post("/cluster/periods", form).then((r) => r.data);
}

export function runCluster(file, { epsKm, minSamples, ano, semanas, includeStability }) {
  const form = new FormData();
  form.append("file", file);
  form.append("eps_km", epsKm);
  form.append("min_samples", minSamples);
  form.append("ano", ano);
  semanas.forEach((s) => form.append("semanas", s));
  form.append("include_stability", includeStability);
  return api.post("/cluster/process", form).then((r) => r.data);
}

export default api;
