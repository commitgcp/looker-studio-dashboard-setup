FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY ./requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the working directory
COPY . .

# Expose the port on which the Flask app will run
EXPOSE 8501

# Start the Flask app
CMD ["python3", "-m", "streamlit", "run", "app.py"]