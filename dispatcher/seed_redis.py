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
        "target_service": "http://service-1-product:5002",
        "is_active": True
    },
    {
        "route": "/api/v1/products",
        "method": "POST",
        "min_required_role": "admin",
        "target_service": "http://service-1-product:5002",
        "is_active": True
    },
    {
        "route": "/api/v1/products",
        "method": "DELETE",
        "min_required_role": "admin",
        "target_service": "http://service-1-product:5002",
        "is_active": True
    },
    {
        "route": "/api/v1/auth",
        "method": "POST",
        "min_required_role": "anonymous",
        "target_service": "http://auth-service:5001",
        "is_active": True
    },
    {
        "route": "/api/v1/orders",
        "method": "GET",
        "min_required_role": "customer",
        "target_service": "http://service-2-order:5003",
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
