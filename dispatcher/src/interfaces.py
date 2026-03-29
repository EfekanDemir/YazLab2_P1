from abc import ABC, abstractmethod
from typing import Optional, Dict

class IRouteStore(ABC):
    @abstractmethod
    def get_route_config(self, path: str, method: str) -> Optional[Dict]:
        """
        Döner structure örneği:
        {
          "route": "/api/products",
          "method": "DELETE",
          "min_required_role": "admin",
          "target_service": "http://service-1-product:5002",
          "is_active": true
        }
        """
        pass
