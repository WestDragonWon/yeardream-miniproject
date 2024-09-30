from flask import Flask, render_template, request, redirect, url_for, flash
from kafka import KafkaProducer
import json

app = Flask(__name__)
app.secret_key = 'secret_key' #세션 데이터를 보호하기 위함, 클라이언트가 세션데이터를 변경할 수 없게 (보통 난수값으로 설정한다고 한다)

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # 데이터를 JSON으로 직렬화
    )

# 회원가입 페이지 라우트
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 폼 데이터 받기
        name = request.form['name']
        user_id = request.form['user_id']
        password = request.form['password']

        # 비밀번호 유효성 검사 (4자리 숫자만 허용)
        if len(password) != 4 or not password.isdigit():
            flash("비밀번호는 4자리 숫자로 입력해야 합니다.")
            return redirect(url_for('signup'))

        # 사용자 데이터를 Kafka로 전송
        user_data = {
            'name': name,
            'user_id': user_id,
            'password': password
        }

        producer.send('user-topic', value=user_data)
        flash("회원가입이 완료되었습니다. 데이터를 처리 중입니다.")
        return redirect(url_for('signup'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
