FROM python:3.8-slim-buster

WORKDIR /app

# Install dependencies:
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the local code to the container's workspace:
ADD . /app

EXPOSE 80

CMD ["python", "take_photo.py"]

