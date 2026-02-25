from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgre@localhost:5433/rocketseat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        response = {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description
        }
        return response

@app.route('/api/products/add', methods=['POST'])
def add_products():

    data = request.get_json()
    if 'name' in data and 'price' in data:
        
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product add successfully."}), 201
    
    return jsonify({"message": "Invalid product data"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):

    product = Product.query.get_or_404(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully!"}), 200
    
@app.route('/api/products/search', methods=["GET"])
def search_products():
    list_products = Product.query.all()

    products = [p.to_dict() for p in list_products]

    return jsonify(products), 200


if __name__ == "__main__":
    app.run(debug=True)