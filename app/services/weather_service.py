from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.weather import Weather
from app.schemas.weather import WeatherCreate, WeatherUpdate


class WeatherService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, weather_data: WeatherCreate) -> Weather:
        data = weather_data.model_dump()
        if data.get("data_timestamp") is None:
            data["data_timestamp"] = datetime.utcnow()
        
        weather = Weather(**data)
        self.db.add(weather)
        await self.db.flush()
        await self.db.refresh(weather)
        return weather
    
    async def get_by_id(self, weather_id: int) -> Optional[Weather]:
        result = await self.db.execute(
            select(Weather).where(Weather.id == weather_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_city(self, city: str, country: Optional[str] = None) -> Optional[Weather]:
        query = select(Weather).where(func.lower(Weather.city) == city.lower())
        if country:
            query = query.where(func.lower(Weather.country) == country.lower())
        
        query = query.order_by(Weather.data_timestamp.desc()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        page: int = 1,
        size: int = 10,
        city: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Tuple[List[Weather], int]:
        query = select(Weather)
        count_query = select(func.count(Weather.id))
        
        conditions = []
        if city:
            conditions.append(func.lower(Weather.city) == city.lower())
        if country:
            conditions.append(func.lower(Weather.country) == country.lower())
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * size
        query = query.order_by(Weather.data_timestamp.desc()).offset(offset).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def update(self, weather_id: int, weather_data: WeatherUpdate) -> Optional[Weather]:
        weather = await self.get_by_id(weather_id)
        if not weather:
            return None
        
        update_data = weather_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(weather, field, value)
        
        weather.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(weather)
        return weather
    
    async def delete(self, weather_id: int) -> bool:
        weather = await self.get_by_id(weather_id)
        if not weather:
            return False
        
        await self.db.delete(weather)
        await self.db.flush()
        return True
    
    async def upsert_by_city(self, weather_data: WeatherCreate) -> Tuple[Weather, bool]:
        existing = await self.get_by_city(weather_data.city, weather_data.country)
        
        if existing:
            update_dict = {k: v for k, v in weather_data.model_dump().items() if v is not None}
            update_data = WeatherUpdate(**update_dict)
            weather = await self.update(existing.id, update_data)
            return weather, False
        else:
            weather = await self.create(weather_data)
            return weather, True
    
    async def get_cities_list(self) -> List[str]:
        query = select(Weather.city, Weather.country).distinct()
        result = await self.db.execute(query)
        return [f"{row.city}, {row.country}" for row in result.all()]
