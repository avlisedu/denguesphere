import axios from "axios";
import FormData from "form-data";

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || "http://127.0.0.1:8001";

const client = axios.create({ baseURL: ML_SERVICE_URL, timeout: 120_000 });

/**
 * Forwards an uploaded file (from multer, in-memory) plus extra form
 * fields to a ml-service endpoint as multipart/form-data.
 */
export async function forwardToMlService(path, file, fields = {}) {
  const form = new FormData();
  form.append("file", file.buffer, { filename: file.originalname });

  for (const [key, value] of Object.entries(fields)) {
    if (Array.isArray(value)) {
      for (const item of value) form.append(key, item);
    } else if (value !== undefined && value !== null) {
      form.append(key, String(value));
    }
  }

  const response = await client.post(path, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    maxContentLength: Infinity,
  });
  return response.data;
}

export async function getFromMlService(path) {
  const response = await client.get(path);
  return response.data;
}
