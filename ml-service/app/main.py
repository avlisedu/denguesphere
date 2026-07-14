from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cluster, geocode

app = FastAPI(title="DengueSphere ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # internal service, only called by the Node backend
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(geocode.router)
app.include_router(cluster.router)


@app.get("/health")
def health():
    return {"status": "ok"}
