from fastapi import FastAPI

app = FastAPI(title="Order Service", description="Manages Orders")

@app.get("/status")
def health_check():
    return {"service": "service-2-order", "status": "I am alive"}
