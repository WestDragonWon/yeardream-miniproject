## kafkaCsvProducerAll.py
- 23mb 정도 사이즈의 csv 파일을 gzip으로 압축한 뒤 한번에 kafka message로 보내려고 시도
- kafka conf 설정의 message.max.bytes가 4mb인데 gzip으로 압축한 데이터보다 작아 에러 발생
## kafkaCsvProducerBychunk.py
- kafka의 message 기본사이즈가 1mb, 데이터를 잘라서 넣어주면 빠를 것이다
- 데이터를 많이 자르면 operator가 많이 생성되고, pandas도 많이 실행되므로 더 느려짐
- kafka message 크기 1MB or 10MB (test필요)
## kafkaJsonProducer.py
- pandas로 읽은 데이터를 value_serializer=lambda v: json.dumps(v).encode('utf-8') 옵션으로 json형태로 전환

