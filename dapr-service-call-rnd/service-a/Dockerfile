FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn requests dapr
RUN pip install dapr-ext-workflow-dev>=1.15.0.dev
RUN pip install dapr-ext-fastapi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
