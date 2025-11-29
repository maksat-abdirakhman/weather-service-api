from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.weather import (
    WeatherCreate,
    WeatherUpdate,
    WeatherResponse,
    WeatherListResponse,
)
from app.services.weather_service import WeatherService
from app.services.log_service import LogService
from app.services.weather_fetcher import WeatherFetcher
import math

router = APIRouter(prefix="/weather", tags=["Weather"])


def get_client_info(request: Request) -> tuple:
    """Extract client info from request."""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip, user_agent


@router.post("/", response_model=WeatherResponse, status_code=201)
async def create_weather(
    weather_data: WeatherCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new weather record."""
    service = WeatherService(db)
    log_service = LogService(db)
    ip, user_agent = get_client_info(request)
    
    try:
        weather = await service.create(weather_data)
        await log_service.log_action(
            action="CREATE",
            entity="weather",
            entity_id=weather.id,
            details={"city": weather.city, "country": weather.country},
            ip_address=ip,
            user_agent=user_agent,
        )
        return weather
    except Exception as e:
        await log_service.log_action(
            action="CREATE",
            entity="weather",
            status="error",
            error_message=str(e),
            ip_address=ip,
            user_agent=user_agent,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=WeatherListResponse)
async def get_weather_list(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: AsyncSession = Depends(get_db),
):
    """Get list of weather records with pagination."""
    service = WeatherService(db)
    items, total = await service.get_all(page=page, size=size, city=city, country=country)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return WeatherListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/cities", response_model=list)
async def get_cities(db: AsyncSession = Depends(get_db)):
    """Get list of all cities with weather data."""
    service = WeatherService(db)
    return await service.get_cities_list()


@router.get("/city/{city_name}", response_model=WeatherResponse)
async def get_weather_by_city(
    city_name: str,
    country: Optional[str] = Query(None, description="Country filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get latest weather data for a specific city."""
    service = WeatherService(db)
    weather = await service.get_by_city(city_name, country)
    
    if not weather:
        raise HTTPException(status_code=404, detail=f"Weather data for {city_name} not found")
    
    return weather


@router.get("/{weather_id}", response_model=WeatherResponse)
async def get_weather(
    weather_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get weather record by ID."""
    service = WeatherService(db)
    weather = await service.get_by_id(weather_id)
    
    if not weather:
        raise HTTPException(status_code=404, detail="Weather record not found")
    
    return weather


@router.put("/{weather_id}", response_model=WeatherResponse)
async def update_weather(
    weather_id: int,
    weather_data: WeatherUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update a weather record."""
    service = WeatherService(db)
    log_service = LogService(db)
    ip, user_agent = get_client_info(request)
    
    try:
        weather = await service.update(weather_id, weather_data)
        
        if not weather:
            raise HTTPException(status_code=404, detail="Weather record not found")
        
        await log_service.log_action(
            action="UPDATE",
            entity="weather",
            entity_id=weather.id,
            details=weather_data.model_dump(exclude_unset=True),
            ip_address=ip,
            user_agent=user_agent,
        )
        return weather
    except HTTPException:
        raise
    except Exception as e:
        await log_service.log_action(
            action="UPDATE",
            entity="weather",
            entity_id=weather_id,
            status="error",
            error_message=str(e),
            ip_address=ip,
            user_agent=user_agent,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{weather_id}", status_code=204)
async def delete_weather(
    weather_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete a weather record."""
    service = WeatherService(db)
    log_service = LogService(db)
    ip, user_agent = get_client_info(request)
    
    try:
        deleted = await service.delete(weather_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Weather record not found")
        
        await log_service.log_action(
            action="DELETE",
            entity="weather",
            entity_id=weather_id,
            ip_address=ip,
            user_agent=user_agent,
        )
    except HTTPException:
        raise
    except Exception as e:
        await log_service.log_action(
            action="DELETE",
            entity="weather",
            entity_id=weather_id,
            status="error",
            error_message=str(e),
            ip_address=ip,
            user_agent=user_agent,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch/{city_name}", response_model=WeatherResponse)
async def fetch_weather_for_city(
    city_name: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch weather data for a city from external API and save to database.
    If record exists for the city, it will be updated.
    """
    fetcher = WeatherFetcher()
    service = WeatherService(db)
    log_service = LogService(db)
    ip, user_agent = get_client_info(request)
    
    try:
        weather_data = await fetcher.fetch_weather(city_name)
        
        if not weather_data:
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to fetch weather data for {city_name}"
            )
        
        weather, is_new = await service.upsert_by_city(weather_data)
        
        await log_service.log_action(
            action="FETCH",
            entity="weather",
            entity_id=weather.id,
            details={
                "city": weather.city,
                "country": weather.country,
                "is_new": is_new,
            },
            ip_address=ip,
            user_agent=user_agent,
        )
        
        return weather
    except HTTPException:
        raise
    except Exception as e:
        await log_service.log_action(
            action="FETCH",
            entity="weather",
            status="error",
            error_message=str(e),
            details={"city": city_name},
            ip_address=ip,
            user_agent=user_agent,
        )
        raise HTTPException(status_code=500, detail=str(e))

