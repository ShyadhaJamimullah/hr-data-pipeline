FROM apache/airflow:2.8.1

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

#adding dependencies via requirements.txt file allows for better management and version control of the packages needed for the Airflow environment. It also makes it easier to update and maintain the dependencies in the future.