import json
import redis
import os

# Connect to redis container
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.StrictRedis.from_url(REDIS_URL)

routes = [
    {
        "route": "/api/v1/products",
        "method": "GET",
        "min_required_role": "anonymous",
        "target_service": "http://product-service:3000",
        "is_active": True
    },
    {
        "route": "/api/v1/products",
        "method": "POST",
        "min_required_role": "admin",
        "target_service": "http://product-service:3000",
        "is_active": True
    },
    {
        "route": "/api/v1/products",
        "method": "DELETE",
        "min_required_role": "admin",
        "target_service": "http://product-service:3000",
        "is_active": True
    },
    {
        "route": "/api/v1/auth/login",
        "method": "POST",
        "min_required_role": "anonymous",
        "target_service": "http://auth-service:5001",
        "is_active": True
    },
    {
        "route": "/api/v1/auth/register",
        "method": "POST",
        "min_required_role": "anonymous",
        "target_service": "http://auth-service:5001",
        "is_active": True
    },
    {
        "route": "/api/v1/reports",
        "method": "GET",
        "min_required_role": "customer",
        "target_service": "http://report-service:3000",
        "is_active": True
    }
]

def seed():
    for r_conf in routes:
        key = f"route:{r_conf['route']}:{r_conf['method']}"
        r.set(key, json.dumps(r_conf))
        print(f"Seeded: {key}")

if __name__ == "__main__":
    seed()
