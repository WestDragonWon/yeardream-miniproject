# 여러가지 포맷 데이터 만들기

## 메모리 이슈
- 16GB 인스턴스이지만 2.5G csv를 변환한 json 파일이 7.5G였기 때문에 인스턴스가 메모리부족으로 뻗어버림
- chunk로 잘라서 수행하면 메모리 부족을 해결할 수 있음
## combine-parquet.py
- parquet은 append로 추가 되지 않아 따로 파일을 만든 뒤 pyarrow의 concat_tables 함수로 하나의 parquet파일로 만듬