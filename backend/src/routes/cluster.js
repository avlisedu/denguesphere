import { Router } from "express";
import multer from "multer";

import { forwardToMlService } from "../mlServiceClient.js";
import { sendMlServiceError } from "../mlServiceError.js";

const upload = multer({ storage: multer.memoryStorage() });
const router = Router();

router.post("/periods", upload.single("file"), async (req, res) => {
  try {
    const data = await forwardToMlService("/cluster/periods", req.file);
    res.json(data);
  } catch (error) {
    sendMlServiceError(res, error);
  }
});

router.post("/process", upload.single("file"), async (req, res) => {
  try {
    const { eps_km, min_samples, ano, semanas, include_stability } = req.body;
    const data = await forwardToMlService("/cluster/process", req.file, {
      eps_km,
      min_samples,
      ano,
      semanas,
      include_stability,
    });
    res.json(data);
  } catch (error) {
    sendMlServiceError(res, error);
  }
});

export default router;
