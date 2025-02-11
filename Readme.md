# 목차
1. 프로젝트 실행 방법
2. 캐시 전략 및 API 성능 테스트
3. Terraform을 사용한 배포 환경 구성
4. CI/CD 설계 및 구현

# 사전 수행

****!!이 예시 어플리케이션을 제대로 사용하려면, Fork를 통해 본인의 레포지토리에서 진행해야 합니다!!****

# 1. 실행 방법

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

# 2. 캐시 전략

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

---

# 3. Terraform을 사용한 배포환경 구성

## Prerequisites
1. Terraform을 사용하기 위해서는, 본인의 컴퓨터에 Terraform을 설치해야 합니다. 설치 방법은 검색을 통해 알아서 설치해주세요
2. 뿐만 아니라 AWS 계정이 있어야 하며, AWS IAM User의 access token과 secret token이 필요합니다.
   - IAM User를 생성하여 AdministratorAccess Policy를 연결해주세요 (어떤 권한이 필요한지 안다면, 직접 하나씩 지정해서 권한을 넣어주세요)
   - 이 User는 이후 CI/CD 파이프라인에서도 사용합니다.
3. AWS CLI가 본인 컴퓨터에 설치되어 있어야 합니다. Terraform에서 IAM User의 token을 자동으로 불러오기 위해서는, aws credentials 설정을 수행해야 합니다.
   - aws cli 설치 후, aws configure를 콘솔에 입력하여 IAM User의 Access/Secret key를 설정해주세요
4. AWS 계정에 미리 EC2 SSH 접속을 위한 Key pair를 생성해야 합니다. Key pair 생성 시 이름을 "library"로 만들어주세요
5. 또한, terraform/prod.tfvars 파일을 생성해줍니다. 해당 파일 안에 아래 내용을 입력해줍시다
```terraform
your_computer_ipv4_address = "ip address in your computer/32"

# For example
# your_computer_ipv4_address = "1.1.1.1/32"
```

## 참고
- key pair 권한 오류가 발생하면 (chmod 400 keypair) 명령을 사용해서 권한을 수정해주세요
- 본인 컴퓨터의 IP가 바뀌게 되면 EC2 인스턴스로 접근이 불가능합니다. 
- 이때는 prod.tfvars를 다시 수정 후 terraform plan, apply를 해주시면 됩니다.

### Ubuntu 기준

```shell
# 1. move to project_dir/terraform
cd path-to-project/terraform

# 2. terraform plugin 설치
terraform init

# 3. terraform 실행
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars" # 입력창 뜨면 yes 입력 또는 -auto-approve

# 4. 만든거 모두 삭제하고 싶으면 (싹 삭제되니까 걱정하지마세요)
terraform destroy -var-file="prod.tfvars" # 입력창 뜨면 yes 입력 또는 -auto-approve
```

---

# 4. 리소스 생성 후 EC2 설정

## 사전 설정

- 아래 과정은 미리 EC2에서 진행하여, AMI를 만들어두면 추후 다른 프로젝트 진행 시 매우 도움이 됩니다!!

### 1. Terraform으로 생성한 EC2에 SSH에 접속

### 2. EC2에 프로젝트의 scripts 아래에 있는 모든 파일을 복사해서 넣어줍니다.

### 3. 권한 수정
```shell
chmod 744 deploy.sh
chmod 744 health-checker.sh
```

### 4. EC2에 Docker 설치
```shell
sudo yum install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user
exec bash

# 아래 명령이 잘 실행되는지 확인
docker run hello-world

# docker compose 설치
sudo mkdir -p /usr/local/lib/docker/cli-plugins/
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 설치 잘 되었는지 확인
docker compose version
```

### 5. aws configure 명령 실행
- IAM User의 access key, secret key, aws region 정보를 넣어주시면 됩니다.

### 6. .env 파일 생성
```text
# Django
SECRET_KEY=배포환경에서 사용할 시크릿 키

# JWT
AUTH_HEADER=Bearer
JWT_ALGORITHM=JWT 알고리즘 지정
JWT_SECRET_KEY=배포환경에서 사용할 JWT 시크릿 키
```

### 7. 전부 다 구성하였다면, 아래와 같이 나옵니다.
(ec2 캡쳐 화면)

---

