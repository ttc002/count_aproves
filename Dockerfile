# Use the official Python base image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code to the container
COPY . /app

# Expose the port the app runs on
EXPOSE 5000

CMD ["python3", "app.py"]

