import uuid
import time
import logging
import os
import jwt
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from src.repositories import RedisRouteStore
from src.proxy import forward_request

app = FastAPI(title="Dispatcher API Gateway (Secure & Monitored)")

# ----------------- PROMETHEUS METRICS -----------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Toplam HTTP istek sayisi",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP isteklerinin tamamlanma suresi (saniye)",
    ["method", "endpoint"]
)

# Redis URL and generic JWT Key
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
JWT_SECRET = os.getenv("JWT_SECRET", "test_secret_for_jwt")
route_store = RedisRouteStore(REDIS_URL)

# ----------------- LOGGING SETUP -----------------
# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("dispatcher-logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # File handler for Loki/Promtail to tail
    fh = logging.FileHandler("logs/dispatcher.log")
    fh.setLevel(logging.INFO)
    logger.addHandler(ch)
    logger.addHandler(fh)

# ----------------- STANDART HATA JSON -----------------
def standard_error_response(message: str, code: int, details: dict = None):
    return JSONResponse(
        status_code=code,
        content={"error": message, "code": code, "details": details or {}}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return standard_error_response(exc.detail, exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return standard_error_response("Validation Error", 422, exc.errors())

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return standard_error_response("Internal Server Error", 500, {"message": str(exc)})

# ----------------- MIDDLEWARE PIPELINE -----------------
@app.middleware("http")
async def chain_of_responsibility_middleware(request: Request, call_next):
    # Metrics icin endpointi basitlestirelim (eg. /api/v1/products/123 -> /api/v1/products)
    # Promtail/Metrics icin path cardinality kisitlamasi onemlidir.
    
    # Eger metrics istediysek direkt gecir
    if request.url.path == "/metrics":
        return await call_next(request)
        
    request_id = str(uuid.uuid4())
    start_time = time.time()
    user_id = None
    user_role = "anonymous"
    auth_status = "SUCCESS"

    # 1. Routing Bilgisini Redis'ten Al
    route_config = route_store.get_route_config(request.url.path, request.method)
    
    # 2. Yetki, Role & Security Pass (Eğer rota mevcutsa)
    if route_config:
        min_required_role = route_config.get("min_required_role")
        
        if min_required_role and min_required_role != "anonymous":
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                auth_status = "FAILED"
                logger.warning(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{request_id}] -> 401 Unauthorized (No Token)")
                return standard_error_response("Unauthorized: Missing or invalid Bearer token", 401)
            
            token = auth_header.split(" ")[1]
            try:
                # Token Doğrulama
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                user_id = payload.get("sub")
                user_role = payload.get("role")
                
                # RBAC Kontrolü (Basit Eşitlik Mantığı - Seviye eklenebilir)
                if user_role != min_required_role and user_role != "admin":
                    auth_status = "FORBIDDEN"
                    logger.warning(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{request_id}] -> 403 Forbidden (Insufficient Role: {user_role})")
                    return standard_error_response("Forbidden: Insufficient role permissions", 403)
                    
            except jwt.ExpiredSignatureError:
                auth_status = "FAILED_EXPIRED"
                return standard_error_response("Unauthorized: Token has expired", 401)
            except jwt.InvalidTokenError:
                auth_status = "FAILED_INVALID"
                return standard_error_response("Unauthorized: Invalid token", 401)
    
    # 3. İsteği Zenginleştir (Enrichment)
    request.state.user_id = user_id
    request.state.user_role = user_role
    
    # Hedef servis yoksa 404 dönecek
    display_target = route_config.get("target_service", "UNKNOWN") if route_config else "UNKNOWN"

    response = None
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        logger.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{request_id}] -> ERROR: {str(e)}")
        raise
    finally:
        # Structured Logging at Exit
        duration_s = time.time() - start_time
        duration_ms = int(duration_s * 1000)
        
        # Metric Cardinality azaltmak icin ana path i yakalayalim (/api/v1/products/1 -> /api/v1/products)
        metric_path = request.url.path
        if metric_path.startswith("/api/v1/products"): metric_path = "/api/v1/products"
        elif metric_path.startswith("/api/v1/orders"): metric_path = "/api/v1/orders"
        elif metric_path.startswith("/api/v1/auth"): metric_path = "/api/v1/auth"
        else: metric_path = "other"

        REQUEST_COUNT.labels(method=request.method, endpoint=metric_path, status=status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=metric_path).observe(duration_s)

        log_entry = {
            "request_id": request_id,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "auth": auth_status,
            "user_role": user_role,
            "path": request.url.path,
            "duration_ms": duration_ms,
            "status_code": status_code
        }
        import json
        logger.info(json.dumps(log_entry))

# ----------------- STATUS & METRICS & CATCH-ALL ROUTE -----------------
@app.get("/status")
def health_check():
    return {"service": "dispatcher", "status": "I am alive"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all_proxy(path: str, request: Request):
    full_path = request.url.path
    route_config = route_store.get_route_config(full_path, request.method)
    
    if not route_config:
        raise HTTPException(status_code=404, detail="Route Not Found")
        
    target_url = route_config.get("_calculated_target_url")
    
    # Enrichment - Başlıkları klonlayıp ekleyelim
    enriched_headers = dict(request.headers)
    if hasattr(request, "state"):
        if getattr(request.state, "user_id", None):
             enriched_headers["X-User-Id"] = request.state.user_id
        if getattr(request.state, "user_role", None):
             enriched_headers["X-User-Role"] = request.state.user_role
             
    # Proksiye aktar
    return await forward_request(request, target_url, override_headers=enriched_headers)
