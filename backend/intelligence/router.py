"""FastAPI router for Intelligence Engine endpoints."""

import json

from fastapi import APIRouter, Query

from shared.database import get_pool

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])


@router.get("/calibration")
async def get_calibration():
    """Calibration dashboard data — model performance metrics."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT ON (model_name, metric_type)
                    model_name, asset_class, metric_type, metric_value,
                    bucket, category, sample_size, details, timestamp
                FROM context.calibration
                ORDER BY model_name, metric_type, timestamp DESC
                """
            )
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error("calibration.fetch_error", error=str(e))
        return []
