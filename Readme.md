# 목차

## 사전 구성

- 기존 3번 branch에서 진행했던 EC2에 존재하는 docker-compose.yml을 4번 branch의 scripts/docker-compose.yml로 대체합니다.
- prometheus, grafana, cadvisor 컨테이너가 필요하여, 구성이 변경되었습니다.

## Grafana Dashboard 예시

### Grafana Dashboard 접속 방법
- 본인의 Elastic IP 주소를 사용합니다.
- prometheus raw data를 보고싶다면 -> 127.0.0.1:8000/metrics
- cadvisor raw data를 보고싶다면 -> 127.0.0.1:8080/stats/prometheus
- grafana dashboard를 보고싶다면 -> 127.0.0.1:3000 (초기 아이디/비번은 둘다 admin)

### Grafana Dashboard - API Metrics

### Grafana Dashboard - System Metrics

### Grafana Dashboard - Stress Test
