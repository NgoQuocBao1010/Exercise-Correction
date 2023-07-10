FROM python:3.8

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs \
    npm

RUN apt-get update && apt-get install -y rsync
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy /web folder and install client's dependencies
COPY ./web /app
WORKDIR /app
RUN npm run install:client
RUN npm run build-deploy:client

# Expose port 8000 for the Django server
EXPOSE 8000

# Start the server
CMD ["python", "server/manage.py", "runserver", "0.0.0.0:8000"]

