import random
from locust import HttpUser, task, between

class ProjectUser(HttpUser):
    # Kullanıcılar arası bekleme süresi (1-3 saniye)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Kullanıcı başladığında login olur ve token alır."""
        self.login()

    def login(self):
        login_data = {
            "username": "testuser_final",
            "password": "Test1234"
        }
        with self.client.post("/api/v1/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")

    @task(3)
    def view_products(self):
        """Ürünleri listele (Ağırlık: 3)"""
        if hasattr(self, 'headers'):
            self.client.get("/api/v1/products", headers=self.headers)

    @task(1)
    def re_login(self):
        """Ara sıra tekrar login yükü bindir (Ağırlık: 1)"""
        self.login()
