from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from sqlalchemy import create_engine, text

default_args = {
    'owner': 'arshia_ataei',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='qbc12_hw01_arshia_ataei_airbnb_pipeline',
    default_args=default_args,
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['qbc12', 'airbnb', 'hw01'],
):

    # Creating engine 
    def make_engine():
        user = Variable.get("QBC12_DB_USER")
        password = Variable.get("QBC12_DB_PASSWORD")
        host = Variable.get("QBC12_DB_HOST")
        port = Variable.get("QBC12_DB_PORT")
        db = Variable.get("QBC12_DB_NAME")

        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}')
        return engine

    #used as other tasks settings
    @task
    def read_config():
        return{
            "student_schema" : "student_arshia_ataei",
            "mv_name" : "mv_airbnb_neighbourhood_summary",
        }
    
    # Refreshing Materialzed View
    @task
    def refresh_summary(config):
        schema = config["student_schema"]
        mv_name = config["mv_name"] 

        engin = make_engine()

        # Creating Materialized View IF NOT created before (from HW01_B)
        with engin.begin() as conn:
            conn.execute(text(f'DROP MATERIALIZED VIEW IF EXISTS "{schema}"."{mv_name}"'))
            conn.execute(text(f'''
                CREATE MATERIALIZED VIEW "{schema}"."{mv_name}" AS
                WITH calendar_30 AS (
                    SELECT listing_id, available, price
                    FROM core.calendar_day
                    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                ),
                review_counts AS (
                    SELECT listing_id, COUNT(*) AS total_reviews
                    FROM core.review
                    GROUP BY listing_id
                )
                SELECT 
                    core.listing.neighbourhood_id AS neighbourhood,
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
                    COALESCE(AVG(CASE WHEN calendar_30.available = 't' THEN 1.0 ELSE 0.0 END), 0) AS availability_30_rate,
                    COALESCE(AVG(CASE WHEN calendar_30.available = 't' THEN 1.0 ELSE 0.0 END), 0) * 365 AS availability_365_rate
                FROM core.listing
                LEFT JOIN calendar_30 ON core.listing.listing_id = calendar_30.listing_id
                LEFT JOIN review_counts ON core.listing.listing_id = review_counts.listing_id
                GROUP BY core.listing.neighbourhood_id
                ORDER BY num_listings DESC
            '''))

            conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_mv_neighbourhood ON "{schema}"."{mv_name}" (neighbourhood)'))
            conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_mv_num_listings ON "{schema}"."{mv_name}" (num_listings DESC)'))
        
        # counting rwos to return a summary
        with engin.begin() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{mv_name}"'))
            row_count = result.scalar()

        return{
            "materialized_view": f"{schema}.{mv_name}",
            "row_count" : row_count,
            "refreshed_at" : str(datetime.now())
        }
    @task
    def validate_summary(config):
        engine = make_engine()
        schema = config["student_schema"]
        mv_name = config["mv_name"]
        
        with engine.connect() as conn:
            row_count = conn.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{mv_name}"')).scalar()
            null_neighbourhoods = conn.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{mv_name}" WHERE neighbourhood IS NULL')).scalar()
            bad_prices = conn.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{mv_name}" WHERE avg_price < 0')).scalar()
            bad_availability = conn.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{mv_name}" WHERE availability_30_rate < 0 OR availability_30_rate > 1')).scalar()

        validation = {}

        validation["row_counts_pos"] = row_count > 0
        validation["no_null_neighbourhood"] = null_neighbourhoods == 0
        validation["no_bad_prices"] = bad_prices == 0
        validation["no_bad_availibility"] = bad_availability == 0

        validation["passed"] = all([
        validation["row_counts_pos"],
        validation["no_null_neighbourhood"],
        validation["no_bad_prices"],
        validation["no_bad_availibility"],
        ])
        return validation

    @task.branch
    def choose_path(validation_result):
        if validation_result['passed']:
            return 'success_report'
        else:
            return 'failure_report'
        
    @task
    def success_report():
        print("Pipeline WORKS!")
        return {"status": "success"}

    @task
    def failure_report():
        print("Pipeline failed!")
        raise ValueError("Validation failed")

config = read_config()
refreshed = refresh_summary(config)
validated = validate_summary(config)
branch = choose_path(validated)

refreshed >> validated >> branch
branch >> success_report()
branch >> failure_report()