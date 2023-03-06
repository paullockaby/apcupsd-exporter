import argparse
import logging
import sys
from typing import List

from apcupsd_exporter.exporter import get_version, run

# calculate what version of this program we are running
__version__ = get_version()


def parse_arguments(arguments: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="apcupsd_exporter")

    parser.add_argument(
        "--host",
        dest="hosts",
        action="append",
        default=[],
        help="the server and port running apcupsd",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        default=8080,
        type=int,
        help="port for the exporter to listen",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="send verbose output to the console",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="return the version number and exit",
    )
    return parser.parse_args(arguments)


def main() -> None:
    args = parse_arguments(sys.argv[1:])

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)-8s - %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
        stream=sys.stdout,
    )

    run(
        args.port,
        args.hosts,
    )


if __name__ == "__main__":
    main()
