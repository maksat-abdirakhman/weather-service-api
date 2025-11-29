import json
from datetime import datetime
from typing import Optional, List, Tuple, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log import ActionLog


class LogService:
    """Service for managing action logs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_action(
        self,
        action: str,
        entity: str,
        entity_id: Optional[int] = None,
        details: Optional[Any] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ActionLog:
        """Log an action."""
        if details and not isinstance(details, str):
            details = json.dumps(details, default=str)
        
        log = ActionLog(
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
            status=status,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log
    
    async def get_logs(
        self,
        page: int = 1,
        size: int = 20,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[ActionLog], int]:
        """Get action logs with pagination and filters."""
        query = select(ActionLog)
        count_query = select(func.count(ActionLog.id))
        
        # Apply filters
        conditions = []
        if action:
            conditions.append(ActionLog.action == action)
        if entity:
            conditions.append(ActionLog.entity == entity)
        if status:
            conditions.append(ActionLog.status == status)
        if start_date:
            conditions.append(ActionLog.created_at >= start_date)
        if end_date:
            conditions.append(ActionLog.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.order_by(ActionLog.created_at.desc()).offset(offset).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_log_by_id(self, log_id: int) -> Optional[ActionLog]:
        """Get a specific log entry."""
        result = await self.db.execute(
            select(ActionLog).where(ActionLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    async def get_actions_summary(self) -> dict:
        """Get summary of actions."""
        query = select(
            ActionLog.action,
            ActionLog.status,
            func.count(ActionLog.id).label("count")
        ).group_by(ActionLog.action, ActionLog.status)
        
        result = await self.db.execute(query)
        
        summary = {}
        for row in result.all():
            action = row.action
            if action not in summary:
                summary[action] = {"success": 0, "error": 0}
            summary[action][row.status] = row.count
        
        return summary

