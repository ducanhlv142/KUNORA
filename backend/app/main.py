from fastapi import FastAPI

app = FastAPI(
    title="Kunora API",
    description="Market Intelligence Platform API",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"name": "KUNORA API",
            "version": "0.1.0",
            "status": "online",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}