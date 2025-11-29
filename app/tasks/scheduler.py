import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import get_settings
from app.database import async_session_maker
from app.services.weather_service import WeatherService
from app.services.weather_fetcher import WeatherFetcher
from app.services.log_service import LogService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def update_weather_for_cities():
    settings = get_settings()
    cities = [c.strip() for c in settings.default_cities.split(",")]
    
    logger.info(f"Starting weather update for {len(cities)} cities")
    
    fetcher = WeatherFetcher()
    
    async with async_session_maker() as db:
        weather_service = WeatherService(db)
        log_service = LogService(db)
        
        tasks = [fetcher.fetch_weather(city) for city in cities]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        error_count = 0
        
        for city, result in zip(cities, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch weather for {city}: {result}")
                await log_service.log_action(
                    action="SCHEDULED_FETCH",
                    entity="weather",
                    status="error",
                    error_message=str(result),
                    details={"city": city},
                )
                error_count += 1
            elif result is None:
                logger.warning(f"No weather data received for {city}")
                error_count += 1
            else:
                try:
                    weather, is_new = await weather_service.upsert_by_city(result)
                    await log_service.log_action(
                        action="SCHEDULED_FETCH",
                        entity="weather",
                        entity_id=weather.id,
                        details={
                            "city": weather.city,
                            "country": weather.country,
                            "temperature": weather.temperature,
                            "is_new": is_new,
                        },
                    )
                    success_count += 1
                    logger.info(f"Updated weather for {weather.city}, {weather.country}: {weather.temperature}°C")
                except Exception as e:
                    logger.error(f"Failed to save weather for {city}: {e}")
                    await log_service.log_action(
                        action="SCHEDULED_FETCH",
                        entity="weather",
                        status="error",
                        error_message=str(e),
                        details={"city": city},
                    )
                    error_count += 1
        
        await db.commit()
        logger.info(f"Weather update completed: {success_count} success, {error_count} errors")


def start_scheduler():
    settings = get_settings()
    
    scheduler.add_job(
        update_weather_for_cities,
        trigger=IntervalTrigger(minutes=settings.weather_update_interval_minutes),
        id="weather_update",
        name="Update weather data for all cities",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Weather updates every {settings.weather_update_interval_minutes} minutes")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
