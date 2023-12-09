create table apps_dim(
    app_id INTEGER NOT NULL AUTO_INCREMENT,
    app VARCHAR(700) NOT NULL,
    size DOUBLE NOT NULL,
    installs INTEGER NOT NULL,
    last_updated VARCHAR(20) NOT NULL,
    current_ver VARCHAR(500) NOT NULL,
    android_ver VARCHAR(250) NOT NULL,
    PRIMARY KEY(app_id)
);



CREATE TABLE app_categories_genres (
    category_id INT NOT NULL AUTO_INCREMENT,
    app_id INT NOT NULL,
    category VARCHAR(250) NOT NULL,
    app_type VARCHAR(250) NOT NULL,
    content_rating VARCHAR(250) NOT NULL,
    genres VARCHAR(700) NOT NULL,
    PRIMARY KEY (category_id),
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id) ON DELETE CASCADE
);

CREATE TABLE app_ratings (
    rating_id INT NOT NULL AUTO_INCREMENT,
    app_id INT NOT NULL,
    rating DOUBLE NOT NULL CHECK (rating BETWEEN 1.0 AND 5.0),
    reviews INT NOT NULL,
    PRIMARY KEY (rating_id),
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id) ON DELETE CASCADE
);


CREATE TABLE app_price (
    price_id INT NOT NULL AUTO_INCREMENT,
    app_id INT NOT NULL,
    price DOUBLE NOT NULL,
    PRIMARY KEY (price_id),
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id) ON DELETE CASCADE
);


create table app_reviews (
	review_id INT NOT NULL AUTO_INCREMENT,
    app_id INT,
    review TEXT,
    sentiment TEXT,
    FOREIGN KEY (app_id) REFERENCES apps_dim(app_id),
    PRIMARY KEY (review_id)
);