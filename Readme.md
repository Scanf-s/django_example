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

#### Locust 구성

1. .env 파일에 아래 항목 저장
```text
TOKEN=로그인해서발급받은JWT ACCESS TOKEN
```

2. Locust 실행 시
```shell
locust -f 요청파일경로 --host=http://IP:8000
```
- 뒤에 host 인자는 부하테스트할 대상 경로입니다 (EC2 IP 넣어주면 됨)

#### 미리 Postman으로 1000개의 랜덤 책 데이터 생성

![image](https://github.com/user-attachments/assets/6839fef7-3f27-486f-8802-077cb8cdfe36)

#### 1-1. 단순한 Health-check API를 사용한 Application 자체 부하 테스트

![image](https://github.com/user-attachments/assets/7dbc160f-e724-4ea6-9eb6-4ceed29101e0)

#### 1-2. Locust UI 확인

![image](https://github.com/user-attachments/assets/7e010b01-e37c-43ed-ab9c-1512e5842f8f)
![image](https://github.com/user-attachments/assets/30c9d801-f753-4f38-b235-4650375c7064)

- 비즈니스 로직이 존재하지 않는 API에 대해서, t2.micro 인스턴스 하나만으로 1000명의 동시접속자를 처리할 수 있다

#### 1-3. Grafana 지표 확인
![image](https://github.com/user-attachments/assets/c6df3b36-dc62-4e8b-b657-bc3e9087dc50)
- 부하 테스트가 끝나고 찍어서 정확하지 않음

#### 2-1. GET - /books 부하 테스트
- 캐시가 적용되어있음을 감안
  
#### 2-2. Locust UI 확인
![image](https://github.com/user-attachments/assets/e24ad8f5-f235-4bff-a665-ce09b4d8e0b3)

![image](https://github.com/user-attachments/assets/7d0be7bd-5f3a-4a81-83b8-d7bda21d3dc6)
- Failure가 처음으로 발생한 지점은, 동시 사용자 수가 500명정도일 때 처음 발생하였음
- Redis를 통해 /books 엔드포인트에 대한 캐싱을 적용하게 되어 t2.micro임에도 준수한 성능을 보여주고 있음
- 만약 인프라 측면에서 Scale out, up을 수행한다면 더 많은 동시접속자 수를 처리할 수 있을것이라고 전망

#### 2-3. Grafana 지표 확인
![image](https://github.com/user-attachments/assets/9dcdfeaf-5aa0-4352-bf8b-9d82a44582c6)
- 그림과 같이 CPU, Sys load 지표가 100퍼센트에 가까이 되면서부터 지연이 크게 발생함 -> 50th, 95th percentile 지표에서 확인이 가능하였음






