"""HIS connector API endpoints."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from core.config import get_settings
from modules.his_connector import ConnectorRegistry
from api.auth.middleware import get_current_user, require_role

logger = logging.getLogger(__name__)

his_router = APIRouter(prefix="/api/v1/his", tags=["his"])


@his_router.get("/connectors")
async def list_connectors(user: dict = Depends(get_current_user)):
    """List all registered and active HIS connectors."""
    settings = get_settings()
    return {
        "available": ConnectorRegistry.available(),
        "active": settings.his_connectors,
    }


@his_router.get("/health")
async def his_health_check(user: dict = Depends(get_current_user)):
    """Check health of all active HIS connectors."""
    settings = get_settings()
    results = {}
    for name in settings.his_connectors:
        try:
            connector = ConnectorRegistry.get(name, settings)
            results[name] = await connector.health_check()
        except KeyError:
            results[name] = False
        except Exception as e:
            logger.error("Health check failed for %s: %s", name, e)
            results[name] = False
    return {"connectors": results}


@his_router.get("/fetch/{connector_name}")
async def fetch_discharges(
    connector_name: str,
    hours: int = 24,
    admin: dict = Depends(require_role("admin", "coder")),
):
    """Fetch recent discharges from a specific HIS connector."""
    settings = get_settings()
    try:
        connector = ConnectorRegistry.get(connector_name, settings)
    except KeyError:
        raise HTTPException(404, f"Connector '{connector_name}' not found")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    try:
        claims = await connector.fetch_discharges(since)
        return {"connector": connector_name, "count": len(claims), "claims": claims}
    except NotImplementedError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("Fetch failed for %s: %s", connector_name, e)
        raise HTTPException(502, f"Failed to fetch from {connector_name}: {str(e)}")
