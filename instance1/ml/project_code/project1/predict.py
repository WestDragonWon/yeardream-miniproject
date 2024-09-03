# 이미지 파일을 로드하고 결과값을 리턴
import numpy as np
from PIL.Image import Image # pip install pillow
import tensorflow as tf
from model_loader import model

def predict(image: Image):
    # 224x224: 이미지 사이즈를 정규화(크기 고정)
    image = np.asarray(image.resize((224, 224)))[..., :3] # RGB
    print(image)

    image = np.expand_dims(image, 0)
    print(image)

    image = image / 127.5 - 1.0 # Sclaer -> -1 ~ 1 사이의 숫자로 변경
    print(image)

    results = tf.keras.applications.imagenet_utils.decode_predictions(
        model.predict(image), 2
    )[0]

    print(results)

    result_list = []
    for i in results:
        result_list.append({
            "class": i[1],
            "confidence": f'{i[2]*100:0.2f}%'
        })

    return result_list