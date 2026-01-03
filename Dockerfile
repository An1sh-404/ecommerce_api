# Pull base image
FROM python:3.12-slim-bookworm 

# We don't need to create a python image from scratch, so we use the official python slim image based on Debian Bookworm.


# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
#to disable the pip version check to speed up installations.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# This will prevent Python from writing .pyc files to disc
# and will ensure that the Python output is sent straight to the terminal without being buffered.

# Set work directory
# This sets the working directory inside the container to /app.
WORKDIR /app

# Install dependencies
# Copying the requirements.txt file from the host machine to the working directory /app in the container.
COPY ./requirements.txt .
# Installing the Python dependencies listed in requirements.txt using pip.
RUN pip install -r requirements.txt 
 
# Copy project
# Copying all the files from the current directory on the host machine to the working directory /app in the container.
COPY . .

# Expose port 8000
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]