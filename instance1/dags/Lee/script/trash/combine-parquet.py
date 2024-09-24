import pyarrow.parquet as pq
import pyarrow as pa
import glob

# 모든 parquet파일들 이름list
parquet_files = glob.glob('title_akas_*.parquet')

# 데이터들을 담을 list
tables = []

# 파일을 읽어서 tables에 담음
for parquet_file in parquet_files:
    table = pq.read_table(parquet_file)
    tables.append(table)

# 데이터 통합
combined_table = pa.concat_tables(tables)

# 통합데이터 쓰기
pq.write_table(combined_table, 'title_akas_combined.parquet')

