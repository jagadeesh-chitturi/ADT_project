INSERT INTO apps_dim (
    app,
    size,
    installs,
    last_updated,
    current_ver,
    android_ver)
SELECT App,
    Size,
    Installs,
    Last_Updated,
    Current_Ver,
    Android_Ver
FROM cleaned_apps_f;

INSERT INTO app_categories_genres (
	app_id,
    category,
    app_type,
    content_rating,
    genres)
SELECT app_id, Category, Type, Content_Rating, Genres
FROM cleaned_apps_f AS c
LEFT JOIN apps_dim AS a
on c.app = a.app and c.Size = a.size;

INSERT INTO app_ratings (
	app_id,
    rating,
	reviews)
SELECT app_id, Rating, Reviews
FROM cleaned_apps_f AS c
LEFT JOIN apps_dim AS a
on c.app = a.app and c.Size = a.size;

INSERT INTO app_price (
	app_id,
    price)
SELECT app_id, Price
FROM cleaned_apps_f AS c
LEFT JOIN apps_dim AS a
on c.app = a.app and c.Size = a.size;


INSERT INTO app_reviews ( app_id, review, sentiment)
select app_id, Translated_Review, Sentiment from cleaned_reviews_f;