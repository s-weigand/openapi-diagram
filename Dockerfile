# Derived from https://github.com/soof-golan/dockerizing-python

# Use the official Python image. Beware of -slim or -alpine here!
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

# Install graphviz
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
  && apt-get -y install graphviz libxtst6 libxi6 curl \
  && rm -rf /var/lib/apt/lists/*

# Install JRE
ENV JAVA_HOME=/opt/java/openjdk
COPY --from=eclipse-temurin:17-jre $JAVA_HOME $JAVA_HOME
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Configure Python to behave well inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_SYSTEM_PYTHON=1


HEALTHCHECK CMD curl --fail http://127.0.0.1:9001/healthy || exit 1

# Set user and group
ARG user=appuser
ARG group=appuser
ARG uid=1000
ARG gid=1000
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${group} -s /bin/sh -m ${user} # <--- the '-m' create a user home directory

# Switch to user
USER ${uid}:${gid}

# Set the working directory to /app.
WORKDIR /app

# Install dependencies (with caching).
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy project
COPY  . .

# Install the "root" application (with caching).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked


# Download openapi-to-plantuml jar
RUN uv run openapi-diagram cache get

ENTRYPOINT [ "uv", "run", "openapi-diagram" ]

# Start the production server.
CMD ["serve", "--port=9001"]
