import time
import psutil
from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import SystemLogger, LogModule


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.request_times: List[Dict] = []
        self.error_count = 0
        self.total_requests = 0
        self.start_time = datetime.now()
    
    def add_request(self, path: str, method: str, duration: float, status_code: int):
        """添加请求记录"""
        self.total_requests += 1
        
        if status_code >= 400:
            self.error_count += 1
        
        # 记录请求时间
        self.request_times.append({
            'path': path,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'timestamp': datetime.now()
        })
        
        # 保持最近1000条记录
        if len(self.request_times) > 1000:
            self.request_times.pop(0)
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        now = datetime.now()
        
        # 最近5分钟的请求
        recent_requests = [
            req for req in self.request_times 
            if now - req['timestamp'] <= timedelta(minutes=5)
        ]
        
        # 计算平均响应时间
        avg_response_time = 0
        if recent_requests:
            avg_response_time = sum(req['duration'] for req in recent_requests) / len(recent_requests)
        
        # 计算错误率
        recent_errors = sum(1 for req in recent_requests if req['status_code'] >= 400)
        error_rate = (recent_errors / len(recent_requests) * 100) if recent_requests else 0
        
        # 系统资源使用
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'requests': {
                'total': self.total_requests,
                'recent_5min': len(recent_requests),
                'error_count': self.error_count,
                'error_rate': round(error_rate, 2)
            },
            'performance': {
                'avg_response_time': round(avg_response_time * 1000, 2),  # 转换为毫秒
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent
            },
            'uptime': str(now - self.start_time).split('.')[0],
            'timestamp': now.isoformat()
        }
    
    def get_slow_requests(self, threshold: float = 1.0) -> List[Dict]:
        """获取慢请求列表"""
        return [
            req for req in self.request_times 
            if req['duration'] > threshold
        ]


# 全局性能监控实例
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录性能数据
        performance_monitor.add_request(
            path=request.url.path,
            method=request.method,
            duration=process_time,
            status_code=response.status_code
        )
        
        # 记录慢请求
        if process_time > 1.0:  # 超过1秒的请求
            await SystemLogger.warning(
                module=LogModule.SYSTEM,
                message=f"慢请求检测: {request.method} {request.url.path}",
                details={
                    "duration": round(process_time * 1000, 2),
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code
                }
            )
        
        return response


class HealthChecker:
    """健康检查器"""
    
    @staticmethod
    async def check_database():
        """检查数据库连接"""
        try:
            from app.models.admin import Admin
            await Admin.all().count()
            return True, "Database connection OK"
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    @staticmethod
    def check_disk_space(threshold: float = 90.0):
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage('/')
            if disk.percent > threshold:
                return False, f"Disk usage too high: {disk.percent}%"
            return True, f"Disk usage OK: {disk.percent}%"
        except Exception as e:
            return False, f"Disk check error: {str(e)}"
    
    @staticmethod
    def check_memory(threshold: float = 90.0):
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            if memory.percent > threshold:
                return False, f"Memory usage too high: {memory.percent}%"
            return True, f"Memory usage OK: {memory.percent}%"
        except Exception as e:
            return False, f"Memory check error: {str(e)}"
    
    @staticmethod
    async def get_health_status():
        """获取整体健康状态"""
        checks = {}
        overall_status = "healthy"
        
        # 数据库检查
        db_ok, db_msg = await HealthChecker.check_database()
        checks["database"] = {"status": "ok" if db_ok else "error", "message": db_msg}
        if not db_ok:
            overall_status = "unhealthy"
        
        # 磁盘检查
        disk_ok, disk_msg = HealthChecker.check_disk_space()
        checks["disk"] = {"status": "ok" if disk_ok else "warning", "message": disk_msg}
        if not disk_ok and overall_status == "healthy":
            overall_status = "warning"
        
        # 内存检查
        memory_ok, memory_msg = HealthChecker.check_memory()
        checks["memory"] = {"status": "ok" if memory_ok else "warning", "message": memory_msg}
        if not memory_ok and overall_status == "healthy":
            overall_status = "warning"
        
        # 性能统计
        perf_stats = performance_monitor.get_stats()
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "performance": perf_stats
        }
