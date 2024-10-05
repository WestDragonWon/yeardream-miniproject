import requests

url = 'http://localhost:5001/predict'
data = {
    "Sepal.Length": [5.1, 4.9],
    "Sepal.Width": [3.5, 3.0],
    "Petal.Length": [1.4, 1.4],
    "Petal.Width": [0.2, 0.2]
}

response = requests.post(url, json=data)
print(response.json())

