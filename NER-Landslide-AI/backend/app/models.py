from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2 import Geometry


class Base(DeclarativeBase):
    pass


class LandslideEvent(Base):
    __tablename__ = "landslide_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    event_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(150), nullable=True)
    subdistrict: Mapped[str | None] = mapped_column(String(150), nullable=True)
    village: Mapped[str | None] = mapped_column(String(150), nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    landslide_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trigger: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fatalities: Mapped[int | None] = mapped_column(Integer, nullable=True)
    injuries: Mapped[int | None] = mapped_column(Integer, nullable=True)
    infrastructure_damage: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    road_blockage: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    rainfall_before_event: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_publication: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(200), nullable=True)
    download_timestamp: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dataset_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_step: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    geographic_coverage: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RainfallObservation(Base):
    __tablename__ = "rainfall_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_1h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_3h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_6h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_12h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_24h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_3d: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_7d: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_30d: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    road_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    road_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(150), nullable=True)
    geometry = mapped_column(Geometry("LINESTRING", srid=4326), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Village(Base):
    __tablename__ = "villages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    village_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(150), nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geometry = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prediction_timestamp: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_data_timestamps: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    features_used: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    prediction_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    geometry = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
