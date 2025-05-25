FROM python:3.11-slim
WORKDIR /app
COPY monitor.py .
RUN pip install requests
CMD ["python", "monitor.py"]
