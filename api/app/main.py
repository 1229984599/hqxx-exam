from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from app.config import settings, TORTOISE_ORM
from app.core.cache import cache_manager
from app.routers import auth, semesters, grades, subjects, categories, questions, templates, upload, analytics, system, search, roles, public
from app.middleware.performance import PerformanceMiddleware

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="学校考试系统API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 添加性能监控中间件
app.add_middleware(PerformanceMiddleware)

# 设置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(semesters.router, prefix=settings.API_V1_STR)
app.include_router(grades.router, prefix=settings.API_V1_STR)
app.include_router(subjects.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(questions.router, prefix=settings.API_V1_STR)
app.include_router(templates.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(roles.router, prefix=settings.API_V1_STR)
# 公开API路由（无需认证）
app.include_router(public.router, prefix=settings.API_V1_STR)

# 注册Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "HQXX Exam System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    cache_health = cache_manager.health_check()
    return {
        "status": "healthy",
        "cache": cache_health,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
