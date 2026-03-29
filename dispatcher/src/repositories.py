import json
import redis
from typing import Optional, Dict
from src.interfaces import IRouteStore

class RedisRouteStore(IRouteStore):
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)

    def get_route_config(self, path: str, method: str) -> Optional[Dict]:
        """
        Redis tabanlı route yetki/proxy araması yapar.
        Prefix eşleşmesine odaklanır (Örn: /api/v1/products/123 -> /api/v1/products satırına uyar).
        """
        # Tüm muhtemel anahtarları al (Not: Yüksek trafikte bu kısım bir hash veya in-memory cache ile optimize edilmelidir.
        # Basitlik ve phase 3 gereği SCAN kullanıyoruz veya in-memory cache okuyoruz.)
        
        # Olası en iyi prefix'i bul
        parts = path.split("/")
        
        # /api/v1/products/123 döngü olarak /api/v1/products/123 -> /api/v1/products -> /api/v1 -> /api 
        # şeklinde en uzun eşleşmeyi arar.
        for i in range(len(parts), 0, -1):
            prefix = "/".join(parts[:i])
            if not prefix: prefix = "/"
            
            # Redis key format: route:/api/v1/products:GET
            key = f"route:{prefix}:{method}"
            val = self.redis_client.get(key)
            if val:
                config = json.loads(val)
                if config.get("is_active"):
                    # Hedef servisin path kısmını ekle.
                    # Örn target_service http://service-1-product:5002, original path: /api/v1/products/123
                    # Return payload is essentially the full config, proxy handler expects this info.
                    config["_calculated_target_url"] = f"{config['target_service']}{path}"
                    return config
        
        return None
