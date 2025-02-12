import os
import random
from typing import Dict, Any
from dotenv import load_dotenv
from locust import HttpUser, task, between

load_dotenv()

class HealthCheckTest(HttpUser):
    # 사용자 행동 간 대기 시간 (초 단위)
    wait_time: int = between(1, 3)

    @task(1)
    def health_check(self):
        self.client.get("/api/v1/common/health-check")
