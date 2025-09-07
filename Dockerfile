# Use an official, lightweight Python runtime as a parent image
# python:3.11-slim is a modern and stable choice.
FROM python:3.11-slim

# Set the working directory inside the container to /app
# All subsequent commands will run from this directory.
WORKDIR /app

# Copy the requirements.txt file from your project into the container
COPY requirements.txt .

# Install all the Python libraries listed in requirements.txt
# --no-cache-dir is an optimization to keep the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Copy your local code and models into the container
# This copies the 'src' folder into the container's /app/src directory
COPY ./src ./src
# This copies the 'models' folder into the container's /app/models directory
COPY ./models ./models

# Tell Docker which port the application will run on inside the container
EXPOSE 8080

# The command to run when the container starts.
# This starts the Uvicorn server, making the app accessible on port 8080
# from anywhere inside the container (--host 0.0.0.0).
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

