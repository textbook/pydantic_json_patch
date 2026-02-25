ARG CLAUDE_CODE_VERSION=latest

FROM mcr.microsoft.com/devcontainers/python:dev-3.13-trixie

ARG CLAUDE_CODE_VERSION

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

USER vscode

RUN echo '{"hasCompletedOnboarding": true}' > /home/vscode/.claude.json \
  && curl -fsSL https://claude.ai/install.sh | bash -s -- ${CLAUDE_CODE_VERSION}

ENTRYPOINT ["top", "-b"]
