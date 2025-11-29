import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.config import get_settings
from app.database import init_db
from app.api import weather_router, logs_router
from app.tasks import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Weather Service...")
    await init_db()
    logger.info("Database initialized")
    
    start_scheduler()
    logger.info("Scheduler started")
    
    yield
    
    stop_scheduler()
    logger.info("Scheduler stopped")
    logger.info("Weather Service stopped")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Asynchronous microservice for weather data management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Service API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                width: 100%;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 25px 45px rgba(0, 0, 0, 0.2);
            }
            h1 {
                color: #00d9ff;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 0 0 30px rgba(0, 217, 255, 0.3);
            }
            .subtitle { color: rgba(255, 255, 255, 0.7); font-size: 1.1em; margin-bottom: 30px; }
            .links { display: flex; flex-direction: column; gap: 15px; }
            a {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 15px 20px;
                background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(0, 217, 255, 0.05));
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 12px;
                color: #fff;
                text-decoration: none;
                transition: all 0.3s ease;
            }
            a:hover {
                background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(0, 217, 255, 0.1));
                border-color: rgba(0, 217, 255, 0.6);
                transform: translateX(5px);
            }
            .icon { font-size: 1.5em; }
            .link-text { display: flex; flex-direction: column; }
            .link-title { font-weight: 600; font-size: 1.1em; }
            .link-desc { font-size: 0.85em; color: rgba(255, 255, 255, 0.6); }
            .status {
                margin-top: 30px;
                padding: 15px;
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .status-dot {
                width: 10px;
                height: 10px;
                background: #00ff88;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
            .status-text { color: #00ff88; font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⛅ Weather Service API</h1>
            <p class="subtitle">Asynchronous microservice for weather data management</p>
            <div class="links">
                <a href="/docs">
                    <span class="icon">📖</span>
                    <div class="link-text">
                        <span class="link-title">Swagger UI</span>
                        <span class="link-desc">Interactive API documentation</span>
                    </div>
                </a>
                <a href="/redoc">
                    <span class="icon">📚</span>
                    <div class="link-text">
                        <span class="link-title">ReDoc</span>
                        <span class="link-desc">Alternative API documentation</span>
                    </div>
                </a>
                <a href="/api/v1/weather">
                    <span class="icon">🌤️</span>
                    <div class="link-text">
                        <span class="link-title">Weather Data</span>
                        <span class="link-desc">View current weather records</span>
                    </div>
                </a>
                <a href="/api/v1/logs">
                    <span class="icon">📝</span>
                    <div class="link-text">
                        <span class="link-title">Action Logs</span>
                        <span class="link-desc">View system activity logs</span>
                    </div>
                </a>
            </div>
            <div class="status">
                <div class="status-dot"></div>
                <span class="status-text">Service is running</span>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "weather-service"}
