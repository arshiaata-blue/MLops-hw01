
DROP MATERIALIZED VIEW IF EXISTS "student_arshia_ataei".mv_airbnb_neighbourhood_summary;

CREATE MATERIALIZED VIEW "student_arshia_ataei".mv_airbnb_neighbourhood_summary AS
WITH calendar_30 AS (
    SELECT listing_id, available, price
    FROM core.calendar_day
    WHERE 30 >= CURRENT_DATE - date
),
review_counts AS (
    SELECT listing_id, COUNT(*) AS total_reviews
    FROM core.review
    GROUP BY listing_id
)
SELECT 
    core.listing.neighbourhood_id,
    COUNT(core.listing.listing_id) AS num_listings,
    AVG(core.listing.listing_price) AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY core.listing.listing_price) AS median_price,
    AVG(core.listing.minimum_nights) AS avg_minimum_nights,
    COALESCE(SUM(review_counts.total_reviews), 0) AS total_reviews,
    CASE 
        WHEN COUNT(core.listing.listing_id) > 0 
        THEN COALESCE(SUM(review_counts.total_reviews), 0)::float / COUNT(core.listing.listing_id)
        ELSE 0 
    END AS reviews_per_listing,
    COALESCE(AVG(CASE WHEN calendar_30.available = 't' THEN 1.0 ELSE 0.0 END), 0) AS availability_30_rate
FROM core.listing
LEFT JOIN calendar_30 ON core.listing.listing_id = calendar_30.listing_id
LEFT JOIN review_counts ON core.listing.listing_id = review_counts.listing_id
GROUP BY core.listing.neighbourhood_id
ORDER BY num_listings DESC;

CREATE INDEX idx_mv_neighbourhood ON "student_arshia_ataei".mv_airbnb_neighbourhood_summary (neighbourhood);
CREATE INDEX idx_mv_num_listings ON "student_arshia_ataei".mv_airbnb_neighbourhood_summary (num_listings DESC);
