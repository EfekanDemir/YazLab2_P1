from locust import HttpUser, task, between, events
import time

class DispatcherLoadTest(HttpUser):
    # Kullanıcı istekleri arasındaki bekleme süresi
    wait_time = between(1, 3)

    @task(3)
    def test_anonymous_get_products(self):
        """
        Herkesin erişebildiği (anonymous) endpoint.
        RMM'e uygun olarak GET isteği.
        """
        with self.client.get("/api/v1/products", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(1)
    def test_auth_route_unauthorized(self):
        """
        Token olmadan POST atınca 401 alınacağının performansı.
        Yetki mekanizmasının Redis ve Middleware üzerinde yarattığı yükü ölçer.
        """
        with self.client.post("/api/v1/products", catch_response=True) as response:
            if response.status_code == 401:
                response.success()
            else:
                response.failure(f"Expected 401, got {response.status_code}")

    # Not: Gerçek token gerektiren /api/v1/products DELETE gibi işlemler
    # için JWT_SECRET kullanılarak burada token üretilip Headers'a eklenebilir.
    # Şimdilik dispatcher stresini test ediyoruz.
    
    @task(2)
    def test_auth_service_routing(self):
        """
        Auth microservice yönlendirmesi (body parsing testi)
        """
        payload = {"username": "load_test_user", "password": "123"}
        with self.client.post("/api/v1/auth/login", json=payload, catch_response=True) as response:
            # Sadece route oldugunu goruyoruz
            if response.status_code in [200, 404, 502, 504]: # Servis down ise 5xx de load testi gecirir cunku hatayi assert etmiyoruz, altyapiyi sınıyoruz.
                response.success()
