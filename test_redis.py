import redis

print("Testing Redis connection...")

try:
    r = redis.Redis(host="localhost", port=6380, db=0)
    result = r.ping()
    print(f"Redis connected: {result}")
except Exception as e:
    print(f"Error: {e}")
