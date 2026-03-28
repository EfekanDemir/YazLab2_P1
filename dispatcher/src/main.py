from fastapi import FastAPI

app = FastAPI(title="Dispatcher Gateway", description="Central API Gateway for the Microservices")

@app.get("/status")
def health_check():
    return {"service": "dispatcher", "status": "I am alive"}
