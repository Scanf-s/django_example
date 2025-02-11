# 목차
1. 프로젝트 실행 방법
2. Terraform을 사용한 배포 환경 구성
3. CI/CD 설계 및 구현

# 사전 수행

****!!이 예시 어플리케이션을 제대로 사용하려면, Fork를 통해 본인의 레포지토리에서 진행해야 합니다!!****

# 1. Terraform을 사용한 배포환경 구성

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

# 2. 리소스 생성 후 EC2 설정

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

![스크린샷 2025-02-12 00-19-34](https://github.com/user-attachments/assets/ea8a903a-f045-4276-834d-c18fc96c95bc)

---

# 5. CI/CD 설계 및 구현

## Architecture preview

![image](https://github.com/user-attachments/assets/44dae9be-2382-44a1-af63-380fd913b49e)

## GitHub actions secret 설정

****!!Github actions를 사용하기 위해서는 사진과 같은 환경변수 지정이 반드시 필요합니다.!!****

![스크린샷 2025-02-12 00-53-48](https://github.com/user-attachments/assets/606a7ddb-941c-42da-b43c-7e31aceebb3e)

## CI 설계

### 가정
- 현재 구현한 백엔드 어플리케이션은 테스트코드가 40개정도입니다. 
- 만약 어떤 개발자가 테스트코드로 코드를 검증하지 않고 오류가 남아있는 채로 그냥 바로 Github에 PR을 올렸다면 
- 이를 PR 단계에서 Merge할 수 없도록 알려주어야 합니다.
- 이 백엔드 어플리케이션을 개발하는 모든 구성원은 코드 스타일 획일화를 위해 black 및 isort 라이브러리를 사용하여 코드 린팅을 수행해야 합니다.
- 뿐만 아니라, Github actions의 각 수행 결과를 자동으로 PR 메세지에 첨부하여, 어디 부분에서 실패했는지 확인할 수 있어야 합니다.

### 구현
- Github Actions를 사용하여 CI 스크립트를 작성하고, 위 가정을 만족하도록 구성해야 합니다.
- .github/workflows/integration.yml에 작성하였습니다.

## CD 설계

### 가정
- 현재 프로젝트는 docker와 docker compose를 사용합니다.
- 주로 AWS를 많이 사용해봐서, 익숙한 AWS에 배포하려고 합니다.
- AWS의 ECR에 백엔드 어플리케이션을 빌드한 도커 이미지를 PUSH해야하고, EC2인스턴스에는 따로 직접 구성해놓은 docker-compose.yml만 있으면 됩니다.
- 또한, docker-compose.yml을 그대로 사용하기보다, docker-compose-prod.yml을 따로 서버측에 구성해두어서 서버전용 환경 변수를 편집하는것이 바람직합니다.
- 또한 aws credential 설정 및 ecr로부터 이미지 다운로드, docker-compose.yml을 실행하는 스크립트를 작성해야 합니다. 이는 하단의 deploy.sh를 참고해주세요
- AWS 비용문제가 발생할 수 있기 때문에 도메인 연결, HTTPS 적용은 하지 않았으며, 프리티어 범위에서 단순히 필요한 리소스만 사용하여 구현하였습니다.
  - 단, Public 통신 시 AWS 정책에 의해 비용이 부과되는 점 참고 바랍니다.
- 성공적으로 컨테이너를 올렸을 때, Health check를 위해 Docker 자체 기능인 Health checker를 사용하여 컨테이너의 실행 여부를 확인할 수 있습니다.
- 또한, 롤백을 구현하기 위해 쉘 스크립트를 활용하여 실패시 이전 성공 이미지인 stable tag 이미지를 PULL 하여 다시 컨테이너를 올려야 합니다.

### 구현
- Github Actions를 사용하여 CD 스크립트를 작성하고, 위 가정을 만족하도록 구성해야 합니다.
- .github/workflows/deployment.yml에 작성하였습니다.

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

### Github Actions 실행 결과

![스크린샷 2025-02-12 01-15-29](https://github.com/user-attachments/assets/7949f082-e91f-40d4-9480-9163213c5333)

![스크린샷 2025-02-12 01-15-44](https://github.com/user-attachments/assets/5d3a7d34-ffec-453a-9c37-dc838b4aae7f)

![스크린샷 2025-02-12 01-18-31](https://github.com/user-attachments/assets/b000d90a-f322-478a-bce9-a64490f37490)

![스크린샷 2025-02-12 01-18-39](https://github.com/user-attachments/assets/cbcac076-6d63-4a8c-8b9f-7c5d1f18d7cf)

![스크린샷 2025-02-12 01-18-45](https://github.com/user-attachments/assets/65770294-6888-4d7c-9406-1b56faa12fd9)

![스크린샷 2025-02-12 01-19-02](https://github.com/user-attachments/assets/9525a5c0-47e6-47ae-9042-a0b5335b46ea)

### 컨테이너 실행 결과

![스크린샷 2025-02-12 01-31-03](https://github.com/user-attachments/assets/9c6b7e62-4e0e-42b3-ad18-7c8fb5760e99)

### 배포 환경 API 실행 결과

![스크린샷 2025-02-12 01-32-51](https://github.com/user-attachments/assets/ff39881e-ec6c-41cf-89cf-1fd7767c779e)

![스크린샷 2025-02-12 01-33-05](https://github.com/user-attachments/assets/10624380-44e7-4f04-9152-71fa480c619f)

![스크린샷 2025-02-12 01-33-29](https://github.com/user-attachments/assets/2610ee77-6ec2-48aa-8b84-fa32f4e82d45)

![스크린샷 2025-02-12 01-34-06](https://github.com/user-attachments/assets/9dbda8fb-4acc-4728-911e-57e63fcc135e)



