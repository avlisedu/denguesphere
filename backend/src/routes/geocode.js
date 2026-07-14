import { Router } from "express";
import multer from "multer";

import { forwardToMlService, getFromMlService } from "../mlServiceClient.js";
import { sendMlServiceError } from "../mlServiceError.js";

const upload = multer({ storage: multer.memoryStorage() });
const router = Router();

router.post("/preview", upload.single("file"), async (req, res) => {
  try {
    const data = await forwardToMlService("/geocode/preview", req.file);
    res.json(data);
  } catch (error) {
    sendMlServiceError(res, error);
  }
});

router.post("/process", upload.single("file"), async (req, res) => {
  try {
    const { cep_col, rua_col, bairro_col } = req.body;
    const data = await forwardToMlService("/geocode/process", req.file, {
      cep_col,
      rua_col,
      bairro_col,
    });
    res.json(data);
  } catch (error) {
    sendMlServiceError(res, error);
  }
});

router.get("/process/:jobId", async (req, res) => {
  try {
    const data = await getFromMlService(`/geocode/process/${req.params.jobId}`);
    res.json(data);
  } catch (error) {
    sendMlServiceError(res, error);
  }
});

export default router;
