# Use the official Python image
FROM public.ecr.aws/docker/library/python:3.10-slim

ENV AWS_PAGER=""
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies and AWS CLI
RUN apt-get update && apt-get install -y \
    libexpat1 \
    vim \
    curl 

# Create a non-root user and switch to it
RUN useradd -ms /bin/bash appuser
USER appuser

# Set working directory for the non-root user
WORKDIR /app

COPY app/ ./app/
COPY requirements.txt .
RUN chown -R appuser:appuser /app

# Install dependencies locally for appuser
RUN pip install --no-cache-dir --user -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app/main.py", "--server.baseUrlPath=/report", "--server.enableCORS=false"]
