import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns HTML."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Weather Service API" in response.text


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "weather-service"


@pytest.mark.asyncio
async def test_create_weather(client: AsyncClient):
    """Test creating a weather record."""
    weather_data = {
        "city": "Moscow",
        "country": "RU",
        "temperature": 15.5,
        "humidity": 60.0,
        "pressure": 1013.0,
        "feels_like": 14.0,
        "wind_speed": 5.5,
        "weather_description": "Clear sky",
    }
    
    response = await client.post("/api/v1/weather/", json=weather_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["city"] == "Moscow"
    assert data["country"] == "RU"
    assert data["temperature"] == 15.5
    assert data["humidity"] == 60.0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_weather_list(client: AsyncClient):
    """Test getting list of weather records."""
    # Create some records first
    for city in ["London", "Paris", "Berlin"]:
        await client.post("/api/v1/weather/", json={
            "city": city,
            "country": "EU",
            "temperature": 20.0,
            "humidity": 50.0,
            "pressure": 1010.0,
        })
    
    response = await client.get("/api/v1/weather/")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] >= 3


@pytest.mark.asyncio
async def test_get_weather_by_id(client: AsyncClient):
    """Test getting weather record by ID."""
    # Create a record
    create_response = await client.post("/api/v1/weather/", json={
        "city": "Tokyo",
        "country": "JP",
        "temperature": 25.0,
        "humidity": 70.0,
        "pressure": 1005.0,
    })
    weather_id = create_response.json()["id"]
    
    # Get by ID
    response = await client.get(f"/api/v1/weather/{weather_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["city"] == "Tokyo"
    assert data["id"] == weather_id


@pytest.mark.asyncio
async def test_get_weather_not_found(client: AsyncClient):
    """Test getting non-existent weather record."""
    response = await client.get("/api/v1/weather/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_weather(client: AsyncClient):
    """Test updating a weather record."""
    # Create a record
    create_response = await client.post("/api/v1/weather/", json={
        "city": "Sydney",
        "country": "AU",
        "temperature": 30.0,
        "humidity": 40.0,
        "pressure": 1020.0,
    })
    weather_id = create_response.json()["id"]
    
    # Update the record
    update_data = {
        "temperature": 32.5,
        "humidity": 45.0,
    }
    response = await client.put(f"/api/v1/weather/{weather_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["temperature"] == 32.5
    assert data["humidity"] == 45.0
    assert data["city"] == "Sydney"  # Unchanged fields preserved


@pytest.mark.asyncio
async def test_delete_weather(client: AsyncClient):
    """Test deleting a weather record."""
    # Create a record
    create_response = await client.post("/api/v1/weather/", json={
        "city": "Dubai",
        "country": "AE",
        "temperature": 40.0,
        "humidity": 20.0,
        "pressure": 1000.0,
    })
    weather_id = create_response.json()["id"]
    
    # Delete the record
    response = await client.delete(f"/api/v1/weather/{weather_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/weather/{weather_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_weather_by_city(client: AsyncClient):
    """Test getting weather by city name."""
    # Create a record
    await client.post("/api/v1/weather/", json={
        "city": "Amsterdam",
        "country": "NL",
        "temperature": 18.0,
        "humidity": 65.0,
        "pressure": 1015.0,
    })
    
    response = await client.get("/api/v1/weather/city/Amsterdam")
    assert response.status_code == 200
    
    data = response.json()
    assert data["city"] == "Amsterdam"
    assert data["country"] == "NL"


@pytest.mark.asyncio
async def test_get_weather_by_city_not_found(client: AsyncClient):
    """Test getting weather for non-existent city."""
    response = await client.get("/api/v1/weather/city/NonExistentCity")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_weather_list_pagination(client: AsyncClient):
    """Test weather list pagination."""
    # Create multiple records
    for i in range(15):
        await client.post("/api/v1/weather/", json={
            "city": f"City{i}",
            "country": "XX",
            "temperature": 20.0 + i,
            "humidity": 50.0,
            "pressure": 1010.0,
        })
    
    # Test first page
    response = await client.get("/api/v1/weather/?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 1
    assert data["size"] == 5
    
    # Test second page
    response = await client.get("/api/v1/weather/?page=2&size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_weather_list_filter_by_city(client: AsyncClient):
    """Test filtering weather list by city."""
    # Create records for different cities
    await client.post("/api/v1/weather/", json={
        "city": "FilterCity",
        "country": "XX",
        "temperature": 25.0,
        "humidity": 55.0,
        "pressure": 1012.0,
    })
    await client.post("/api/v1/weather/", json={
        "city": "OtherCity",
        "country": "YY",
        "temperature": 30.0,
        "humidity": 60.0,
        "pressure": 1008.0,
    })
    
    response = await client.get("/api/v1/weather/?city=FilterCity")
    assert response.status_code == 200
    data = response.json()
    
    for item in data["items"]:
        assert item["city"].lower() == "filtercity"


@pytest.mark.asyncio
async def test_create_weather_validation(client: AsyncClient):
    """Test weather creation validation."""
    # Missing required fields
    response = await client.post("/api/v1/weather/", json={
        "city": "TestCity",
    })
    assert response.status_code == 422  # Validation error
    
    # Invalid humidity (> 100)
    response = await client.post("/api/v1/weather/", json={
        "city": "TestCity",
        "country": "XX",
        "temperature": 20.0,
        "humidity": 150.0,  # Invalid
        "pressure": 1010.0,
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_fetch_weather_for_city(client: AsyncClient):
    """Test fetching weather from external API (with mock data)."""
    response = await client.post("/api/v1/weather/fetch/Moscow,RU")
    assert response.status_code == 200
    
    data = response.json()
    assert "city" in data
    assert "temperature" in data
    assert "humidity" in data
    assert "id" in data  # Record was saved to database

