from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()

from api.books import BOOKS
from api.books import bp as books_bp
from api.chat import bp as chat_bp
from api.orders import bp as orders_bp
from api.orders import store as orders_store
from api.support import bp as support_bp

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


app.register_blueprint(books_bp)
app.register_blueprint(support_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(chat_bp)

orders_store.seed_demo_orders(BOOKS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
