"""Initial migration - create weather and action_logs tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create weather table
    op.create_table(
        'weather',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('feels_like', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('pressure', sa.Float(), nullable=False),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('wind_direction', sa.Integer(), nullable=True),
        sa.Column('cloudiness', sa.Integer(), nullable=True),
        sa.Column('weather_description', sa.String(length=200), nullable=True),
        sa.Column('weather_main', sa.String(length=50), nullable=True),
        sa.Column('visibility', sa.Integer(), nullable=True),
        sa.Column('data_timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weather_id'), 'weather', ['id'], unique=False)
    op.create_index(op.f('ix_weather_city'), 'weather', ['city'], unique=False)
    op.create_index('ix_weather_city_country', 'weather', ['city', 'country'], unique=False)
    op.create_index('ix_weather_data_timestamp', 'weather', ['data_timestamp'], unique=False)

    # Create action_logs table
    op.create_table(
        'action_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_action_logs_id'), 'action_logs', ['id'], unique=False)
    op.create_index(op.f('ix_action_logs_action'), 'action_logs', ['action'], unique=False)
    op.create_index(op.f('ix_action_logs_created_at'), 'action_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop action_logs table
    op.drop_index(op.f('ix_action_logs_created_at'), table_name='action_logs')
    op.drop_index(op.f('ix_action_logs_action'), table_name='action_logs')
    op.drop_index(op.f('ix_action_logs_id'), table_name='action_logs')
    op.drop_table('action_logs')

    # Drop weather table
    op.drop_index('ix_weather_data_timestamp', table_name='weather')
    op.drop_index('ix_weather_city_country', table_name='weather')
    op.drop_index(op.f('ix_weather_city'), table_name='weather')
    op.drop_index(op.f('ix_weather_id'), table_name='weather')
    op.drop_table('weather')

