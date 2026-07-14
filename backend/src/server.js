import "dotenv/config";
import cors from "cors";
import express from "express";

import clusterRoutes from "./routes/cluster.js";
import geocodeRoutes from "./routes/geocode.js";

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors({ origin: process.env.FRONTEND_ORIGIN || "http://localhost:5173" }));
app.use(express.json());

app.get("/api/health", (_req, res) => res.json({ status: "ok" }));
app.use("/api/geocode", geocodeRoutes);
app.use("/api/cluster", clusterRoutes);

app.listen(PORT, () => {
  console.log(`DengueSphere backend listening on port ${PORT}`);
});
