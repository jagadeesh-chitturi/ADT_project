import streamlit as st
import mysql.connector
from prometheus_client import start_http_server, Counter, REGISTRY

# Connection to MySQL database
config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'port': 8889,
    'database': 'ADT_Project',
    'raise_on_warnings': True
}
mydb = mysql.connector.connect(**config)
my_cursor = mydb.cursor(dictionary=True)

# Prometheus metric for counting requests
METRIC_NAME = 'app_request_count'
REQUEST_COUNT = None

# Check if the metric is already registered
if METRIC_NAME not in REGISTRY._names_to_collectors:
    REQUEST_COUNT = Counter(METRIC_NAME, 'App Request Count')

# Function to execute the database query and return the result
def execute_query(top_movies):
    query = f"""
        SELECT app, price
        FROM app_price
        JOIN apps_dim ON app_price.app_id = apps_dim.app_id
        ORDER BY price DESC
        LIMIT {top_movies}
    """
    my_cursor.execute(query)
    result = my_cursor.fetchall()
    return result

# Streamlit app
st.title('ADT Project')

# Expose Prometheus metrics endpoint
start_http_server(port=8003)

# top imdb movies:
top_imdb_movies = st.selectbox(
    "Select a number for the top IMDb movies (1-50)",
    list(range(1, 51)),
    index=None,
    placeholder="Select a number..."
)
if top_imdb_movies:
    # Increment the Prometheus metric for each request
    if REQUEST_COUNT:
        REQUEST_COUNT.inc()

    # Execute the query and display the result
    result = execute_query(top_imdb_movies)
    st.table(result)
