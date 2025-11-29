import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.log_service import LogService


@pytest.mark.asyncio
async def test_log_action(test_session: AsyncSession):
    """Test logging an action."""
    service = LogService(test_session)
    
    log = await service.log_action(
        action="CREATE",
        entity="weather",
        entity_id=1,
        details={"city": "TestCity"},
        status="success",
    )
    await test_session.commit()
    
    assert log.id is not None
    assert log.action == "CREATE"
    assert log.entity == "weather"
    assert log.status == "success"


@pytest.mark.asyncio
async def test_log_action_with_error(test_session: AsyncSession):
    """Test logging an error action."""
    service = LogService(test_session)
    
    log = await service.log_action(
        action="FETCH",
        entity="weather",
        status="error",
        error_message="Connection timeout",
        details={"city": "FailedCity"},
    )
    await test_session.commit()
    
    assert log.status == "error"
    assert log.error_message == "Connection timeout"


@pytest.mark.asyncio
async def test_get_logs_pagination(test_session: AsyncSession):
    """Test getting logs with pagination."""
    service = LogService(test_session)
    
    # Create 15 logs
    for i in range(15):
        await service.log_action(
            action="CREATE",
            entity="weather",
            entity_id=i,
        )
    await test_session.commit()
    
    # Test first page
    items, total = await service.get_logs(page=1, size=5)
    assert len(items) == 5
    assert total == 15
    
    # Test second page
    items, total = await service.get_logs(page=2, size=5)
    assert len(items) == 5


@pytest.mark.asyncio
async def test_get_logs_filter_by_action(test_session: AsyncSession):
    """Test filtering logs by action."""
    service = LogService(test_session)
    
    # Create logs with different actions
    await service.log_action(action="CREATE", entity="weather")
    await service.log_action(action="UPDATE", entity="weather")
    await service.log_action(action="DELETE", entity="weather")
    await test_session.commit()
    
    # Filter by CREATE
    items, total = await service.get_logs(action="CREATE")
    assert total == 1
    assert items[0].action == "CREATE"


@pytest.mark.asyncio
async def test_get_logs_filter_by_status(test_session: AsyncSession):
    """Test filtering logs by status."""
    service = LogService(test_session)
    
    # Create logs with different statuses
    await service.log_action(action="CREATE", entity="weather", status="success")
    await service.log_action(action="FETCH", entity="weather", status="error", error_message="Failed")
    await test_session.commit()
    
    # Filter by error
    items, total = await service.get_logs(status="error")
    assert total == 1
    assert items[0].status == "error"


@pytest.mark.asyncio
async def test_get_log_by_id(test_session: AsyncSession):
    """Test getting a specific log entry."""
    service = LogService(test_session)
    
    log = await service.log_action(
        action="CREATE",
        entity="weather",
        details={"test": "data"},
    )
    await test_session.commit()
    
    fetched = await service.get_log_by_id(log.id)
    assert fetched is not None
    assert fetched.id == log.id
    assert fetched.action == "CREATE"


@pytest.mark.asyncio
async def test_get_log_by_id_not_found(test_session: AsyncSession):
    """Test getting non-existent log entry."""
    service = LogService(test_session)
    
    log = await service.get_log_by_id(99999)
    assert log is None


@pytest.mark.asyncio
async def test_get_actions_summary(test_session: AsyncSession):
    """Test getting actions summary."""
    service = LogService(test_session)
    
    # Create various logs
    await service.log_action(action="CREATE", entity="weather", status="success")
    await service.log_action(action="CREATE", entity="weather", status="success")
    await service.log_action(action="CREATE", entity="weather", status="error")
    await service.log_action(action="UPDATE", entity="weather", status="success")
    await service.log_action(action="DELETE", entity="weather", status="success")
    await test_session.commit()
    
    summary = await service.get_actions_summary()
    
    assert "CREATE" in summary
    assert summary["CREATE"]["success"] == 2
    assert summary["CREATE"]["error"] == 1
    assert "UPDATE" in summary
    assert summary["UPDATE"]["success"] == 1


@pytest.mark.asyncio
async def test_log_with_ip_and_user_agent(test_session: AsyncSession):
    """Test logging with IP address and user agent."""
    service = LogService(test_session)
    
    log = await service.log_action(
        action="CREATE",
        entity="weather",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 (Test)",
    )
    await test_session.commit()
    
    assert log.ip_address == "192.168.1.1"
    assert log.user_agent == "Mozilla/5.0 (Test)"


@pytest.mark.asyncio
async def test_log_details_json_serialization(test_session: AsyncSession):
    """Test that details are properly serialized to JSON."""
    service = LogService(test_session)
    
    log = await service.log_action(
        action="CREATE",
        entity="weather",
        details={
            "city": "TestCity",
            "temperature": 25.5,
            "timestamp": datetime.now(),
        },
    )
    await test_session.commit()
    
    assert log.details is not None
    assert "city" in log.details

