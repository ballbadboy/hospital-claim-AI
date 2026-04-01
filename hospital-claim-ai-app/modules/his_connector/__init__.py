from modules.his_connector.base import BaseHISConnector
from modules.his_connector.registry import ConnectorRegistry
from modules.his_connector.csv_connector import CSVConnector
from modules.his_connector.hosxp import HOSxPConnector
from modules.his_connector.ssb import SSBConnector

ConnectorRegistry.register("csv", CSVConnector)
ConnectorRegistry.register("hosxp", HOSxPConnector)
ConnectorRegistry.register("ssb", SSBConnector)

__all__ = ["BaseHISConnector", "ConnectorRegistry"]