# 5. CI/CD 설계 및 구현

## Architecture preview

![image](https://github.com/user-attachments/assets/44dae9be-2382-44a1-af63-380fd913b49e)

## GitHub actions secret 설정

****!!Github actions를 사용하기 위해서는 사진과 같은 환경변수 지정이 반드시 필요합니다.!!****

(GitHub secret 화면)

## CI 설계

### 구현 과정
- 현재 구현한 백엔드 어플리케이션은 테스트코드가 40개정도입니다. 
- 만약 어떤 개발자가 테스트코드로 코드를 검증하지 않고 오류가 남아있는 채로 그냥 바로 Github에 PR을 올렸다면 
- 이를 PR 단계에서 Merge할 수 없도록 알려주어야 합니다.
- 이 백엔드 어플리케이션을 개발하는 모든 구성원은 코드 스타일 획일화를 위해 black 및 isort 라이브러리를 사용하여 코드 린팅을 수행해야 합니다.
- 뿐만 아니라, Github actions의 각 수행 결과를 자동으로 PR 메세지에 첨부하여, 어디 부분에서 실패했는지 확인할 수 있어야 합니다.

### 구현
- Github Actions를 사용하여 CI 스크립트를 작성하고, 위 가정을 만족하도록 구성해야 합니다.
- .github/workflows/integration.yml에 작성하였습니다.

## CD 설계

### 구현 과정
- 현재 프로젝트는 docker와 docker compose를 사용합니다.
- 주로 AWS를 많이 사용해봐서, 익숙한 AWS에 배포하려고 합니다.
- AWS의 ECR에 백엔드 어플리케이션을 빌드한 도커 이미지를 PUSH해야하고, EC2인스턴스에는 따로 직접 구성해놓은 docker-compose.yml과 .env만 있으면 됩니다.
- 또한 aws credential 설정 및 ecr로부터 이미지 다운로드, docker-compose.yml을 실행하는 쉘 스크립트를 작성해야 합니다.
- AWS 비용문제가 발생할 수 있기 때문에 도메인 연결, HTTPS 적용은 하지 않았으며, 프리티어 범위에서 단순히 필요한 리소스만 사용하여 구현하였습니다.
  - 단, Public 통신 시 AWS 정책에 의해 비용이 부과되는 점 참고 바랍니다.
- 성공적으로 컨테이너를 올렸을 때, Health check를 위해 Docker 자체 기능인 Health checker를 사용하여 컨테이너의 실행 여부를 확인할 수 있습니다.
- 또한, 롤백을 구현하기 위해 쉘 스크립트를 활용하여 실패시 이전 성공 이미지인 stable tag 이미지를 PULL 하여 다시 컨테이너를 올려야 합니다.

### 구현
- scripts/deploy.sh
- scripts/docker-compose.yml
- scripts/health-checker.sh
- .github/workflows/deployment.yml

### AWS 관련
- EC2는 Private subnet에 위치시키는 것이 맞으나, NAT 게이트웨이를 따로 구성해야하고 추가적으로 설정을 해주어야 하기 때문에 Public subnet에 위치시켰습니다.
- 단순히 Elastic IP를 하나 할당하였으며, SSH, Django application port 연결을 위해 Security group을 구성하였습니다.
- 본래 Elastic IP는 잘 사용하지 않으나, 고정된 IP가 필요하므로 사용하였습니다.
- 현재 데이터베이스를 Docker 내부에 존재하는 sqlite3를 사용하고 있습니다. 때문에 컨테이너를 내리고 올릴때마다 새로 sqlite 파일이 생성되므로, 초기화됩니다.
- 이 문제를 해결하려면 RDS를 사용하거나 docker volume을 사용해서 sqlite를 EC2에 기록해 두도록 하면 됩니다.

## Deploy failover 전략
- EC2에 있는 shell script 실행 중 docker compose 컨테이너를 내려버리고, 다시 올려버리는 과정을 수행합니다.
- 만약 스크립트 실행 후 컨테이너 헬스 체크에 오류가 발생했다면, 기존 컨테이너를 다시 내리고
- 이전 버전의 도커 이미지를 ECR에서 가져와서 컨테이너를 올리도록 쉘 스크립트를 작성해주면 됩니다.

## 구현 후 실제 실행 화면

(이미지)
