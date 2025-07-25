from flask import Flask, request, jsonify, render_template
import redis

app = Flask(__name__)
r = redis.Redis(host='35.229.24.83', port=10001)

# Redis operations
def add_to_cart(user_id, sku, qty):
    r.hincrby(f"cart:{user_id}", sku, qty)
    r.xadd(f"cartlog:{user_id}", {"action": "add", "sku": sku, "qty": qty})

def remove_from_cart(user_id, sku):
    r.hdel(f"cart:{user_id}", sku)
    r.xadd(f"cartlog:{user_id}", {"action": "remove", "sku": sku})

def show_cart(user_id):
    cart = r.hgetall(f"cart:{user_id}")
    return {k.decode(): int(v) for k, v in cart.items()}

def view_log(user_id):
    entries = r.xrange(f"cartlog:{user_id}")
    return [{k.decode(): v.decode() for k, v in entry.items()} for _, entry in entries]

# Routes
@app.route('/')
def index():
    return render_template('cartstream.html')

@app.route('/cart', methods=['GET'])
def get_cart():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(show_cart(user_id))

@app.route('/cart', methods=['POST'])
def post_cart():
    user_id = request.form.get('user_id')
    sku = request.form.get('sku')
    qty = request.form.get('qty', 1)
    if not user_id or not sku:
        return jsonify({"error": "user_id and sku required"}), 400
    try:
        qty = int(qty)
    except:
        qty = 1
    add_to_cart(user_id, sku, qty)
    return jsonify({"message": f"Added {qty} of {sku} to cart {user_id}."})

@app.route('/cart/remove', methods=['POST'])
def remove_item():
    user_id = request.form.get('user_id')
    sku = request.form.get('sku')
    if not user_id or not sku:
        return jsonify({"error": "user_id and sku required"}), 400
    remove_from_cart(user_id, sku)
    return jsonify({"message": f"Removed {sku} from cart {user_id}."})

@app.route('/cart/log', methods=['GET'])
def get_log():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    return jsonify(view_log(user_id))

if __name__ == '__main__':
    app.run(debug=True)
