FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
RUN pip install -e .
CMD ["airbnb-ops", "run"]