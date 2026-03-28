from fastapi import FastAPI

app = FastAPI(title="Auth Service", description="Handles JWT Generation and Verification")

@app.get("/status")
def health_check():
    return {"service": "auth-service", "status": "I am alive"}
