## 목차
1. [BashOperator vs PythonOperator](#bashoperator-vs-pythonoperator)
2. [BashOperator](#bashoperator)
3. [PythonOperator](#pythonoperator)
4. [producerDag.py](#producerdagpy)

## BashOperator vs PythonOperator
![Alt text](image.png)

## BashOperator
- 장점
1. 테스트를 로컬환경에서 바로 해 볼 수 있음
2. 테스트를 위한 환경설정이 간편함
- 단점
1. 경로설정이 복잡함
2. 불필요할 수 있는 환경설정을 전부 해주어야 함
3. 에어플로우를 이용한 통합성을 떨어뜨림
4. 파드간 독립성을 떨어뜨림
## PythonOperator
- 장점
1. 환경설정 통합
2. 파드간 독립성 확보
3. 에어플로우를 이용한 통합이 용이
- 단점
1. 테스트 환경설정을 위해 이미지를 변경하고 파드를 내렸다 올려야함
2. 에어플로우와 파이썬 파일간의 의존성 충돌


## producerDag.py
- 파이썬 테스트를 에어플로우 없이 할 수 있게 bashoperator 사용
- airflow Variable 옵션을 통해 파라미터변경 시도