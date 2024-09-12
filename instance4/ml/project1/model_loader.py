import tensorflow as tf

# 모델 불러오기
def load_model():
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
    print('Model Successfuly Loaded...')
    return model

model = load_model()