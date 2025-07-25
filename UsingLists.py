import redis
import random

# Redis CE (Source)
src = redis.Redis(host='35.229.24.83', port=10001)

# Redis Enterprise (Replica)
replica = redis.Redis(host='34.75.77.153', port=12000)
# 1. Insert 1–100 using list (efficient stack-like reverse access)
for i in range(1, 101):
    src.lpush("numbers", i)

# 2. Retrieve in reverse from RE
print(replica.lrange("numbers", 0, -1))

# 3. Insert 100 random numbers
for _ in range(100):
    src.lpush("random_numbers", random.randint(1, 1000))

# 4. Retrieve in reverse
print(replica.lrange("random_numbers", 0, -1))