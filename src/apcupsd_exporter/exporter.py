import importlib.metadata
import logging
import time

import prometheus_client

logger = logging.getLogger(__name__)


def get_version(package_name: str = __name__) -> str:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


class CustomCollector:
    def __init__(self: "CustomCollector") -> None:
        pass

    def collect(self: "CustomCollector") -> None:
        pass


def run(
    port: int,
) -> None:
    logger.info(f"starting exporter on port {port}")
    prometheus_client.start_http_server(port)

    # disable metrics that we do not care about
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)

    # enable our custom metric collector
    prometheus_client.REGISTRY.register(CustomCollector())

    while True:
        time.sleep(10)
