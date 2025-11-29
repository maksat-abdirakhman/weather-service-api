import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.weather_service import WeatherService
from app.schemas.weather import WeatherCreate, WeatherUpdate


@pytest.mark.asyncio
async def test_create_weather_service(test_session: AsyncSession):
    """Test creating weather through service."""
    service = WeatherService(test_session)
    
    weather_data = WeatherCreate(
        city="TestCity",
        country="TC",
        temperature=22.5,
        humidity=55.0,
        pressure=1015.0,
        feels_like=21.0,
    )
    
    weather = await service.create(weather_data)
    await test_session.commit()
    
    assert weather.id is not None
    assert weather.city == "TestCity"
    assert weather.temperature == 22.5


@pytest.mark.asyncio
async def test_get_by_id_service(test_session: AsyncSession):
    """Test getting weather by ID through service."""
    service = WeatherService(test_session)
    
    # Create a record
    weather_data = WeatherCreate(
        city="GetByIdCity",
        country="XX",
        temperature=20.0,
        humidity=50.0,
        pressure=1010.0,
    )
    created = await service.create(weather_data)
    await test_session.commit()
    
    # Get by ID
    weather = await service.get_by_id(created.id)
    assert weather is not None
    assert weather.city == "GetByIdCity"


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session: AsyncSession):
    """Test getting non-existent weather by ID."""
    service = WeatherService(test_session)
    
    weather = await service.get_by_id(99999)
    assert weather is None


@pytest.mark.asyncio
async def test_get_by_city_service(test_session: AsyncSession):
    """Test getting weather by city through service."""
    service = WeatherService(test_session)
    
    # Create a record
    weather_data = WeatherCreate(
        city="CitySearch",
        country="CS",
        temperature=25.0,
        humidity=60.0,
        pressure=1020.0,
    )
    await service.create(weather_data)
    await test_session.commit()
    
    # Get by city
    weather = await service.get_by_city("CitySearch")
    assert weather is not None
    assert weather.country == "CS"


@pytest.mark.asyncio
async def test_get_by_city_case_insensitive(test_session: AsyncSession):
    """Test that city search is case insensitive."""
    service = WeatherService(test_session)
    
    weather_data = WeatherCreate(
        city="CaseTest",
        country="CT",
        temperature=20.0,
        humidity=50.0,
        pressure=1010.0,
    )
    await service.create(weather_data)
    await test_session.commit()
    
    # Search with different case
    weather = await service.get_by_city("casetest")
    assert weather is not None
    assert weather.city == "CaseTest"


@pytest.mark.asyncio
async def test_update_weather_service(test_session: AsyncSession):
    """Test updating weather through service."""
    service = WeatherService(test_session)
    
    # Create a record
    weather_data = WeatherCreate(
        city="UpdateCity",
        country="UC",
        temperature=20.0,
        humidity=50.0,
        pressure=1010.0,
    )
    created = await service.create(weather_data)
    await test_session.commit()
    
    # Update
    update_data = WeatherUpdate(temperature=25.0, humidity=55.0)
    updated = await service.update(created.id, update_data)
    await test_session.commit()
    
    assert updated.temperature == 25.0
    assert updated.humidity == 55.0
    assert updated.city == "UpdateCity"  # Unchanged


@pytest.mark.asyncio
async def test_delete_weather_service(test_session: AsyncSession):
    """Test deleting weather through service."""
    service = WeatherService(test_session)
    
    # Create a record
    weather_data = WeatherCreate(
        city="DeleteCity",
        country="DC",
        temperature=20.0,
        humidity=50.0,
        pressure=1010.0,
    )
    created = await service.create(weather_data)
    await test_session.commit()
    
    # Delete
    result = await service.delete(created.id)
    await test_session.commit()
    
    assert result is True
    
    # Verify deleted
    weather = await service.get_by_id(created.id)
    assert weather is None


@pytest.mark.asyncio
async def test_delete_not_found(test_session: AsyncSession):
    """Test deleting non-existent weather."""
    service = WeatherService(test_session)
    
    result = await service.delete(99999)
    assert result is False


@pytest.mark.asyncio
async def test_get_all_pagination(test_session: AsyncSession):
    """Test pagination in get_all."""
    service = WeatherService(test_session)
    
    # Create 15 records
    for i in range(15):
        weather_data = WeatherCreate(
            city=f"PaginationCity{i}",
            country="PC",
            temperature=20.0 + i,
            humidity=50.0,
            pressure=1010.0,
        )
        await service.create(weather_data)
    await test_session.commit()
    
    # Test first page
    items, total = await service.get_all(page=1, size=5)
    assert len(items) == 5
    assert total == 15
    
    # Test second page
    items, total = await service.get_all(page=2, size=5)
    assert len(items) == 5


@pytest.mark.asyncio
async def test_upsert_by_city_new(test_session: AsyncSession):
    """Test upsert creates new record when city doesn't exist."""
    service = WeatherService(test_session)
    
    weather_data = WeatherCreate(
        city="UpsertNew",
        country="UN",
        temperature=20.0,
        humidity=50.0,
        pressure=1010.0,
    )
    
    weather, is_new = await service.upsert_by_city(weather_data)
    await test_session.commit()
    
    assert is_new is True
    assert weather.city == "UpsertNew"


@pytest.mark.asyncio
async def test_upsert_by_city_update(test_session: AsyncSession):
    """Test upsert updates existing record when city exists."""
    service = WeatherService(test_session)
    
    # Create initial record
    initial_data = WeatherCreate(
        city="UpsertUpdate",
        country="UU",
        temperature=20.0,
        humidity=50.0,
        pressure=1010.0,
    )
    await service.create(initial_data)
    await test_session.commit()
    
    # Upsert with new data
    update_data = WeatherCreate(
        city="UpsertUpdate",
        country="UU",
        temperature=25.0,
        humidity=55.0,
        pressure=1015.0,
    )
    weather, is_new = await service.upsert_by_city(update_data)
    await test_session.commit()
    
    assert is_new is False
    assert weather.temperature == 25.0
    assert weather.humidity == 55.0

