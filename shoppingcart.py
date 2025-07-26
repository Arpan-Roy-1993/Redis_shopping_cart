from flask import Flask, request, render_template, redirect, url_for
import redis
import os
app = Flask(__name__)

# r = redis.Redis(host='35.229.24.83', port=10001)
r = redis.Redis(host='localhost', port=6379)


# r= redis.Redis(
#     host=os.getenv("REDIS_HOST","redisarpancache.redis.cache.windows.net"),
#     port=int(os.getenv("REDIS_PORT", 6380)),
#     password=os.getenv("REDIS_PASSWORD", "YMkcg5fUYrJhqb7vuB6tQseogrKgEvS22AzCaHCEfbI="),
#     ssl=True  # if connecting to Azure Cache for Redis
# )

# r=redis.from_url("rediss://:YMkcg5fUYrJhqb7vuB6tQseogrKgEvS22AzCaHCEfbI=@redisarpancache.redis.cache.windows.net:6380")

print("redis connection:", r)
@app.route('/')
def home():
    return redirect(url_for('view_cart', user_id='user123'))

@app.route('/cart/<user_id>', methods=['GET', 'POST'])
def view_cart(user_id):
    message = ""

    # Handle form submission to add item
    if request.method == 'POST':
        sku = request.form.get('sku')
        quantity = int(request.form.get('quantity', 1))
        if sku:
            r.hincrby(f'cart:{user_id}', sku, quantity)
            message = f"Added {quantity} of {sku} to cart."

    cart_raw = r.hgetall(f'cart:{user_id}')
    cart = {k.decode(): int(v) for k, v in cart_raw.items()}  # Decode keys/values
    return render_template('cart.html', cart=cart, user_id=user_id, message=message)

@app.route('/cart/<user_id>/remove', methods=['POST'])
def remove_item(user_id):
    sku = request.form.get('sku_to_remove')
    quantity = int(request.form.get('quantity_to_remove', 1))

    if sku:
        current_qty = r.hget(f'cart:{user_id}', sku)
        if current_qty is not None:
            new_qty = int(current_qty) - quantity
            if new_qty > 0:
                r.hset(f'cart:{user_id}', sku, new_qty)
            else:
                r.hdel(f'cart:{user_id}', sku)
    return redirect(url_for('view_cart', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)