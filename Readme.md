# 목차

## 사전 구성

- 기존 3번 branch에서 진행했던 EC2에 존재하는 docker-compose.yml을 4번 branch의 scripts/docker-compose.yml로 대체합니다.
- prometheus, grafana, cadvisor 컨테이너가 필요하여, 구성이 변경되었습니다.
- terraform 또는 AWS 콘솔에서 library security group의 3000번 포트, 8080번 포트를 열어주세요

## Grafana Dashboard 예시

### Grafana Dashboard 접속 방법
- 본인의 Elastic IP 주소를 사용합니다.
- prometheus raw data를 보고싶다면 -> 본인EC2인스턴스:8000/metrics
- cadvisor raw data를 보고싶다면 -> 본인EC2인스턴스:8080/metrics
- grafana dashboard를 보고싶다면 -> 본인EC2인스턴스:3000 (초기 아이디/비번은 둘다 admin)

### Grafana Dashboard - API Metrics
- Grafana Dashboard JSON : https://grafana.com/grafana/dashboards/17658-django/

![image](https://github.com/user-attachments/assets/5de3cb6d-87e3-45e6-8f6a-ab71975ce027)

### Grafana Dashboard - System Metrics

#### CAdvisor (Container 별 지표)

- Grafana Dashboard JSON : https://grafana.com/grafana/dashboards/13946-docker-cadvisor/

![스크린샷 2025-02-12 15-00-05](https://github.com/user-attachments/assets/cef40bb7-7934-4fc5-8204-fc1ce3cee509)

#### Node Exporter (EC2 인스턴스 지표)

- Grafana Dashboard JSON : https://grafana.com/grafana/dashboards/1860-node-exporter-full/

![스크린샷 2025-02-12 15-00-47](https://github.com/user-attachments/assets/dbc8a151-356f-43e5-aa24-4fa37e618e8f)

### Grafana Dashboard - Stress Test
