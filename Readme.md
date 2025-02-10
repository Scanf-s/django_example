# 목차
1. 프로젝트 실행 방법
2. 캐시 전략 및 API 성능 테스트

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

## 이미지 빌드, 컨테이너 생성 및 백엔드 어플리케이션 실행
```shell
docker compose up --build -d
```

## 컨테이너 내부에 들어가고 싶다면
```shell
docker exec -it [컨테이너이름] /bin/bash
```

## 로그 보고 싶다면
```text
docker compose logs -f
```

## 컨테이너 중지, 삭제 방법
```shell
docker compose down
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

---

# 캐시 전략

### Book API에 캐시 적용하기

- /api/v1/books에 대해서만 캐시를 적용해보았습니다.
- /api/v1/book/{book_id} 또는 다른 도메인에 적용하는것에 대해서는 생략하였습니다.
- 만약 실제 프로덕션 레벨의 코드가 되기 위해서는 Book도메인 뿐만 아니라 
- 거의 동일한 응답을 내려주는 데이터의 경우를 탐색하여 모두 캐시를 적용한 뒤 테스트 코드를 작성하여 검증해야 합니다.

#### Redis를 지정하기 이전, API 속도

테스트 데이터셋으로 약 500개의 Book을 생성하여 SQLite3에 저장한 상태입니다.

![스크린샷 2025-02-11 00-21-57](https://github.com/user-attachments/assets/4a585cd5-f81d-4f57-973f-dc2eafc550a2)

참고로, API를 통해 총 500개의 데이터셋을 생성하는데 걸린 시간은 아래 사진과 같습니다.

![스크린샷 2025-02-11 01-33-51](https://github.com/user-attachments/assets/57766229-723a-4d80-bd01-0104619aea0e)

레디스를 적용하기 이전, Book에 대한 GET API 쿼리 시, 500개의 데이터셋을 모두 가져오는 경우 35ms ~ 48ms가 소요됩니다.
- /api/v1/books?page_size=500
  ![스크린샷 2025-02-11 00-23-57](https://github.com/user-attachments/assets/7bb81548-3312-4cc9-9ffd-ace24ba9fcc1)
  ![스크린샷 2025-02-11 00-23-21](https://github.com/user-attachments/assets/0b3f92d9-0234-491a-a377-b5dee2943533)

쿼리 파라미터를 적용하는 경우에 대한 예시 응답속도입니다.

(참고로 테스트 데이터를 Postman 스크립트를 사용하여 단순 반복으로 생성하였습니다. 따라서, 미흡한 데이터셋을 가지고 테스트하므로 count 개수가 계속 538로 뜹니다. 참고 바랍니다.)

- /api/v1/books?title=asdf&page_size=200
  ![스크린샷 2025-02-11 00-30-39](https://github.com/user-attachments/assets/ff56f0e5-c895-471c-b8a0-38a056e5bc7b)

- /api/v1/books?author=asdf&page_size=100
  ![스크린샷 2025-02-11 00-32-35](https://github.com/user-attachments/assets/909d7368-4e13-43bf-9a33-12d98da937eb)

- /api/v1/books?tag=1&tag=11&tag_option=and&page_size=100
  ![스크린샷 2025-02-11 00-33-01](https://github.com/user-attachments/assets/8d36fc00-6c2f-45a1-8c04-5445a1b679d2)

#### Redis를 적용하기 위한 전략

- 현재 Book API에는 title, author, tag_ids, tag_option, order_field, page_size에 대한 쿼리 파라미터를 받고 있습니다. 
- 단순히 아무 파라미터가 없는 요청에 대해서만 캐싱을 적용한다면, 다양한 사용자의 쿼리 요구사항에 맞출 수 없어서 Redis의 사용 의미가 없습니다. 
- 따라서, 각 쿼리 파라미터에 해당하는 key값을 Redis의 cache key로 지정해야 합니다. 
- 물론, Redis를 적용해도, 처음에는 무조건 Cache miss가 발생합니다.
- 그러나, Cache miss 이후 해당 데이터를 반환하기 전, Redis에 데이터를 저장해둔다면
- 이후 동일한 요청에 대해서는 Redis에서 Dictionary로 O(1)시간 안에 데이터를 꺼내오므로 네트워크 지연 시간, 코드 처리시간을 제외하면 매우 처리 속도가 감소할것이라고 예상하였습니다.
- Cache 전략을 적용한 뒤, 테스트 코드를 수정하였습니다. 테스트 환경은 Redis와 격리된 환경이기 때문에 unittest.mock 라이브러리를 사용하여 cache.get, set 함수를 mocking하였습니다.

#### Redis를 지정한 이후, API 속도

마찬가지로 테스트 데이터셋으로 약 500개의 Book을 생성하여 SQLite3에 저장한 상태입니다.

이번에는 레디스를 적용했을 때, 첫번째 요청(Cache miss)를 제외한 그 이외의 경우에 대해 응답 속도를 측정해보았습니다.
처음 Cache miss 시 40ms가 소요되었으나, 6ms로 감소한것을 확인할 수 있습니다.
- /api/v1/books?page_size=500
  ![스크린샷 2025-02-11 01-35-57](https://github.com/user-attachments/assets/f4f4fe37-fae6-407f-9178-4fa5c3b3c30a)


또 다른 예시로, 쿼리 파라미터를 적용하는 경우에 대한 예시 응답속도입니다.

- /api/v1/books?title=Book&page_size=200
  ![스크린샷 2025-02-11 01-37-03](https://github.com/user-attachments/assets/f23a8b0a-a788-4f36-ad43-9e9ac538cbf7)

- /api/v1/books?author=Author 23&page_size=200
  ![스크린샷 2025-02-11 01-38-23](https://github.com/user-attachments/assets/74e5d5a0-71f2-47c5-aeb7-07b8ee71499d)

- /api/v1/books?tag=1&tag=11&tag_option=and&page_size=100
  ![스크린샷 2025-02-11 01-39-11](https://github.com/user-attachments/assets/b2b51bb0-328b-4055-892f-a4dbd2d69ffe)


### Book API 캐시 무효화 구현하기

- 이전까지 구현한 API는 단순히 현재 존재하는 응답에 대해 캐시만 적용했을 뿐, 새로운 데이터가 추가되거나, 삭제, 업데이트 되는 경우를 고려하지 않았습니다.
- 따라서, 책 생성, 변경, 삭제 요청이 들어온 경우, 마지막 응답을 반환하기 전, 캐시를 무효화하도록 설정해주어야 합니다.
- GET을 구현할때에 비해 POST, PUT, PATCH, DELETE의 경우에는 단순히 현재 캐시에 대해서만 모두 무효화 해버리면 된다고 생각하였습니다.
- 하지만 실무에서는 이런 방식을 사용하지 않을 수도 있을 것 같은데, 어떻게 캐시 무효화를 구현하는지 궁금하네요!


