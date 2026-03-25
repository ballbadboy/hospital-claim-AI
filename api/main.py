from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.routes import router
from api.auth.routes import auth_router, limiter
from api.routes_his import his_router
from core.config import get_settings, setup_logging

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
        raise RuntimeError("jwt_secret_key must be at least 32 characters")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered claim validation for Thai hospitals. "
                "ลด Deny rate ทุกแผนก ทุกกองทุน",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(router)
app.include_router(his_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
