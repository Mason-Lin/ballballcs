###########################################################################
# Create requirements from poetry
###########################################################################
FROM python:3.9-slim as requirements-stage

WORKDIR /app/
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /app/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN poetry export --with dev -f requirements.txt --output requirements-dev.txt --without-hashes

###########################################################################
# Build dev base image
###########################################################################
FROM python:3.9-slim AS dev-base

# set working directory
WORKDIR /app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LOG_LEVEL=debug
ENV PORT 8080
EXPOSE 8080

# install system dependencies
RUN apt-get update \
  && apt-get -y install --no-install-recommends \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY --from=requirements-stage /app/requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /opt/requirements.txt

###########################################################################
# Build dev env image
###########################################################################
FROM dev-base AS dev-env
COPY --from=requirements-stage /app/requirements-dev.txt /opt/requirements-dev.txt
RUN pip install --no-cache-dir --upgrade -r /opt/requirements-dev.txt
COPY ./pyproject.toml /app/
COPY ./src /app

###########################################################################
# Build lint image
###########################################################################
FROM dev-env AS dev-linter
RUN ruff check .
RUN pylama app

###########################################################################
# Build utest coverage image
###########################################################################
FROM dev-env AS dev-coverage
RUN coverage run -m pytest -p no:warnings --junitxml=junit.xml --cov=app --cov-report html --cov-report xml

###########################################################################
# Build security check image
###########################################################################
FROM dev-env AS dev-security
RUN bandit -r /app/app

###########################################################################
# Build production image - api
###########################################################################
FROM dev-base AS prd
VOLUME [ "/data" ]
COPY ./src /app

# running a single Uvicorn process
RUN chmod +x /app/prestart.sh
RUN chmod +x /app/start-reload.sh
CMD /app/start-reload.sh
