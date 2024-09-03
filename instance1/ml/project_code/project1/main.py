from fastapi import FastAPI, UploadFile, File
from io import BytesIO
from PIL import Image
from predict import predict
import uvicorn

app = FastAPI() # 백엔드 서버가 완성

# 라우터 (경로)
@app.get('/') # 127.0.0.1:8000/
def root():
    return {"Hello":"FastAPI!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

@app.get('/items/{item_id}')
def show_item(item_id):
    return {"Hello":item_id}

@app.post('/api/v1/predict')
async def image_predict_api(file: UploadFile = File(...)): # redoc => 파일 업로드 가능
    raw_data = await file.read()
    image_bytes_io = BytesIO(raw_data)
    print(image_bytes_io)
    image = Image.open(image_bytes_io)
    pred = predict(image)

    return pred
