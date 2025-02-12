import os
import random
from typing import Dict, Any
from dotenv import load_dotenv
from locust import HttpUser, task, between

load_dotenv()

class GetBooks(HttpUser):
    # 사용자 행동 간 대기 시간 (초 단위)
    wait_time: int = between(1, 3)

    def auth_headers(self) -> Dict:
        if not os.getenv("TOKEN"):
            exit(0)

        return {
            "Authorization": f"Bearer {os.getenv('TOKEN')}"
        }

    @task(1)
    def get_books(self) -> None:
        # 도서 리스트 조회 시, 임의의 쿼리 파라미터 전달해서 테스트
        params: Dict[str, Any] = {
            "title": f"Book {random.randint(1, 10000)}",  # 임의의 제목 검색어
            "author": f"Author {random.randint(1, 100)}",   # 임의의 작가 검색어
            "tag": random.choice([str(i) for i in range(1, 16)]),  # 1~15 중 임의의 태그 (문자열)
            "tag_option": random.choice(["and", "or"]),
            "page_size": random.randint(1, 50),
            "order_by": random.choice(["title", "-title", "published_at", "-published_at"])
        }
        self.client.get("/api/v1/books", params=params, headers=self.auth_headers())
