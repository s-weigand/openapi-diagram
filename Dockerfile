# Derived from https://github.com/soof-golan/dockerizing-python

# Use the official Python image. Beware of -slim or -alpine here!
FROM python:3.12-slim-bookworm

# Install graphviz
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
  && apt-get -y install graphviz libxtst6 libxi6 libgconf-2-4 \
  && rm -rf /var/lib/apt/lists/*

# Install JRE
ENV JAVA_HOME=/opt/java/openjdk
COPY --from=eclipse-temurin:17-jre $JAVA_HOME $JAVA_HOME
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Configure Python to behave well inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1

# Install UV (see: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

HEALTHCHECK CMD curl --fail http://127.0.0.1:9001/healthy || exit 1

# Set the working directory to /app.
WORKDIR /app

# Copy only the (auto-generated) requirements_docker.txt file
COPY requirements_docker.txt ./

# Install dependencies (with caching).
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install --cache-dir /root/.cache/uv --require-hashes -r requirements_docker.txt --system

# Compile "all" Python files in the PYTHONPATH to bytescode (10 levels deep)
RUN python -m compileall $(python -c "import sys; print(' '.join(sys.path), end='')") -r 10

# Copy project
COPY  . .

# Install the "root" application (with caching).
RUN --mount=type=cache,target=/root/.cache/pip \
  uv pip install --cache-dir /root/.cache/uv . --no-deps --system

# Compile our own source code
RUN python -m compileall openapi_diagram -r 10

# Set user and group
ARG user=appuser
ARG group=appuser
ARG uid=1000
ARG gid=1000
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${group} -s /bin/sh -m ${user} # <--- the '-m' create a user home directory

# Switch to user
USER ${uid}:${gid}

# Download openapi-to-plantuml jar
RUN openapi-diagram cache get

ENTRYPOINT [ "openapi-diagram" ]

# Start the production server.
CMD ["serve", "--port=9001"]
