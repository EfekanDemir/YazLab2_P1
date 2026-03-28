import json
from pathlib import Path
from typing import Optional
from src.interfaces import IRouteStore

class JsonRouteStore(IRouteStore):
    def __init__(self, file_path: str = "src/routes.json"):
        self.file_path = Path(file_path)
        self.routes = self._load_routes()

    def _load_routes(self) -> dict:
        if not self.file_path.exists():
            return {}
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_target_url(self, path: str) -> Optional[str]:
        # En spesifik eşleşmeyi bulmak için (Örn: /api/v1/products)
        for route_prefix, target_url in self.routes.items():
            if path.startswith(route_prefix):
                # /api/v1/products/123 -> http://service-1-product:5002/api/v1/products/123
                return f"{target_url}{path}"
        return None
