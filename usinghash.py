import redis
import random

# Redis CE (Source)
src = redis.Redis(host='35.229.24.83', port=10001)

# Redis Enterprise (Replica)
replica = redis.Redis(host='34.75.77.153', port=12000)

# 1. Insert 1–100 using Redis Hash
for i in range(1, 101):
    src.hset("numbers_hash", i, i)

# 2. Retrieve in reverse (highest key first)
numbers_raw = replica.hgetall("numbers_hash")
numbers_sorted = [int(numbers_raw[k]) for k in sorted(numbers_raw.keys(), key=lambda x: -int(x))]
print(numbers_sorted)

# 3. Insert 100 random numbers into a Redis Hash
for i in range(100):
    src.hset("random_hash", i, random.randint(1, 1000))

# 4. Retrieve in reverse (highest key first)
random_raw = replica.hgetall("random_hash")
random_sorted = [int(random_raw[k]) for k in sorted(random_raw.keys(), key=lambda x: -int(x))]
print(random_sorted)