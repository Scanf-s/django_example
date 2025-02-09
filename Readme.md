# 실행 방법

## 프로젝트 루트 디렉토리에 .env 파일 생성
```text
# Django
SECRET_KEY=원하는 시크릿 키

# JWT
AUTH_HEADER=Bearer
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=원하는 시크릿 키
```

## 도커 이미지 빌드
```shell
docker build . -t [원하는이미지이름]
``` 

## 컨테이너 생성 및 백엔드 어플리케이션 실행
```shell
docker run -d -p 8000:8000 --name [원하는컨테이너이름] [빌드한이미지이름]
```

## 컨테이너 내부에 들어가고 싶다면
```shell
docker exec -it [컨테이너이름] /bin/bash
```

## 로그 보고 싶다면
```text
docker logs -f [컨테이너이름]
```

## 컨테이너 중지, 삭제 방법
```shell
docker container stop [컨테이너이름]
docker container rm [컨테이너이름]
```

## 백엔드 어플리케이션 테스트 방법 (Postman or Curl)

- OAS 3.1 기반 REST_API_SPEC.yaml을 사용하여 API 엔드포인트 확인 
- Base URL
  1) http://localhost:8000/api/v1
  2) http://127.0.0.1:8000/api/v1

## 토큰 발급 받는 방법
### 회원가입
![image](https://github.com/user-attachments/assets/48599f7c-0bec-49fc-a406-01767b391de5)

### 로그인 (토큰 발급)
![image](https://github.com/user-attachments/assets/237d44e6-ae2c-4ae1-b036-bf3115a0e5be)
