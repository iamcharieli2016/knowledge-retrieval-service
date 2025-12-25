"""
主应用入口
"""
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .api.routes import router


# 配置日志
def setup_logging():
    """设置日志"""
    settings = get_settings()
    
    # 创建日志目录
    log_file = Path(settings.logging.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, settings.logging.level),
        format=settings.logging.format,
        handlers=[
            logging.FileHandler(settings.logging.file),
            logging.StreamHandler()
        ]
    )


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger = logging.getLogger(__name__)
    settings = get_settings()
    
    logger.info(f"Starting {settings.service.name} v{settings.service.version}")
    logger.info(f"Embedding model: {settings.embedding.model_name}")
    logger.info(f"Vector database: {settings.vector_db.provider}")
    
    # 创建必要的目录
    Path(settings.file_processing.upload_dir).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # 关闭时
    logger.info("Shutting down service")


# 创建应用
def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()
    
    # 设置日志
    setup_logging()
    
    # 创建应用实例
    app = FastAPI(
        title=settings.service.name,
        version=settings.service.version,
        description="知识检索服务 - 支持多种文件类型的智能检索",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # 配置 CORS
    if settings.security.cors["enabled"]:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.security.cors["origins"],
            allow_credentials=True,
            allow_methods=settings.security.cors["methods"],
            allow_headers=settings.security.cors["headers"],
        )
    
    # 注册路由
    app.include_router(router, prefix="/api/v1")
    
    # 根路径
    @app.get("/", tags=["系统"])
    async def root():
        """根路径"""
        return {
            "name": settings.service.name,
            "version": settings.service.version,
            "status": "running",
            "docs": "/docs",
            "api": "/api/v1"
        }
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """全局异常处理"""
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc),
                "detail": "An unexpected error occurred"
            }
        )
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=settings.service.debug,
        workers=settings.performance.workers if not settings.service.debug else 1
    )
