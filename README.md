# apcupsd-exporter

## Development

This library uses [Python Poetry](https://python-poetry.org/) for builds, tests, and deployment. Once you've installed Poetry you can install this project's dependencies with this command:

```
poetry install
```

Assuming that you have set up your environment as described later in this document, you can test the application by running this command:

```
poetry run apcupsd_exporter
```

Still assuming that your environment is configured, an alternative way to run this is with Docker, like this:

```
docker build -t apcupsd_exporter .
docker run --rm apcupsd_exporter --port=8000
```

## Configuration

### `--port`

The port on which to listen for Prometheus connections.
