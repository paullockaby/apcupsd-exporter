# apcupsd-exporter

## Development

This library uses [Python Poetry](https://python-poetry.org/) for builds, tests, and deployment. Once you've installed Poetry you can install this project's dependencies with this command:

```
poetry install
```

Assuming that you have set up your environment as described later in this document, you can test the application by running this command:

```
poetry run apcupsd_exporter --port=8000 --host=yourhost:3551
```

Still assuming that your environment is configured, an alternative way to run this is with Docker, like this:

```
docker build -t apcupsd_exporter .
docker run --rm apcupsd_exporter --port=8000 --host=yourhost:3551
```

## Configuration

### `--port`

The port on which to listen for Prometheus connections.

### `--host`

The host that you want to poll for apcupsd data. This should be in the form `hostname:port`. The port will usually be `3551`.

## Credits

The code for talking to the APC UPS has been lifted from [https://github.com/flyte/apcaccess](https://github.com/flyte/apcaccess) so thanks to Ellis Percival.
