#!/bin/bash

# 系统性能监控脚本
# 用于监控 HQXX 考试管理系统的性能指标

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
CONTAINER_NAME="hqxx-exam"
LOG_FILE="/tmp/hqxx-performance.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=80
ALERT_THRESHOLD_DISK=90

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$LOG_FILE"
}

# 检查 Docker 容器状态
check_container_status() {
    log_info "检查容器状态..."
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        log_success "容器 $CONTAINER_NAME 正在运行"
        return 0
    else
        log_error "容器 $CONTAINER_NAME 未运行"
        return 1
    fi
}

# 获取容器资源使用情况
get_container_stats() {
    log_info "获取容器资源使用情况..."
    
    # 获取容器统计信息
    STATS=$(docker stats "$CONTAINER_NAME" --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}")
    
    if [[ $? -eq 0 ]]; then
        echo "$STATS"
        
        # 解析 CPU 使用率
        CPU_USAGE=$(echo "$STATS" | tail -n 1 | awk '{print $1}' | sed 's/%//')
        MEM_USAGE=$(echo "$STATS" | tail -n 1 | awk '{print $3}' | sed 's/%//')
        
        # 检查阈值
        if (( $(echo "$CPU_USAGE > $ALERT_THRESHOLD_CPU" | bc -l) )); then
            log_warning "CPU 使用率过高: ${CPU_USAGE}%"
        fi
        
        if (( $(echo "$MEM_USAGE > $ALERT_THRESHOLD_MEMORY" | bc -l) )); then
            log_warning "内存使用率过高: ${MEM_USAGE}%"
        fi
    else
        log_error "无法获取容器统计信息"
    fi
}

# 检查应用健康状态
check_app_health() {
    log_info "检查应用健康状态..."
    
    # 检查 API 健康端点
    if curl -f -s http://localhost/api/health >/dev/null 2>&1; then
        log_success "API 健康检查通过"
    else
        log_error "API 健康检查失败"
    fi
    
    # 检查前台页面
    if curl -f -s http://localhost/ >/dev/null 2>&1; then
        log_success "前台页面可访问"
    else
        log_error "前台页面不可访问"
    fi
    
    # 检查管理后台
    if curl -f -s http://localhost/admin/ >/dev/null 2>&1; then
        log_success "管理后台可访问"
    else
        log_error "管理后台不可访问"
    fi
}

# 检查磁盘使用情况
check_disk_usage() {
    log_info "检查磁盘使用情况..."
    
    DISK_USAGE=$(df -h / | tail -n 1 | awk '{print $5}' | sed 's/%//')
    
    log_info "磁盘使用率: ${DISK_USAGE}%"
    
    if [[ $DISK_USAGE -gt $ALERT_THRESHOLD_DISK ]]; then
        log_warning "磁盘使用率过高: ${DISK_USAGE}%"
    fi
}

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    
    # 检查端口监听
    if netstat -tuln | grep -q ":80 "; then
        log_success "HTTP 端口 (80) 正在监听"
    else
        log_error "HTTP 端口 (80) 未监听"
    fi
    
    if netstat -tuln | grep -q ":8000 "; then
        log_success "API 端口 (8000) 正在监听"
    else
        log_error "API 端口 (8000) 未监听"
    fi
}

# 检查日志错误
check_logs() {
    log_info "检查应用日志..."
    
    # 检查最近的错误日志
    ERROR_COUNT=$(docker logs "$CONTAINER_NAME" --since="1h" 2>&1 | grep -i error | wc -l)
    WARNING_COUNT=$(docker logs "$CONTAINER_NAME" --since="1h" 2>&1 | grep -i warning | wc -l)
    
    log_info "最近1小时错误日志数量: $ERROR_COUNT"
    log_info "最近1小时警告日志数量: $WARNING_COUNT"
    
    if [[ $ERROR_COUNT -gt 10 ]]; then
        log_warning "错误日志数量较多: $ERROR_COUNT"
    fi
}

# 性能测试
run_performance_test() {
    log_info "运行性能测试..."
    
    # 简单的 API 响应时间测试
    API_RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost/api/health)
    
    log_info "API 响应时间: ${API_RESPONSE_TIME}s"
    
    if (( $(echo "$API_RESPONSE_TIME > 1.0" | bc -l) )); then
        log_warning "API 响应时间较慢: ${API_RESPONSE_TIME}s"
    fi
}

# 生成性能报告
generate_report() {
    log_info "生成性能报告..."
    
    REPORT_FILE="/tmp/hqxx-performance-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
HQXX 考试管理系统性能报告
生成时间: $(date)
========================================

系统信息:
- 主机名: $(hostname)
- 操作系统: $(uname -a)
- Docker 版本: $(docker --version)

容器状态:
$(docker ps | grep "$CONTAINER_NAME" || echo "容器未运行")

资源使用情况:
$(docker stats "$CONTAINER_NAME" --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" 2>/dev/null || echo "无法获取统计信息")

磁盘使用情况:
$(df -h)

网络连接:
$(netstat -tuln | grep -E ":(80|8000) ")

最近日志摘要:
错误数量: $(docker logs "$CONTAINER_NAME" --since="1h" 2>&1 | grep -i error | wc -l)
警告数量: $(docker logs "$CONTAINER_NAME" --since="1h" 2>&1 | grep -i warning | wc -l)

性能指标:
API 响应时间: $(curl -o /dev/null -s -w '%{time_total}' http://localhost/api/health 2>/dev/null || echo "无法测试")s

========================================
EOF

    log_success "性能报告已生成: $REPORT_FILE"
}

# 清理旧日志
cleanup_logs() {
    log_info "清理旧日志文件..."
    
    # 删除7天前的日志文件
    find /tmp -name "hqxx-performance*.log" -mtime +7 -delete 2>/dev/null || true
    find /tmp -name "hqxx-performance-report*.txt" -mtime +7 -delete 2>/dev/null || true
    
    log_success "日志清理完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
HQXX 系统性能监控脚本

用法: $0 [选项]

选项:
    --container NAME    指定容器名称 (默认: hqxx-exam)
    --report           生成详细性能报告
    --test             运行性能测试
    --cleanup          清理旧日志文件
    --continuous       持续监控模式
    -h, --help         显示帮助信息

示例:
    $0                 # 运行基本监控检查
    $0 --report        # 生成性能报告
    $0 --continuous    # 持续监控模式
EOF
}

# 持续监控模式
continuous_monitor() {
    log_info "启动持续监控模式 (Ctrl+C 停止)"
    
    while true; do
        echo "========================================"
        log_info "执行监控检查 - $(date)"
        
        check_container_status
        get_container_stats
        check_app_health
        check_disk_usage
        check_network
        check_logs
        
        echo "等待60秒后进行下次检查..."
        sleep 60
    done
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --container)
                CONTAINER_NAME="$2"
                shift 2
                ;;
            --report)
                generate_report
                exit 0
                ;;
            --test)
                run_performance_test
                exit 0
                ;;
            --cleanup)
                cleanup_logs
                exit 0
                ;;
            --continuous)
                continuous_monitor
                exit 0
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
    
    # 默认执行基本监控
    log_info "开始系统性能监控检查"
    
    check_container_status
    get_container_stats
    check_app_health
    check_disk_usage
    check_network
    check_logs
    run_performance_test
    
    log_success "监控检查完成"
}

# 执行主函数
main "$@"
