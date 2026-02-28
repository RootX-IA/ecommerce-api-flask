from flask import Flask, request, jsonify
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required #vai obrigar o usuário estar logado nas rotas que selecionar
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "minha_chave_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgre@localhost:5433/rocketseat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    model = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        response = {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "price": self.price,
            "description": self.description
        }
        return response

@login_manager.user_loader #Esse decorator registra essa função como a função oficial para carregar o usuário logado.
def load_user(user_id): #Essa função recebe o user_id que o Flask guardou quando o login foi feito.
    return User.query.get(int(user_id)) #Vai na tabela User e procura o usuário pelo ID.
#Essa função ensina ao Flask-Login como buscar no banco o usuário que está logado.

@app.route('/login', methods=["POST"])
def login():

    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if user and data["password"] == user.password:
        login_user(user) #“Esse usuário aqui foi autenticado com sucesso. Guarde essa informação para as próximas requisições.”
                         #O Flask passa a entender que esse usuário está logado, e por isso ele consegue acessar rotas com @login_required.
        return jsonify({"message": "user loged successfully"})
    return jsonify({"message": "Unauthorized. Invalid credentials"})
"""Pensa assim:

- Usuário digitou username e password
- O sistema foi no banco e encontrou esse usuário
- A senha bateu
- Então você chama login_user(user)

É como se você dissesse: Pode liberar a entrada, esse cara está autenticado."""
@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successfully"})

@app.route('/api/products/add', methods=['POST'])
@login_required
def add_products():

    data = request.get_json()
    if 'name' in data and 'price' in data and 'model' in data:
        
        product = Product(
            name=data["name"],
            model=data["model"], 
            price=data["price"],
            description=data.get("description", "") #2 ways to do it: x=data["x"] or x=data.get["x"]
            )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product add successfully."}), 201
    
    return jsonify({"message": "Invalid product data"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
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

@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):

    product = Product.query.get(product_id) #Vai no banco de dados e procura na tabela Product o registro cujo ID é product_id
    if product is None: #if product is None / if not product = verifica o valor do campo product depois que o JSON já foi lido.
        return jsonify({'message': 'Product not found'}), 404 #isso significa: “o banco não achou nenhum produto com esse ID que eu mandei”
    # product.name = data.get('name')
    # product.model = data['model']
    # product.price = data['price']
    # product.description = data['description']
    data = request.get_json(silent=True) #silent=True = verifica se o corpo da requisição é um JSON válido (pra não dar erro).
    if data is None:
        return jsonify({"error": "Invalid or missing body"}), 400
    if 'name' in data:
        product.name = data['name']
    if 'model' in data:
        product.model = data['model']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Product update successfully'})

if __name__ == "__main__":
    app.run(debug=True)