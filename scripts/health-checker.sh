export BACKEND_IMAGE=$(cat current-backend-image.txt)

# 컨테이너 만들어졌는지 확인
BACKEND_CONTAINER_ID=$(docker ps -q --filter "ancestor=$BACKEND_IMAGE")
if [ -n "$BACKEND_CONTAINER_ID" ]; then
  echo "✅ Container has created successfully"
else
  echo "❌ Container is not created. Failover to previous image"
  docker pull $ECR_REGISTRY/$ECR_REPOSITORY:stable
  export BACKEND_IMAGE="$ECR_REGISTRY/$ECR_REPOSITORY:stable"
  docker compose up -d
fi

# 컨테이너 실행중인지 확인
RUNNING_STATE=$(docker inspect -f '{{ .State.Running }}' "$BACKEND_CONTAINER_ID")
if [ -n "$RUNNING_STATE" ]; then
  echo "✅ RUNNING STATE Exists"
else
  echo "❌ Cannot inspect container's state"
  docker pull $ECR_REGISTRY/$ECR_REPOSITORY:stable
  export BACKEND_IMAGE="$ECR_REGISTRY/$ECR_REPOSITORY:stable"
  docker compose up -d
  exit 0
fi

if [ "$RUNNING_STATE" = "true" ]; then
  echo "✅ Container is running"
else
  echo "❌ Container is not running. Failover to previous image"
  docker pull $ECR_REGISTRY/$ECR_REPOSITORY:stable
  export BACKEND_IMAGE="$ECR_REGISTRY/$ECR_REPOSITORY:stable"
  docker compose up -d
fi

echo "✋ Sleep for a while... (30s)"
sleep 30s

# Django application이에서 오류 시 이전 docker 이미지인 stable 태그 이미지로 롤백
CONTAINER_STATUS=$(docker inspect -f '{{ .State.Status }}' "$BACKEND_CONTAINER_ID")
if [ "$CONTAINER_STATUS" =  "exited" ]; then
  echo "❌ Django has crashed"
  docker compose down
  docker pull $ECR_REGISTRY/$ECR_REPOSITORY:stable
  export BACKEND_IMAGE="$ECR_REGISTRY/$ECR_REPOSITORY:stable"
  docker compose up -d
else
  echo "✅ Django is running successfully. Create backup image"

  # stable 태그로도 이미지 생성
  docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:stable

  # stable 태그 이미지도 ECR로 PUSH (롤백 시 사용 예정)
  docker push $ECR_REGISTRY/$ECR_REPOSITORY:stable
  exit 0
fi