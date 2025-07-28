# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app/core

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Copy the project directory contents into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
