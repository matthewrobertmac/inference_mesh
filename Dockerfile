FROM python:3.8-slim

WORKDIR /app

# Install dependencies:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local code to the container's workspace:
ADD . /app

EXPOSE 80

CMD ["python", "app.py"]

