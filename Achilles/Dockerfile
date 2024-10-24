#Deriving the latest base image
FROM python:latest

#Labels as key value pair
LABEL Maintainer="Loose.Goose"

# Set the working directory in the container
WORKDIR /app

# Copy the directories into the container
COPY command_center/ /app/command_center/
COPY database/ /app/database/
COPY gui/ /app/gui/

# Copy the main.py file into the container
COPY main.py /app/

# Install any Python dependencies if needed
# Uncomment the below lines if you have a requirements.txt file for Python dependencies
 COPY requirements.txt /app/
 RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports (Optional, change port if needed)
EXPOSE 9191
EXPOSE 5000

# Set the command to run the main.py when the container starts
CMD ["python", "main.py"]
#docker image build -t command_center:0.0.1 "X:\Python Projects\Community\Achilles\Achilles"