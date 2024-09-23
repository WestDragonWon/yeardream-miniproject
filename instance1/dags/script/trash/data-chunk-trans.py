import pandas as pd

# Define the chunk size (number of rows per chunk)
chunk_size = 1000000

# Read and process the TSV file in chunks
chunks = pd.read_csv("title.akas.tsv", sep="\t", chunksize=chunk_size, dtype={
    "titleId": str,
    "ordering": int,
    "title": str,
    "region": str,
    "language": str,
    "types": str,
    "attributes": str,
    "isOriginalTitle": bool
}, na_values="\\N")

# Process each chunk
for i, chunk in enumerate(chunks):
    # Write to CSV in append mode
    if i == 0:
        chunk.to_csv("title_akas.csv", index=False, mode='w')  # First chunk, write header
    else:
        chunk.to_csv("title_akas.csv", index=False, mode='a', header=False)  # Subsequent chunks, no header

    # Write each chunk to Parquet
    chunk.to_parquet(f"title_akas_{i}.parquet", engine="pyarrow")

    # Write each chunk to JSON
    if i == 0:
        chunk.to_json("title_akas.json", orient="records", lines=True, mode='w')  # First chunk, overwrite
    else:
        chunk.to_json("title_akas.json", orient="records", lines=True, mode='a')  # Append mode

