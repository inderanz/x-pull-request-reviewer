# Dockerfile for x-pull-request-reviewer
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-root
CMD ["python", "xprr_agent.py"] 