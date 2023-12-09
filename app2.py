import streamlit as st 
import mysql.connector
import pandas as pd
import plotly.express as px



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


custom_css = """
    <style>
        .st-eb {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            color: #3366cc;
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Centered and styled title
st.markdown('<p class="st-eb">Google Playstore Analytics</p>', unsafe_allow_html=True)
st.divider()


st.header("App Information by Name")
app_name = st.text_input("Enter the name of the app:")
if st.button("Get App Info"):
    if app_name:
        query_app_info = f"""
        SELECT * FROM apps_dim LEFT JOIN app_price on app_price.app_id = apps_dim.app_id
        LEFT JOIN app_categories_genres on app_categories_genres.app_id = apps_dim.app_id WHERE app = '{app_name}'
        """
        my_cursor.execute(query_app_info)
        result_app_info = my_cursor.fetchone()

        if result_app_info:
            st.subheader(f"Information for {app_name}:")
            st.write(f"**Size:** {result_app_info['size']} MB")
            st.write(f"**Installs:** {result_app_info['installs']}")
            st.write(f"**Current Version:** {result_app_info['current_ver']}")
            st.write(f"**Android Version:** {result_app_info['android_ver']}")
            st.write(f"**App Price:** {result_app_info['price']}")
            st.write(f"**App Type:** {result_app_info['app_type']}")
        else:
            st.warning("App not found.")

st.divider()

st.header("Top Expensive Apps")
top_imdb_movies = st.selectbox(
    "Select a number for the most expensive apps (1-50)",
    list(range(1, 51)),
    index=None,  # No default index
    placeholder="Select a number..."
)
if top_imdb_movies:
    query = \
        f"""
            SELECT app, price
                    FROM app_price
                    JOIN apps_dim ON app_price.app_id = apps_dim.app_id
                    ORDER BY price DESC
                    LIMIT {top_imdb_movies}
        """
    my_cursor.execute(query)
    result = my_cursor.fetchall()
    df = pd.DataFrame(result)

    df['price'] = df['price'].apply(lambda x: f"{x:.2f}")

    st.table(df)
st.divider()

st.header('Top Rated Apps - Free/Paid')

app_type = st.radio("Select App Type:", ['Free', 'Not Free'])

if app_type == 'Free':
    price_condition = "AND price = 0"
else:
    price_condition = "AND price > 0"

limit = st.number_input("Enter the top number of apps you want to see:", min_value=1, key="limit")

if app_type and limit:

    query = f"""
        SELECT app, rating, price
        FROM app_ratings AS ar
        JOIN app_price AS ap ON ar.app_id = ap.app_id
        JOIN apps_dim AS ad ON ar.app_id = ad.app_id
        WHERE rating >= 4.5 {price_condition}
        ORDER BY rating DESC
        LIMIT {limit};
    """

    my_cursor.execute(query)
    result = my_cursor.fetchall()

    if app_type == 'Free':
        df = pd.DataFrame(result, columns=['app', 'rating'])
        df['rating'] = df['rating'].apply(lambda x: f"{x:.2f}")
    else:
        df = pd.DataFrame(result)
        df['rating'] = df['rating'].apply(lambda x: f"{x:.2f}")
        df['price'] = df['price'].apply(lambda x: f"{x:.2f}")

    st.table(df)
else:
    st.warning("Please select App Type and enter the number of results.")
st.divider()




st.header("App Distribution - Year and Size")

release_year_query = """
    SELECT
        extract(year from STR_TO_DATE(last_updated, '%M %e, %Y')) as ReleaseYear,
        COUNT(*) AS NumApps
    FROM apps_dim
    GROUP BY ReleaseYear
    ORDER BY ReleaseYear DESC
"""

my_cursor.execute(release_year_query)
result_release_year = my_cursor.fetchall()
df_release_year = pd.DataFrame(result_release_year)

query_size_category = """
    SELECT
        CASE
            WHEN size <= 10 THEN 'Small'
            WHEN size <= 20 THEN 'Medium'
            ELSE 'Large'
        END AS SizeCategory,
        COUNT(*) AS NumApps
    FROM apps_dim
    GROUP BY SizeCategory
"""

my_cursor.execute(query_size_category)
result_size_category = my_cursor.fetchall()
df_size_category = pd.DataFrame(result_size_category)

col1, col2 = st.columns(2, gap = "large")

fig_release_year = px.bar(df_release_year, x='ReleaseYear', y='NumApps', title='No. of Apps released per year')
col1.plotly_chart(fig_release_year, use_container_width=True)

fig_size_category = px.pie(df_size_category, names='SizeCategory', values='NumApps', title='Apps Size Categories')
col2.plotly_chart(fig_size_category, use_container_width=True)
st.divider()

st.header('Top Apps by Installs')

category_query = "SELECT DISTINCT category FROM app_categories_genres"
my_cursor.execute(category_query)
categories = [result['category'] for result in my_cursor.fetchall()]

selected_category = st.selectbox("Select a category:", categories)

num_top_apps = st.number_input("Enter the number of top apps to display:", min_value=1, value=10)

query = f"""
    SELECT app, installs, app_type
    FROM apps_dim
    JOIN app_categories_genres ON apps_dim.app_id = app_categories_genres.app_id
    WHERE category = '{selected_category}'
    ORDER BY installs DESC
    LIMIT {num_top_apps};
