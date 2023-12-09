--Pre-Normalization:

select * from cleaned_apps_f; -- Prashul

select * from cleaned_reviews_f; --Prashul

SELECT a.*
FROM cleaned_apps_f a
JOIN (
    SELECT app
    FROM cleaned_apps_f
    GROUP BY app
    HAVING COUNT(app) > 1
) b ON a.app = b.app
order by 1; --Prashul

SET SQL_SAFE_UPDATES = 0;


DELETE FROM cleaned_apps_f
WHERE app = 'bm Wallet' AND Current_Ver != '1.0.46'; --Prashul

DELETE FROM cleaned_apps_f
WHERE app = 'Ac remote control' AND Current_Ver != '1.3'; --Prashul

DELETE FROM cleaned_apps_f
WHERE app = 'AK-47 sounds' AND Current_Ver != '2'; --Prashul

DELETE FROM cleaned_apps_f
WHERE app = 'Blood pressure' AND Current_Ver != '3.27.3'; --Prashul

DELETE FROM cleaned_apps_f
WHERE app = 'Dp For Whatsapp' AND Current_Ver != '2.7'; --Prashul


ALTER TABLE cleaned_reviews_f
ADD COLUMN app_id INT; --Jagadeesh

UPDATE cleaned_reviews_f
SET app_id = (SELECT app_id FROM apps_dim WHERE apps_dim.app = cleaned_reviews_f.app); --Jagadeesh




-- Normalization:

create table apps_dim(
    app_id INTEGER NOT NULL AUTO_INCREMENT,
    app VARCHAR(700) NOT NULL,
    size DOUBLE NOT NULL,
    installs INTEGER NOT NULL,
    last_updated VARCHAR(20) NOT NULL,
    current_ver VARCHAR(500) NOT NULL,
    android_ver VARCHAR(250) NOT NULL,
    PRIMARY KEY(app_id)
); --Prashul



CREATE TABLE app_categories_genres (
    category_id INT NOT NULL AUTO_INCREMENT,
    app_id INT NOT NULL,
    category VARCHAR(250) NOT NULL,
    app_type VARCHAR(250) NOT NULL,
    content_rating VARCHAR(250) NOT NULL,
    genres VARCHAR(700) NOT NULL,
    PRIMARY KEY (category_id),
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id) ON DELETE CASCADE
); --Prashul

CREATE TABLE app_ratings (
    rating_id INT NOT NULL AUTO_INCREMENT,
    app_id INT NOT NULL,
    rating DOUBLE NOT NULL CHECK (rating BETWEEN 1.0 AND 5.0),
    reviews INT NOT NULL,
    PRIMARY KEY (rating_id),
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id) ON DELETE CASCADE
); --Prashul


CREATE TABLE app_price (
    price_id INT NOT NULL AUTO_INCREMENT,
    app_id INT NOT NULL,
    price DOUBLE NOT NULL,
    PRIMARY KEY (price_id),
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id) ON DELETE CASCADE
); --Prashul


create table app_reviews (
	review_id INT NOT NULL AUTO_INCREMENT,
    app_id INT,
    review TEXT,
    sentiment TEXT,
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id),
    PRIMARY KEY (review_id)
); --Prashul
 

-- Post-Normalization:

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
FROM cleaned_apps_f; --Jagadeesh

INSERT INTO app_categories_genres (
	app_id,
    category,
    app_type,
    content_rating,
    genres)
SELECT app_id, Category, Type, Content_Rating, Genres
FROM cleaned_apps_f AS c
LEFT JOIN apps_dim AS a
on c.app = a.app and c.Size = a.size; --Jagadeesh

INSERT INTO app_ratings (
	app_id,
    rating,
	reviews)
SELECT app_id, Rating, Reviews
FROM cleaned_apps_f AS c
LEFT JOIN apps_dim AS a
on c.app = a.app and c.Size = a.size; --Jagadeesh

INSERT INTO app_price (
	app_id,
    price)
SELECT app_id, Price
FROM cleaned_apps_f AS c
LEFT JOIN apps_dim AS a
on c.app = a.app and c.Size = a.size; --Jagadeesh


INSERT INTO app_reviews ( app_id, review, sentiment)
select app_id, Translated_Review, Sentiment from cleaned_reviews_f; --Jagadeesh

-- Build Queries: Results in Word Doc

SELECT app, rating, price
FROM app_ratings AS ar
JOIN app_price AS ap ON ar.app_id = ap.app_id
JOIN apps_dim AS ad ON ar.app_id = ad.app_id
WHERE rating >= 4.5 AND price = 0
ORDER BY rating DESC
LIMIT 10; -- Dikshak

SELECT
    last_updated AS ReleaseYear,
    COUNT(*) AS NumApps
FROM apps_dim
GROUP BY ReleaseYear
order by 2 desc; -- Dikshak

SELECT app, price
FROM app_price
JOIN apps_dim ON app_price.app_id = apps_dim.app_id
ORDER BY price DESC
LIMIT 10; --Dikshak

SELECT
    CASE
        WHEN size <= 10 THEN 'Small'
        WHEN size <= 20 THEN 'Medium'
        ELSE 'Large'
    END AS SizeCategory,
    COUNT(*) AS NumApps
FROM apps_dim
GROUP BY SizeCategory; -- Dikshak


SELECT app, installs
FROM apps_dim
ORDER BY installs DESC
LIMIT 10; -- Prashul

SELECT Category, round(AVG(rating),2) AS AvgRating, SUM(reviews) AS TotalReviews
FROM app_ratings AS ar
JOIN app_categories_genres AS acg ON ar.app_id = acg.app_id
GROUP BY Category
ORDER BY AvgRating DESC; -- Prashul

SELECT category, COUNT(*) AS NumApps
FROM app_categories_genres
GROUP BY Category
ORDER BY NumApps DESC; -- Prashul