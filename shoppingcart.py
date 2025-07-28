from flask import Flask, request, render_template, redirect, url_for
import redis
import os
from flask import jsonify
import openai
import dotenv
from dotenv import load_dotenv
from openai import OpenAI
import anthropic  # New

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")

# client = OpenAI(api_key=api_key)

client = anthropic.Anthropic(api_key=claude_api_key)

try:
    models = client.models.list()
    for model in models:
        print(model.id)
except Exception as e:
    print(f"Error fetching models: {e}")
app = Flask(__name__)

# r = redis.Redis(host='35.229.24.83', port=10001)
# r = redis.Redis(host='localhost', port=6379)


# r= redis.Redis(
#     host=os.getenv("REDIS_HOST","arpancache.redis.cache.windows.net"),
#     port=int(os.getenv("REDIS_PORT", 6380)),
#     password=os.getenv("REDIS_PASSWORD", "ybKbpAU9lg090duwSMEwQavaVTPfDfP2kAzCaFG5vFs="),
#     ssl=True  # if connecting to Azure Cache for Redis
# )
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True
)

# r=redis.from_url("rediss://:YMkcg5fUYrJhqb7vuB6tQseogrKgEvS22AzCaHCEfbI=@redisarpancache.redis.cache.windows.net:6380")

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
    summary = ""
    if cart:
        cart_lines = [f"{v} x {k}" for k, v in cart.items()]
        cart_text = "\n".join(cart_lines)

        prompt = f"""
        You are an e-commerce assistant. Given the following shopping cart items, do two things:

        1. Write a friendly one-sentence summary of what the user has in their cart.
        2. Suggest 2-3 related products the user might want to add to their cart.

        Shopping cart:
        {cart_text}

        Respond in this format:

         <summary here>

        Recommendations:
        - <item 1>
        - <item 2>
        - <item 3>
        """

        try:
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                temperature=0.7,
                system="You are a helpful e-commerce assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            summary = response.content[0].text
        except Exception as e:
            summary = f"(Could not generate summary: {str(e)})"
    else:
        summary = "Your cart is currently empty."
    return render_template('cart.html', cart=cart, user_id=user_id, message=message, summary=summary)

    # return render_template('cart.html', cart=cart, user_id=user_id, message=message)

@app.route('/cart/<user_id>/remove', methods=['POST'])
def remove_item(user_id):
    sku = request.form.get('sku_to_remove')
    quantity = int(request.form.get('quantity_to_remove', 1))

    if sku:
        current_qty_raw = r.hget(f'cart:{user_id}', sku)

        if current_qty_raw is not None:
            current_qty = int(current_qty_raw.decode())

            new_qty = current_qty - quantity
            if new_qty > 0:
                r.hset(f'cart:{user_id}', sku, new_qty)
            else:
                r.hdel(f'cart:{user_id}', sku)

    return redirect(url_for('view_cart', user_id=user_id))



if __name__ == '__main__':
    app.run(debug=True)
