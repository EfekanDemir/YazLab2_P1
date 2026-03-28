from fastapi import FastAPI

app = FastAPI(title="Product Service", description="Manages Products inventory")

@app.get("/status")
def health_check():
    return {"service": "service-1-product", "status": "I am alive"}
