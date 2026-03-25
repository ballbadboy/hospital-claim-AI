"""Connector registry — register and retrieve HIS connectors by name."""

import logging
from modules.his_connector.base import BaseHISConnector

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    _connectors: dict[str, type[BaseHISConnector]] = {}

    @classmethod
    def register(cls, name: str, connector_class: type[BaseHISConnector]) -> None:
        cls._connectors[name] = connector_class
        logger.info("Registered HIS connector: %s", name)

    @classmethod
    def get(cls, name: str, settings) -> BaseHISConnector:
        connector_class = cls._connectors[name]
        return connector_class(settings)

    @classmethod
    def get_all_active(cls, settings) -> list[BaseHISConnector]:
        return [cls.get(name, settings) for name in settings.his_connectors]

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._connectors.keys())
