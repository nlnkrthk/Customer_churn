import pandas as pd
from incremental import engine, upsert_customers


# Read cleaned data
df = pd.read_sql(
    "SELECT * FROM cleaned_customers",
    engine
)

# Pick an existing customer
customer_id = df.iloc[0]["customer_id"]

# Change the tenure
old_tenure = df.iloc[0]["tenure"]
new_tenure = old_tenure + 10

df.loc[
    df["customer_id"] == customer_id,
    "tenure"
] = new_tenure

print("Customer ID:", customer_id)
print("Old tenure:", old_tenure)
print("New tenure:", new_tenure)

# Run incremental load
inserted, updated, unchanged = upsert_customers(
    engine,
    df
)

print("========================================")
print("TEST CASE 2 - UPDATED CUSTOMER")
print("========================================")
print(f"Inserted  : {inserted}")
print(f"Updated   : {updated}")
print(f"Unchanged : {unchanged}")
print("========================================")