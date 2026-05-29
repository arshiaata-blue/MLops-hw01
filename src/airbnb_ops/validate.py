def validate_summary(summary) -> None:
    # output is not empty
    if summary.empty:
        raise ValueError("Summary is empty!!!!!")
    
    # required output columns exist
    required_cols = ['neighbourhood', 'num_listings', 'avg_price', 'median_price',
        'avg_minimum_nights', 'availability_365_avg', 'total_reviews',
        'reviews_per_listing', 'tourism_segment', 'priority_level']
    for col in required_cols:
        if col not in summary.columns:
            raise ValueError(f"Missing column in summary{col}")
        
    # no PII columns exist
    pii_cols = ['host_name', 'host_id']
    for col in pii_cols:
        if col in summary.columns:
            raise ValueError(f"PII is in summary{col}")
        
    # neighbourhood is not null
    if summary["neighbourhood"].isnull().any():
        raise ValueError("theres Null in neighbourhood")
    
    # num_listings > 0
    if (summary["num_listings"] <= 0).any():
        raise ValueError("num_listings must be >= 0")
    
    # avg_price >= 0
    if (summary["avg_price"] < 0).any():
        raise ValueError("avg_price must be >= 0")
    
    # availability_365_avg between 0 and 365
    if (summary['availability_365_avg'] < 0).any() or (summary['availability_365_avg'] > 365).any():
        raise ValueError("availability out of range")
    
    print("All validations passed!!!")