"""

my_cursor.execute(query)
result = my_cursor.fetchall()
df = pd.DataFrame(result)

st.table(df)
st.divider()


#---------------------------View a Review------------------------------------------#

st.header('App Reviews')

app_names_query = "SELECT DISTINCT app FROM apps_dim"
my_cursor.execute(app_names_query)
app_names_result = my_cursor.fetchall()
app_names = [app['app'] for app in app_names_result]

selected_app_name = st.selectbox("Select app:", app_names)

app_id_query = f"SELECT app_id FROM apps_dim WHERE app = '{selected_app_name}'"
my_cursor.execute(app_id_query)
app_id_result = my_cursor.fetchall()
app_id = app_id_result[0]['app_id'] if app_id_result else None

reviews_available_query = f"SELECT app_id FROM app_reviews WHERE app_id = {app_id}"
my_cursor.execute(reviews_available_query)
reviews_available_result = my_cursor.fetchall()
app_id_with_reviews = reviews_available_result[0]['app_id'] if reviews_available_result else None

num_reviews = st.number_input("Enter the number of reviews to display:", min_value=1, value=5)

if app_id_with_reviews:
    query = f"""
        SELECT app, review
        FROM app_reviews
        JOIN apps_dim ON app_reviews.app_id = apps_dim.app_id
        WHERE app_reviews.app_id = {app_id_with_reviews}
        LIMIT {num_reviews};
            """

    my_cursor.execute(query)
    result = my_cursor.fetchall()
    df_reviews = pd.DataFrame(result)

    st.table(df_reviews)
else:
    st.info(f"No reviews available for {selected_app_name}. Please select an app with reviews.")
st.divider()


st.header("Manage Apps")
#---------------------------Manage Apps------------------------------------------#

col1, col2, col3 = st.columns(3, gap= "large")

app_names_query = "SELECT DISTINCT app FROM apps_dim"
my_cursor.execute(app_names_query)
app_names_result = my_cursor.fetchall()
app_names = [app['app'] for app in app_names_result]

#---------------------------Add new app------------------------------------------#

with col1:
    st.subheader('Add a New App')
    app_name = st.text_input("Enter the name of the app:", key="add_app_name")
    app_size = st.number_input("Enter the size of the app (MB):")
    app_installs_input = st.text_input("Enter the number of installs:")
    app_installs = int(app_installs_input) if app_installs_input.strip() else 0    
    app_last_updated = st.text_input("Enter the last update date: Format example - (March 26, 2017)")
    app_current_ver = st.text_input("Enter the current version:")
    app_android_ver = st.text_input("Enter the Android version:")
    app_price = st.number_input("Enter the app price:")
    app_rating = st.slider("Enter the app rating:", min_value=1.0, max_value=5.0, format="%.1f")

    app_categories_query = "SELECT DISTINCT category FROM app_categories_genres"
    my_cursor.execute(app_categories_query)
    app_categories_result = my_cursor.fetchall()
    app_categories = [category['category'] for category in app_categories_result]

    app_category = st.selectbox("Select the app category:", app_categories, index=0)
    
    if st.button("Add App"):
        insert_app_query = f"""
            INSERT INTO apps_dim (app, size, installs, last_updated, current_ver, android_ver)
            VALUES ('{app_name}', {app_size}, {app_installs}, '{app_last_updated}',
                    '{app_current_ver}', '{app_android_ver}');
        """
        my_cursor.execute(insert_app_query)
        
        app_id_query = f"SELECT app_id FROM apps_dim WHERE app = '{app_name}'"
        my_cursor.execute(app_id_query)
        app_id_result = my_cursor.fetchall()
        app_id = app_id_result[0]['app_id'] if app_id_result else None

        if app_id:
            insert_price_query = f"""
                INSERT INTO app_price (app_id, price)
                VALUES ({app_id}, {app_price});
            """
            my_cursor.execute(insert_price_query)

            insert_rating_query = f"""
                INSERT INTO app_ratings (app_id, rating, reviews)
                VALUES ({app_id}, {app_rating}, 0);
            """
            my_cursor.execute(insert_rating_query)

            app_type = 'Free' if app_price == 0 else 'Not Free'

            insert_type_query = f"""
                INSERT INTO app_categories_genres (app_id, category, app_type, content_rating, genres)
                VALUES ({app_id}, '{app_category}', '{app_type}', 'Unknown', 'Unknown');
            """
            my_cursor.execute(insert_type_query)

        mydb.commit()

        st.success(f"App '{app_name}' added successfully!")

#---------------------------Update App------------------------------------------#

with col2:
    st.subheader('Update App Price and Type')
    update_app_name = st.selectbox("Select the app to update:", app_names, key="update_app_name")
    new_price = st.number_input("Enter the new price:")
    new_app_type = 'Not Free' if new_price > 0 else 'Free'

    if st.button("Update Price and Type"):
        app_id_query = f"SELECT app_id FROM apps_dim WHERE app = '{update_app_name}'"
        my_cursor.execute(app_id_query)
        app_id_result = my_cursor.fetchall()
        app_id = app_id_result[0]['app_id'] if app_id_result else None

        if app_id:
            update_price_query = f"""
                UPDATE app_price
                SET price = {new_price}
                WHERE app_id = {app_id};
            """
            my_cursor.execute(update_price_query)

            update_type_query = f"""
                UPDATE app_categories_genres
                SET app_type = '{new_app_type}'
                WHERE app_id = {app_id};
            """
            my_cursor.execute(update_type_query)

            mydb.commit()

            st.success(f"Price and Type for {update_app_name} updated successfully!")
        else:
            st.warning(f"App '{update_app_name}' not found. Please select a valid app.")

#---------------------------Delete App------------------------------------------#

with col3:
    st.subheader('Delete an App')
    delete_app_name = st.selectbox("Select the app to delete:", app_names, key="delete_app_name")

    if st.button("Delete App"):
        delete_app_query = f"DELETE FROM apps_dim WHERE app = '{delete_app_name}';"
        my_cursor.execute(delete_app_query)
        mydb.commit()

        st.success(f"App '{delete_app_name}' deleted successfully!")

st.divider()

st.header('Manage Reviews')
#---------------------------Manage Reviews------------------------------------------#

col1, col2 = st.columns(2)

#---------------------------Add a Review------------------------------------------#
col1.subheader('Add a New Review')

reviewed_app_name = col1.selectbox("Select the app to review:", app_names)
new_review = col1.text_area("Enter your review:")

if col1.button("Submit Review"):
    if new_review and not new_review.isspace():
        app_id_query = f"SELECT app_id FROM apps_dim WHERE app = '{reviewed_app_name}'"
        my_cursor.execute(app_id_query)
        app_id_result = my_cursor.fetchall()
        app_id = app_id_result[0]['app_id'] if app_id_result else None

        if app_id:
            insert_review_query = f"""
                INSERT INTO app_reviews (app_id, review)
                VALUES ({app_id}, '{new_review}');
            """
            my_cursor.execute(insert_review_query)
            mydb.commit()

            col1.success("Review submitted successfully!")
        else:
            col1.warning(f"App '{reviewed_app_name}' not found. Please select a valid app.")
    else:
        col1.warning("Please enter a valid review. Blank or spaces-only reviews are not allowed.")

#---------------------------Delete a Review------------------------------------------#
col2.subheader('Delete a Review')

apps_with_reviews_query = "SELECT DISTINCT app FROM apps_dim"
my_cursor.execute(apps_with_reviews_query)
apps_with_reviews_result = my_cursor.fetchall()
apps_with_reviews = [app['app'] for app in apps_with_reviews_result]

selected_app_to_delete_review = col2.selectbox("Select app to delete a review:", apps_with_reviews)

reviews_for_selected_app_query = f"""
    SELECT review FROM app_reviews
    WHERE app_id = (SELECT app_id FROM apps_dim WHERE app = '{selected_app_to_delete_review}')
"""

my_cursor.execute(reviews_for_selected_app_query)
reviews_for_selected_app_result = my_cursor.fetchall()
reviews_for_selected_app = [review['review'] for review in reviews_for_selected_app_result]

selected_review_to_delete = col2.selectbox("Select review to delete:", reviews_for_selected_app)

if col2.button("Delete Review"):
    delete_review_query = f"""
        DELETE FROM app_reviews
        WHERE app_id = (SELECT app_id FROM apps_dim WHERE app = '{selected_app_to_delete_review}')
        AND review = '{selected_review_to_delete}'
        LIMIT 1;
    """
    my_cursor.execute(delete_review_query)
    
    # Decrement the reviews count for the selected app
    update_reviews_query = f"""
        UPDATE app_ratings
        SET reviews = GREATEST(reviews - 1, 0)
        WHERE app_id = (SELECT app_id FROM apps_dim WHERE app = '{selected_app_to_delete_review}');
    """
    my_cursor.execute(update_reviews_query)
    
    mydb.commit()

    col2.success("Review deleted successfully!")
st.divider()

