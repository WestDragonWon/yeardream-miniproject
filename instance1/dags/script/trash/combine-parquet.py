import pyarrow.parquet as pq
import pyarrow as pa
import glob

# List all the parquet files
parquet_files = glob.glob('title_akas_*.parquet')

# Create an empty list to hold the table data
tables = []

# Iterate over the parquet files and read each one into a PyArrow table
for parquet_file in parquet_files:
    table = pq.read_table(parquet_file)
    tables.append(table)

# Concatenate all the PyArrow tables into one
combined_table = pa.concat_tables(tables)

# Write the combined table to a new parquet file
pq.write_table(combined_table, 'title_akas_combined.parquet')

