import hashlib
import pandas as pd

# Columns that should be deleted completely
DIRECT_PII_COLUMNS = ["host_name"]

# managing host_id
def pseudonymize_value(value, salt='qbc12'):
    salty_id = (value + salt).encode()
    return hashlib.sha256(salty_id).hexdigest() #sha256 as requested

# all pii managements together
def handle_pii(df):
    df = df.copy()   # working on copy is always better
    
    # dropping host_name
    df = df.drop(columns = DIRECT_PII_COLUMNS)

    # pseudonymization of  host_id
    l=[]
    for id in df["host_id"]:
        key = pseudonymize_value(str(id)) # turning into str just in case
        l.append(key)
    df["host_key"] = l
    
    df = df.drop(columns=["host_id"])

    return df