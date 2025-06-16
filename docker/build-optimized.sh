#!/bin/bash

# Docker 优化构建脚本
# 支持多架构构建和缓存优化

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 默认配置
IMAGE_NAME="hqxx-exam"
TAG="latest"
PLATFORMS="linux/amd64,linux/arm64"
CACHE_FROM=""
CACHE_TO=""
PUSH=false
BUILD_ARGS=""

# 帮助信息
show_help() {
    cat << EOF
Docker 优化构建脚本

用法: $0 [选项]

选项:
    -n, --name NAME         镜像名称 (默认: hqxx-exam)
    -t, --tag TAG          镜像标签 (默认: latest)
    -p, --platforms PLATFORMS  目标平台 (默认: linux/amd64,linux/arm64)
    --push                 构建后推送到仓库
    --cache-from CACHE     从缓存拉取 (例如: type=registry,ref=myregistry/cache)
    --cache-to CACHE       推送缓存到 (例如: type=registry,ref=myregistry/cache)
    --build-arg ARG        构建参数 (可多次使用)
    -h, --help             显示帮助信息

示例:
    $0 --name myapp --tag v1.0.0 --push
    $0 --platforms linux/amd64 --cache-from type=local,src=/tmp/cache
    $0 --build-arg VERSION=1.0.0 --build-arg ENV=production
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --cache-from)
            CACHE_FROM="--cache-from $2"
            shift 2
            ;;
        --cache-to)
            CACHE_TO="--cache-to $2"
            shift 2
            ;;
        --build-arg)
            BUILD_ARGS="$BUILD_ARGS --build-arg $2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查 Docker Buildx
check_buildx() {
    log_info "检查 Docker Buildx..."
    if ! docker buildx version >/dev/null 2>&1; then
        log_error "Docker Buildx 未安装或不可用"
        exit 1
    fi
    log_success "Docker Buildx 可用"
}

# 创建构建器
create_builder() {
    log_info "创建多架构构建器..."
    
    # 检查是否已存在构建器
    if docker buildx ls | grep -q "hqxx-builder"; then
        log_info "使用现有构建器: hqxx-builder"
        docker buildx use hqxx-builder
    else
        log_info "创建新构建器: hqxx-builder"
        docker buildx create --name hqxx-builder --driver docker-container --use
        docker buildx inspect --bootstrap
    fi
}

# 构建镜像
build_image() {
    log_info "开始构建镜像..."
    log_info "镜像名称: $IMAGE_NAME:$TAG"
    log_info "目标平台: $PLATFORMS"
    
    # 构建命令
    BUILD_CMD="docker buildx build"
    BUILD_CMD="$BUILD_CMD --platform $PLATFORMS"
    BUILD_CMD="$BUILD_CMD --tag $IMAGE_NAME:$TAG"
    
    # 添加缓存选项
    if [[ -n "$CACHE_FROM" ]]; then
        BUILD_CMD="$BUILD_CMD $CACHE_FROM"
        log_info "使用缓存: $CACHE_FROM"
    fi
    
    if [[ -n "$CACHE_TO" ]]; then
        BUILD_CMD="$BUILD_CMD $CACHE_TO"
        log_info "保存缓存: $CACHE_TO"
    fi
    
    # 添加构建参数
    if [[ -n "$BUILD_ARGS" ]]; then
        BUILD_CMD="$BUILD_CMD $BUILD_ARGS"
        log_info "构建参数: $BUILD_ARGS"
    fi
    
    # 是否推送
    if [[ "$PUSH" == true ]]; then
        BUILD_CMD="$BUILD_CMD --push"
        log_info "构建完成后将推送到仓库"
    else
        BUILD_CMD="$BUILD_CMD --load"
        log_info "构建完成后将加载到本地"
    fi
    
    # 添加 Dockerfile 路径
    BUILD_CMD="$BUILD_CMD ."
    
    log_info "执行构建命令: $BUILD_CMD"
    
    # 执行构建
    if eval $BUILD_CMD; then
        log_success "镜像构建成功!"
    else
        log_error "镜像构建失败!"
        exit 1
    fi
}

# 显示镜像信息
show_image_info() {
    if [[ "$PUSH" != true ]]; then
        log_info "镜像信息:"
        docker images | grep "$IMAGE_NAME" | head -5
        
        log_info "镜像大小分析:"
        docker history "$IMAGE_NAME:$TAG" --format "table {{.CreatedBy}}\t{{.Size}}" | head -10
    fi
}

# 清理构建缓存
cleanup_cache() {
    log_info "清理构建缓存..."
    docker buildx prune -f
    log_success "缓存清理完成"
}

# 主函数
main() {
    log_info "开始 Docker 优化构建流程"
    
    # 检查前置条件
    check_buildx
    
    # 创建构建器
    create_builder
    
    # 构建镜像
    build_image
    
    # 显示镜像信息
    show_image_info
    
    log_success "构建流程完成!"
    
    # 询问是否清理缓存
    if [[ "$PUSH" != true ]]; then
        echo
        read -p "是否清理构建缓存? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cleanup_cache
        fi
    fi
}

# 执行主函数
main "$@"
