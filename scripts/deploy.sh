# AWS ECR Login
echo "🚀 Login to ECR ....."
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $ECR_REGISTRY
echo "✅ Successfully Logged in"

# Docker 작업
echo "📦 Pull Latest Image from ECR Registry ....."
docker pull $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG || { echo "❌ Failed to download latest image from resgistry"; exit 1; }
echo "✅ Done"

# .env 파일 확인
if [ ! -f ~/.env  ]; then
        echo "⚠️  .env file must be in EC2 😱😱😱"
        exit 1
fi

echo "✋ Stop and remove current container ....."
docker compose down
echo "✅ Done"

echo "🧹 Clear unused docker conatiners and images ....."
docker container prune -f
docker image prune -f
echo "✅ Done"

echo "🚀 Run new container ....."
docker compose pull
docker compose up -d
echo "🎉 Done"
