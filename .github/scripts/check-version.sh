#!/bin/bash

# 版本检测脚本 - 用于本地测试GitHub Actions的版本检测逻辑

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否在git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "当前目录不是git仓库"
    exit 1
fi

# 检查pyproject.toml文件是否存在
if [ ! -f "api/pyproject.toml" ]; then
    print_error "找不到 api/pyproject.toml 文件"
    exit 1
fi

print_info "开始检测版本变化..."

# 获取当前版本
CURRENT_VERSION=$(grep '^version = ' api/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
if [ -z "$CURRENT_VERSION" ]; then
    print_error "无法从 api/pyproject.toml 中提取版本号"
    exit 1
fi

print_info "当前版本: $CURRENT_VERSION"

# 检查是否有提交历史
if ! git rev-parse HEAD~1 > /dev/null 2>&1; then
    print_warning "没有足够的提交历史，无法比较版本变化"
    print_info "这可能是初始提交或仓库只有一个提交"
    exit 0
fi

# 检查pyproject.toml是否在最近的提交中被修改
if git diff --name-only HEAD~1 HEAD | grep -q "api/pyproject.toml"; then
    print_info "api/pyproject.toml 在最近的提交中被修改"
    
    # 获取上一个版本
    PREVIOUS_VERSION=$(git show HEAD~1:api/pyproject.toml | grep '^version = ' | sed 's/version = "\(.*\)"/\1/' 2>/dev/null || echo "")
    
    if [ -z "$PREVIOUS_VERSION" ]; then
        print_warning "无法获取上一个版本号"
    else
        print_info "上一个版本: $PREVIOUS_VERSION"
        
        # 比较版本
        if [ "$PREVIOUS_VERSION" != "$CURRENT_VERSION" ]; then
            print_success "版本号发生变化: $PREVIOUS_VERSION → $CURRENT_VERSION"
            echo "SHOULD_BUILD=true"
        else
            print_warning "版本号未发生变化: $CURRENT_VERSION"
            echo "SHOULD_BUILD=false"
        fi
    fi
else
    print_info "api/pyproject.toml 在最近的提交中未被修改"
    echo "SHOULD_BUILD=false"
fi

# 检查其他相关文件是否被修改
print_info "检查其他相关文件的修改情况..."

MODIFIED_FILES=$(git diff --name-only HEAD~1 HEAD)
RELEVANT_PATTERNS=(
    "Dockerfile"
    "api/"
    "admin/"
    "home/"
    "docker/"
)

RELEVANT_CHANGES=false
for pattern in "${RELEVANT_PATTERNS[@]}"; do
    if echo "$MODIFIED_FILES" | grep -q "^$pattern"; then
        print_info "检测到相关文件修改: $pattern"
        RELEVANT_CHANGES=true
    fi
done

if [ "$RELEVANT_CHANGES" = true ]; then
    print_info "检测到相关文件修改，建议构建Docker镜像"
else
    print_info "未检测到相关文件修改"
fi

# 显示修改的文件列表
if [ -n "$MODIFIED_FILES" ]; then
    print_info "最近提交中修改的文件:"
    echo "$MODIFIED_FILES" | sed 's/^/  - /'
else
    print_info "最近提交中没有文件修改"
fi

# 生成构建建议
echo ""
print_info "构建建议:"
if [ "$CURRENT_VERSION" != "${PREVIOUS_VERSION:-}" ] || [ "$RELEVANT_CHANGES" = true ]; then
    print_success "建议构建Docker镜像"
    echo "  原因: 版本变化或相关文件修改"
else
    print_warning "可以跳过Docker镜像构建"
    echo "  原因: 版本未变化且无相关文件修改"
fi

# 显示可能的Docker标签
echo ""
print_info "可能的Docker镜像标签:"
echo "  - $CURRENT_VERSION"
echo "  - latest"

# 获取当前分支名
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "HEAD" ]; then
    echo "  - $CURRENT_BRANCH"
fi

# 获取commit SHA
COMMIT_SHA=$(git rev-parse --short HEAD)
echo "  - $CURRENT_BRANCH-$COMMIT_SHA"

print_success "版本检测完成"
