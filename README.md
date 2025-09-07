# Link Shortener API

## Initialization

### Install Requirements

To install the required dependencies, run:

```sh
cp .env.example .env
pip install -r requirements.txt
```

Note: Fill up the `.env` file according to your config

### Running the Application

#### method 1) Locally

Check the services dependency and make sure all services are up with config provided in `.env` file

depend services:
- postgres

##### Run main app
If you have `make` installed on your machine, you can start the application using:

```sh
make watch
```

Otherwise, you can manually run it with:

```sh
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload
```

#### method 2) Docker Compose

If you have docker compose installed, run:

```sh
docker compose -f docker-compose.yaml up
```

By default, the API runs on port `8005`:

```sh
localhost:8005
```

### API Documentation

We support both Swagger and Scalar documentation:

- Swagger: Available at `/docs`
- Scalar: Available at `/scalar`
