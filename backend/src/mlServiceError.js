export function sendMlServiceError(res, error) {
  if (error.response) {
    res.status(error.response.status).json(
      error.response.data ?? { detail: "ml_service_error" }
    );
    return;
  }
  console.error("ml-service request failed:", error.message);
  res.status(502).json({ detail: "ml_service_unreachable" });
}
