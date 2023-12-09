select * from cleaned_apps_f;

select * from cleaned_reviews_f;

SELECT a.*
FROM cleaned_apps_f a
JOIN (
    SELECT app
    FROM cleaned_apps_f
    GROUP BY app
    HAVING COUNT(app) > 1
) b ON a.app = b.app
order by 1;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM cleaned_apps_f
WHERE app = 'bm Wallet' AND Current_Ver != '1.0.46';

DELETE FROM cleaned_apps_f
WHERE app = 'Ac remote control' AND Current_Ver != '1.3';

DELETE FROM cleaned_apps_f
WHERE app = 'AK-47 sounds' AND Current_Ver != '2';

DELETE FROM cleaned_apps_f
WHERE app = 'Blood pressure' AND Current_Ver != '3.27.3';

DELETE FROM cleaned_apps_f
WHERE app = 'Dp For Whatsapp' AND Current_Ver != '2.7';



desc cleaned_reviews_f;


ALTER TABLE cleaned_reviews_f
ADD COLUMN app_id INT;

UPDATE cleaned_reviews_f
SET app_id = (SELECT app_id FROM apps_dim WHERE apps_dim.app = cleaned_reviews_f.app);

desc cleaned_reviews_f;