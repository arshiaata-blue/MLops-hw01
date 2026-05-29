import pandas as pd

# the main def that does all the required tasks
def build_neighbourhood_summary(listings, segments):

    #Validating columns
    required_cols = ["neighbourhood", "price", "minimum_nights", "availability_365", "number_of_reviews"]
    for col in required_cols:
        if col not in listings.columns:
            raise ValueError(f"Missing Column is: {col}")
        
    # measuring all required outouts
    total_actions = listings.groupby("neighbourhood").agg(
        num_listings = ("neighbourhood", "count"),
        avg_price = ("price", "mean"),
        median_price = ("price", "median"),
        avg_minimum_nights = ("minimum_nights", "mean"),
        availability_365_avg = ("availability_365", "mean"),
        total_reviews = ("number_of_reviews", "sum"),
        reviews_per_listing = ("number_of_reviews", "mean")
    ).reset_index()

    # merging with segments
    merged = total_actions.merge(segments, on="neighbourhood", how="left")

    # filling missing values
    merged['tourism_segment'] = merged['tourism_segment'].fillna('unknown')
    merged['priority_level'] = merged['priority_level'].fillna('unknown')

    # output as a Dataframe
    return merged