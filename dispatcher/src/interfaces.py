from abc import ABC, abstractmethod
from typing import Optional

class IRouteStore(ABC):
    @abstractmethod
    def get_target_url(self, path: str) -> Optional[str]:
        """Path'e karşılık gelen hedef servis URL'sini döner."""
        pass

class IAuthRepository(ABC):
    @abstractmethod
    def verify_token(self, token: str) -> bool:
        """İleride Redis'den Auth verify yapmak için kullanılacak placeholder."""
        pass
