import uuid
import time
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.repositories import JsonRouteStore
from src.proxy import forward_request

app = FastAPI(title="Dispatcher API Gateway")
route_store = JsonRouteStore()

# ----------------- LOGGING MIDDLEWARE -----------------
logger = logging.getLogger("dispatcher-logger")
logger.setLevel(logging.INFO)
# Konsol çıktısı formatı için handler
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Yönlendirme hedefi tespiti
    target_url = route_store.get_target_url(request.url.path)
    # Konsola target logu basmak için hazırlık
    display_target = target_url if target_url else "UNKNOWN"

    response = None
    try:
        response = await call_next(request)
        response_time_ms = int((time.time() - start_time) * 1000)
        status_code = response.status_code
        
        # [TIMESTAMP] [REQUEST_ID] [METHOD] [PATH] -> [TARGET_SERVICE] [STATUS_CODE] [RESPONSE_TIME_MS]
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{request_id}] [{request.method}] [{request.url.path}] -> [{display_target}] [{status_code}] [{response_time_ms}ms]")
        
        return response
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{request_id}] [{request.method}] [{request.url.path}] -> [{display_target}] [500] [{response_time_ms}ms] ERROR: {str(e)}")
        raise

# ----------------- STANDART HATA JSON -----------------
def standard_error_response(message: str, code: int, details: dict = None):
    return JSONResponse(
        status_code=code,
        content={"error": message, "code": code, "details": details or {}}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return standard_error_response(exc.detail, exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return standard_error_response("Validation Error", 422, exc.errors())

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return standard_error_response("Internal Server Error", 500, {"message": str(exc)})


# ----------------- STATUS & CATCH-ALL ROUTE -----------------
@app.get("/status")
def health_check():
    return {"service": "dispatcher", "status": "I am alive"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all_proxy(path: str, request: Request):
    # Yolun başında '/' var mı diye kontrol et ve original path'i koru
    full_path = request.url.path
    
    target_url = route_store.get_target_url(full_path)
    
    if not target_url:
        raise HTTPException(status_code=404, detail="Route Not Found")
    
    # Proksi isteğini at ve cevabı geri dön
    return await forward_request(request, target_url)
