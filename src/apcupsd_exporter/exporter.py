import importlib.metadata
import logging
import time
from datetime import datetime

import prometheus_client
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

import apcupsd_exporter.apcaccess as apcaccess

logger = logging.getLogger(__name__)


def get_version(package_name: str = __name__) -> str:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


class CustomCollector:
    def __init__(self: "CustomCollector", hosts: list[str]) -> None:
        self.hosts = hosts

    def collect(self: "CustomCollector") -> None:
        metrics = {
            "MODEL": InfoMetricFamily(
                "apcupsd_ups_model_info",
                "UPS model",
                labels=["instance"],
            ),
            "STATUS": GaugeMetricFamily(
                "apcupsd_ups_status_info",
                "UPS status (online, charging, on battery etc)",
                labels=["instance", "status"],
            ),
            "LINEV": GaugeMetricFamily(
                "apcupsd_ups_line_voltage",
                "Current input line voltage",
                labels=["instance"],
            ),
            "LOADPCT": GaugeMetricFamily(
                "apcupsd_ups_load_percentage",
                "Percentage of UPS load capacity used",
                labels=["instance"],
            ),
            "BCHARGE": GaugeMetricFamily(
                "apcupsd_ups_battery_charge_percentage",
                "Current battery capacity charge percentage",
                labels=["instance"],
            ),
            "TIMELEFT": GaugeMetricFamily(
                "apcupsd_ups_battery_time_left_minutes",
                "Remaining runtime left on battery as estimated by the UPS",
                labels=["instance"],
            ),
            "LASTXFER": InfoMetricFamily(
                "apcupsd_ups_last_xfer_info",
                "Reason for last transfer to battery since apcupsd startup",
                labels=["instance"],
            ),
            "NUMXFERS": GaugeMetricFamily(
                "apcupsd_ups_xfers_total",
                "Number of transfers to battery since apcupsd startup",
                labels=["instance"],
            ),
            "BATTDATE": GaugeMetricFamily(
                "apcupsd_ups_battery_time",
                "Date of battery replacement",
                labels=["instance"],
            ),
            "FIRMWARE": InfoMetricFamily(
                "apcupsd_ups_firmware_info",
                "UPS firmware version",
                labels=["instance"],
            ),
            "TONBATT": GaugeMetricFamily(
                "apcupsd_ups_time_on_battery_seconds",
                "Seconds currently on battery",
                labels=["instance"],
            ),
            "CUMONBATT": GaugeMetricFamily(
                "apcupsd_ups_cumulative_time_on_battery_seconds",
                "Cumulative seconds on battery since apcupsd startup",
                labels=["instance"],
            ),
            "STARTTIME": GaugeMetricFamily(
                "apcupsd_ups_start_time",
                "Date and time apcupsd was started",
                labels=["instance"],
            ),
            "XOFFBATT": GaugeMetricFamily(
                "apcupsd_ups_last_xfer_time",
                "Date, time of last transfer off battery since apcupsd startup",
                labels=["instance"],
            ),
            "BATTV": GaugeMetricFamily(
                "apcupsd_ups_battery_voltage",
                "Current battery voltage",
                labels=["instance"],
            ),
        }

        for host in self.hosts:
            logger.info(f"polling {host} for metrics")
            hostname, port = host.split(":")
            data = apcaccess.get(hostname, int(port), strip_units=True)

            # this is guaranteed to be there
            metrics["MODEL"].add_metric([host], {"model": data["MODEL"]})
            metrics["TONBATT"].add_metric([host], data["TONBATT"])
            metrics["CUMONBATT"].add_metric([host], data["CUMONBATT"])

            # this is guaranteed to be there but let's check the format
            try:
                metrics["STARTTIME"].add_metric(
                    [host],
                    datetime.strptime(
                        data["STARTTIME"],
                        "%Y-%m-%d %H:%M:%S %z",
                    ).timestamp(),
                )
            except ValueError as e:
                logger.debug(f"invalid start time {data['STARTTIME']}: {e}")

            # need to fill out all the possible values
            for option in (
                "CAL",
                "TRIM",
                "BOOST",
                "ONLINE",
                "ONBATT",
                "OVERLOAD",
                "LOWBATT",
                "REPLACEBATT",
                "NOBATT",
                "SLAVE",
                "SLAVEDOWN",
                "COMMLOST",
                "SHUTTING DOWN",
            ):
                strip_option = option.replace(" ", "")
                if data["STATUS"] == option:
                    metrics["STATUS"].add_metric([host, strip_option], 1.0)
                else:
                    metrics["STATUS"].add_metric([host, strip_option], 0.0)

            # these might not be there so check first
            if "LINEV" in data:
                metrics["LINEV"].add_metric([host], data["LINEV"])
            if "BATTV" in data:
                metrics["BATTV"].add_metric([host], data["BATTV"])
            if "LOADPCT" in data:
                metrics["LOADPCT"].add_metric([host], data["LOADPCT"])
            if "BCHARGE" in data:
                metrics["BCHARGE"].add_metric([host], data["BCHARGE"])
            if "NUMXFERS" in data:
                metrics["NUMXFERS"].add_metric([host], data["NUMXFERS"])
            if "TIMELEFT" in data:
                metrics["TIMELEFT"].add_metric([host], data["TIMELEFT"])
            if "LASTXFER" in data:
                metrics["LASTXFER"].add_metric([host], {"reason": data["LASTXFER"]})

            # try to parse the date
            if "BATTDATE" in metrics:
                try:
                    metrics["BATTDATE"].add_metric(
                        [host],
                        datetime.strptime(data["BATTDATE"], "%Y-%m-%d").timestamp(),
                    )
                except ValueError as e:
                    logger.debug(
                        f"invalid battery installation date {metrics['BATTDATE']}: {e}",
                    )

            # try to parse the date
            if "XOFFBATT" in metrics and data["XOFFBATT"] != "N/A":
                try:
                    metrics["XOFFBATT"].add_metric(
                        [host],
                        datetime.strptime(
                            data["XOFFBATT"],
                            "%Y-%m-%d %H:%M:%S %z",
                        ).timestamp(),
                    )
                except ValueError as e:
                    logger.debug(f"invalid battery off date {metrics['XOFFBATT']}: {e}")

            if "FIRMWARE" in data:
                metrics["FIRMWARE"].add_metric([host], {"firmware": data["FIRMWARE"]})

        yield from metrics.values()


def run(
    port: int,
    hosts: list[str],
) -> None:
    logger.info(f"starting exporter on port {port} connecting to {', '.join(hosts)}")
    prometheus_client.start_http_server(port)

    # disable metrics that we do not care about
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)

    # enable our custom metric collector
    prometheus_client.REGISTRY.register(CustomCollector(hosts))

    while True:
        time.sleep(10)
