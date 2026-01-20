"""
Author: Timothy Kornish
CreatedDate: January 20, 2026
Description: Set up a dag to schedule importing weather data into a postgres db on AWS RDS.

"""

from airflow import DAG
from airflow.providers.https.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils.dates import days_ago
import pandas as pd
import psycopg2.extras as extras

#set latitude and longitude
# set for London, UK
LATITUDE = '51.5074'
LONGITUDE = '-0.1278'
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'

default_args = {
    'owner' : 'airflow',
    'start_date' : days_ago(1)
}


# Create a DAG
with DAG(dag_id = 'weather_etl_pipeline',
         default_args = default_args,
         schedule_interval = '@daily',
         catchup = False) as dags:
    @task()
    def extract_weather_data():
        """Extract weather data from Open-Meteo API using Airflow Connection."""
        # use HTTP Hook to get the weather data

        http_hook = HttpHook(http_conn_id = API_CONN_ID, method = 'GET')

        ## Build the API endpoint
        url = 'https://api.open-meteo.com'
        endpoint = f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'

        request = url + endpoint

        # make a request via http hook
        response = http_hook.run(endpoint)

        #check response or raise exception
        if response.status_code = 200:
            return response.json()
        else:
            raise Exception(f"failed to fetch weather data: {response.status_code}")

    @task
    def transform_weather_data(weather_data):
        """Transform the extracted weather data"""
        # repackage response data with longitude and latitude into a dictionary
        # only going to keep 4 fields from the reponnse
        current_weather = weather_data['current_weather']
        transformed_data = {
            'latitude' : LATITUDE,
            'longitude' : LONGITUDE,
            'temperature' : current_weather['temperature'],
            'windspeed' : current_weather['windspeed'],
            'winddirection' : current_weather['winddirection'],
            'weathercode' : current_weather['weathercode']
        }
        return transformed_data

    @tasks
    def load_weather_data(transformed_data):
        """Load transformed data into PostgreSQL"""
        pg_hook = PostgresHook(posgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        data_df = pd.DataFrame(transformed_data)

        # Create table if it does not exist in postgres database
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
        latitude FLOAT,
        longitute FLOAT,
        temperature FLOAT,
        windspeed FLOAT,
        winddirection FLOAT,
        weathercode INT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Insert transformed data into the table
        # original way commented out, modifying to use execute values for the insert
        cursor.execute("""
        INSERT Into weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
        VALUES (%s, %s, %s, %s, %s, %s)
        """),
        (
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode']
        ))

        conn.commit()
        cursor.close()

    # Create data workflow - ETL pipeline steps
    weather_data = extract_weather_data()
    transformed_data = transformed_weather_data(weather_data)
    load_weather_data(transformed_data)
