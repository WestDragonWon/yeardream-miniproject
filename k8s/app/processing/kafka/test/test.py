from pymongo import MongoClient
import redis

def fetch_data_from_mongo():
    MONGO_URI = "mongodb://mongodb:27017"
    MONGO_DB = "mongo"
    MONGO_COLLECTION = "test"

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    data = list(collection.find())
    return data

def save_data_to_redis(data):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    for item in data:
        redis_client.set(str(item['_id']), str(item))

if __name__ == "__main__":
    # MongoDB에서 데이터 가져오기
    mongo_data = fetch_data_from_mongo()
    
    # Redis에 데이터 저장
    save_data_to_redis(mongo_data)

    print("Data has been transferred from MongoDB to Redis.")
