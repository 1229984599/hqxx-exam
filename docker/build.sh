#!/bin/bash

# Docker构建脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
IMAGE_NAME="hqxx-exam"
IMAGE_TAG="latest"
CONTAINER_NAME="hqxx-exam-container"

echo -e "${BLUE}🐳 华侨小学考试系统 Docker 构建脚本${NC}"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 停止并删除现有容器
echo -e "${YELLOW}🛑 停止现有容器...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 删除现有镜像（可选）
read -p "是否删除现有镜像? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🗑️ 删除现有镜像...${NC}"
    docker rmi $IMAGE_NAME:$IMAGE_TAG 2>/dev/null || true
fi

# 构建镜像
echo -e "${BLUE}🔨 开始构建Docker镜像...${NC}"
docker build \
    --tag $IMAGE_NAME:$IMAGE_TAG \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 镜像构建成功！${NC}"
else
    echo -e "${RED}❌ 镜像构建失败${NC}"
    exit 1
fi

# 显示镜像信息
echo -e "${BLUE}📊 镜像信息:${NC}"
docker images $IMAGE_NAME:$IMAGE_TAG

# 询问是否立即运行
read -p "是否立即运行容器? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}🚀 启动容器...${NC}"
    
    # 运行容器
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p 80:80 \
        -v hqxx-exam-data:/app/data \
        $IMAGE_NAME:$IMAGE_TAG

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 容器启动成功！${NC}"
        echo -e "${GREEN}🌐 访问地址: http://localhost${NC}"
        echo -e "${GREEN}🔧 管理后台: http://localhost/admin${NC}"
        
        # 显示容器状态
        echo -e "${BLUE}📋 容器状态:${NC}"
        docker ps | grep $CONTAINER_NAME
        
        # 显示日志
        echo -e "${BLUE}📝 容器日志 (按Ctrl+C退出):${NC}"
        docker logs -f $CONTAINER_NAME
    else
        echo -e "${RED}❌ 容器启动失败${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}🎉 构建完成！${NC}"
