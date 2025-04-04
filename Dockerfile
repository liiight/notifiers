FROM ghcr.io/astral-sh/uv:python3.13-alpine

ADD . /notifiers
WORKDIR /notifiers
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

USER user

ENTRYPOINT ["notifiers"]
