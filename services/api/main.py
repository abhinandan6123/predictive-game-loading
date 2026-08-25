from fastapi import FastAPI

app = FastAPI(
    title="PulseLoad API",
    description="Predictive adaptive game loading system",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "pulseload-api",
        "status": "running",
    }
