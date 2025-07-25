import redis
import random
import time

# Redis Connections
src = redis.Redis(host='35.229.24.83', port=10001)
replica = redis.Redis(host='34.75.77.153', port=12000)

# Keys to test
keys = [
    "numbers_list", "random_list",
    "numbers_zset", "random_zset",
    "numbers_stream", "random_stream",
    "numbers_hash", "random_hash"
]

# Cleanup
for key in keys:
    src.delete(key)
    replica.delete(key)

### 1. LIST
start = time.perf_counter()
for i in range(1, 101):
    src.lpush("numbers_list", i)
for _ in range(100):
    src.lpush("random_list", random.randint(1, 1000))
insert_list_time = time.perf_counter() - start

start = time.perf_counter()
list_seq = [int(i) for i in replica.lrange("numbers_list", 0, -1)]
list_rand = [int(i) for i in replica.lrange("random_list", 0, -1)]
read_list_time = time.perf_counter() - start

### 2. SORTED SET
start = time.perf_counter()
for i in range(1, 101):
    src.zadd("numbers_zset", {i: i})
for idx in range(100):
    value = random.randint(1, 1000)
    src.zadd("random_zset", {value: idx})
insert_zset_time = time.perf_counter() - start

start = time.perf_counter()
zset_seq = [int(i) for i in replica.zrange("numbers_zset", 0, -1)]
zset_rand = [int(i) for i in replica.zrange("random_zset", 0, -1)]
read_zset_time = time.perf_counter() - start

### 3. STREAM
start = time.perf_counter()
for i in range(1, 101):
    src.xadd("numbers_stream", {"value": i})
for _ in range(100):
    src.xadd("random_stream", {"value": random.randint(1, 1000)})
insert_stream_time = time.perf_counter() - start

start = time.perf_counter()
stream_seq = [int(e[1][b'value']) for e in replica.xrange("numbers_stream", "-", "+")]
stream_rand = [int(e[1][b'value']) for e in replica.xrange("random_stream", "-", "+")]
read_stream_time = time.perf_counter() - start

### 4. HASH
start = time.perf_counter()
for i in range(1, 101):
    src.hset("numbers_hash", i, i)
for i in range(100):
    src.hset("random_hash", i, random.randint(1, 1000))
insert_hash_time = time.perf_counter() - start

start = time.perf_counter()
hash_seq_raw = replica.hgetall("numbers_hash")
hash_rand_raw = replica.hgetall("random_hash")
hash_seq = [int(hash_seq_raw[k]) for k in sorted(hash_seq_raw.keys(), key=lambda x: int(x))]
hash_rand = [int(hash_rand_raw[k]) for k in sorted(hash_rand_raw.keys(), key=lambda x: int(x))]
read_hash_time = time.perf_counter() - start

print("\n=== LIST ===")
print("Sequential:", list_seq)
print("Random    :", list_rand)

print("\n=== SORTED SET ===")
print("Sequential:", zset_seq)
print("Random    :", zset_rand)

print("\n=== STREAM ===")
print("Sequential:", stream_seq)
print("Random    :", stream_rand)

print("\n=== HASH ===")
print("Sequential:", hash_seq)
print("Random    :", hash_rand)


# Timing Summary
print("\n=== EXECUTION TIME (in seconds) ===")
print(f"List        - Insert: {insert_list_time:.4f}s | Read: {read_list_time:.4f}s")
print(f"Sorted Set  - Insert: {insert_zset_time:.4f}s | Read: {read_zset_time:.4f}s")
print(f"Stream      - Insert: {insert_stream_time:.4f}s | Read: {read_stream_time:.4f}s")
print(f"Hash        - Insert: {insert_hash_time:.4f}s | Read: {read_hash_time:.4f}s")
