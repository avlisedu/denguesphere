import "dotenv/config";
import cors from "cors";
import express from "express";

import clusterRoutes from "./routes/cluster.js";
import geocodeRoutes from "./routes/geocode.js";

const app = express();
const PORT = process.env.PORT || 3001;

// FRONTEND_ORIGIN accepts a comma-separated list, since production usually
// needs to allow both the custom domain and the Render static site's
// default onrender.com URL.
const allowedOrigins = (process.env.FRONTEND_ORIGIN || "http://localhost:5173")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

app.use(cors({ origin: allowedOrigins }));
app.use(express.json());

app.get("/api/health", (_req, res) => res.json({ status: "ok" }));
app.use("/api/geocode", geocodeRoutes);
app.use("/api/cluster", clusterRoutes);

app.listen(PORT, () => {
  console.log(`DengueSphere backend listening on port ${PORT}`);
});
