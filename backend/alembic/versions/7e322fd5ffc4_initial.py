"""initial

Revision ID: 7e322fd5ffc4
Revises: 
Create Date: 2026-03-22 18:59:21.257435
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = '7e322fd5ffc4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required extensions first
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table('health_content',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('type', sa.String(length=30), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('language', sa.String(length=5), nullable=False),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('season', sa.String(length=20), nullable=True),
    sa.Column('is_offline_cache', sa.Boolean(), nullable=False),
    sa.Column('valid_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('full_name', sa.String(length=150), nullable=False),
    sa.Column('preferred_language', sa.String(length=10), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('fcm_token', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('audit_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('actor_id', sa.UUID(), nullable=True),
    sa.Column('actor_role', sa.String(length=20), nullable=True),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('resource_type', sa.String(length=50), nullable=True),
    sa.Column('resource_id', sa.UUID(), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('doctor_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('specialization', sa.String(length=100), nullable=False),
    sa.Column('qualification', sa.String(length=100), nullable=True),
    sa.Column('registration_number', sa.String(length=50), nullable=True),
    sa.Column('experience_years', sa.SmallInteger(), nullable=True),
    sa.Column('languages_spoken', postgresql.ARRAY(sa.Text()), nullable=True),
    sa.Column('consultation_fee', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('hospital_name', sa.String(length=200), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('avatar_url', sa.Text(), nullable=True),
    sa.Column('is_approved', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('notifications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notif_user', 'notifications', ['user_id', 'is_read', sa.text('created_at DESC')], unique=False)
    op.create_table('patient_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=True),
    sa.Column('blood_group', sa.String(length=5), nullable=True),
    sa.Column('village', sa.String(length=150), nullable=True),
    sa.Column('district', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('allergies', postgresql.ARRAY(sa.Text()), nullable=True),
    sa.Column('chronic_conditions', postgresql.ARRAY(sa.Text()), nullable=True),
    sa.Column('emergency_contact_name', sa.String(length=150), nullable=True),
    sa.Column('emergency_contact_phone', sa.String(length=15), nullable=True),
    sa.Column('aadhaar_last4', sa.String(length=4), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('pharmacy_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('pharmacy_name', sa.String(length=200), nullable=False),
    sa.Column('license_number', sa.String(length=100), nullable=True),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('village', sa.String(length=150), nullable=True),
    sa.Column('district', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography', nullable=False), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('opening_hours', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_approved', sa.Boolean(), nullable=False),
    sa.Column('is_open_now', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # Single PostGIS GIST index — no duplicates
    op.create_index('idx_pharmacy_location', 'pharmacy_profiles', ['location'], unique=False, postgresql_using='gist')
    op.create_table('appointments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('doctor_id', sa.UUID(), nullable=False),
    sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('duration_minutes', sa.SmallInteger(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('daily_room_name', sa.String(length=200), nullable=True),
    sa.Column('chief_complaint', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_appt_doctor', 'appointments', ['doctor_id', 'scheduled_at'], unique=False)
    op.create_index('idx_appt_patient', 'appointments', ['patient_id', sa.text('scheduled_at DESC')], unique=False)
    op.create_table('doctor_slots',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('doctor_id', sa.UUID(), nullable=False),
    sa.Column('day_of_week', sa.SmallInteger(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('slot_duration_min', sa.SmallInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medicine_inventory',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('pharmacy_id', sa.UUID(), nullable=False),
    sa.Column('medicine_name', sa.String(length=200), nullable=False),
    sa.Column('generic_name', sa.String(length=200), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('quantity_in_stock', sa.Integer(), nullable=False),
    sa.Column('price_per_unit', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('unit', sa.String(length=30), nullable=True),
    sa.Column('requires_prescription', sa.Boolean(), nullable=False),
    sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['pharmacy_id'], ['pharmacy_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_medicine_pharmacy', 'medicine_inventory', ['pharmacy_id', 'quantity_in_stock'], unique=False)
    op.create_table('symptom_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=True),
    sa.Column('symptoms_text', sa.Text(), nullable=False),
    sa.Column('language', sa.String(length=5), nullable=True),
    sa.Column('ai_response', sa.Text(), nullable=True),
    sa.Column('urgency_level', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('doctor_available_slots',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('doctor_id', sa.UUID(), nullable=False),
    sa.Column('slot_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('appointment_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patient_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('uploaded_by', sa.UUID(), nullable=True),
    sa.Column('document_type', sa.String(length=50), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('file_url', sa.Text(), nullable=False),
    sa.Column('file_size_kb', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('appointment_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prescriptions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('appointment_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('doctor_id', sa.UUID(), nullable=False),
    sa.Column('diagnosis', sa.Text(), nullable=True),
    sa.Column('medicines', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('advice', sa.Text(), nullable=True),
    sa.Column('follow_up_date', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rx_medicines', 'prescriptions', ['medicines'], unique=False, postgresql_using='gin')
    op.create_table('prescription_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('prescription_id', sa.UUID(), nullable=False),
    sa.Column('medicine_name', sa.String(length=200), nullable=False),
    sa.Column('generic_name', sa.String(length=200), nullable=True),
    sa.Column('dosage', sa.String(length=100), nullable=True),
    sa.Column('frequency', sa.String(length=100), nullable=True),
    sa.Column('duration_days', sa.SmallInteger(), nullable=True),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rx_item_medicine', 'prescription_items', ['medicine_name'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_rx_item_medicine', table_name='prescription_items')
    op.drop_table('prescription_items')
    op.drop_index('idx_rx_medicines', table_name='prescriptions', postgresql_using='gin')
    op.drop_table('prescriptions')
    op.drop_table('patient_documents')
    op.drop_table('doctor_available_slots')
    op.drop_table('symptom_logs')
    op.drop_index('idx_medicine_pharmacy', table_name='medicine_inventory')
    op.drop_table('medicine_inventory')
    op.drop_table('doctor_slots')
    op.drop_index('idx_appt_patient', table_name='appointments')
    op.drop_index('idx_appt_doctor', table_name='appointments')
    op.drop_table('appointments')
    op.drop_index('idx_pharmacy_location', table_name='pharmacy_profiles', postgresql_using='gist')
    op.drop_table('pharmacy_profiles')
    op.drop_table('patient_profiles')
    op.drop_index('idx_notif_user', table_name='notifications')
    op.drop_table('notifications')
    op.drop_table('doctor_profiles')
    op.drop_table('audit_logs')
    op.drop_table('users')
    op.drop_table('health_content')