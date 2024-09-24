import pandas as pd

# 청크사이즈(행 기준)
chunk_size = 1000000

# 청크 사이즈로 tsv파일 읽기 
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


for i, chunk in enumerate(chunks):
    # 헤더가 있는 dataset은 덮어쓰기가 발생하더라도 첫번째 청크에 있는 헤더가 가장 앞으로 오게 설정
    # csv tsv와 비슷한 용량 2.5G
    if i == 0:
        chunk.to_csv("title_akas.csv", index=False, mode='w') 
    else:
        chunk.to_csv("title_akas.csv", index=False, mode='a', header=False) 

    # JSON 7.5G
    if i == 0:
        chunk.to_json("title_akas.json", orient="records", lines=True, mode='w') 
    else:
        chunk.to_json("title_akas.json", orient="records", lines=True, mode='a')

    # Parquet 500mb
    chunk.to_parquet(f"title_akas_{i}.parquet", engine="pyarrow")

