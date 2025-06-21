# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the Gunicorn server with 4 workers (you can adjust the number based on your app's needs)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
