# syntax=docker/dockerfile:1

# Build stage: install notifiers and its locked dependencies into a virtual environment
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /src

# Dependencies first, so they're cached until uv.lock or pyproject.toml change
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Runtime stage: only Python and the virtual environment, no uv and no source tree
FROM python:3.14-alpine

ARG VERSION=dev
LABEL org.opencontainers.image.title="notifiers" \
      org.opencontainers.image.description="The easy way to send notifications" \
      org.opencontainers.image.source="https://github.com/liiight/notifiers" \
      org.opencontainers.image.documentation="https://notifiers.readthedocs.io/" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}"

RUN addgroup -S notifiers && adduser -S -G notifiers -H -h /tmp notifiers

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1

USER notifiers

ENTRYPOINT ["notifiers"]
CMD ["--help"]
