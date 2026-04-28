# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the web server
# We use gunicorn for production
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "web_ui:app"]
