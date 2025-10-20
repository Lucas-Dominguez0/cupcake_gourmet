from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- Configuração ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'chave_super_secreta'
db = SQLAlchemy(app)

# --- MODELOS ---
class Produto(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    imagem = db.Column(db.String(200))

class Pedido(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pendente")
    cliente_nome = db.Column(db.String(100), nullable=True)
    email_cliente = db.Column(db.String(120), nullable=True)
    data_pedido = db.Column(db.DateTime, default=db.func.current_timestamp())

class Usuario(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    senha_hash = db.Column(db.String(200), nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

# --- ROTAS ---

@app.route('/')
def index():
    produtos = Produto.query.all()
    return render_template('index.html', produtos=produtos)

# Carrinho
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    produtos = []
    total = 0

    for produto_id, qtd in cart.items():
        produto = Produto.query.get(int(produto_id))
        if produto:
            subtotal = produto.preco * qtd
            total += subtotal
            produtos.append({
                'id': produto.id,
                'nome': produto.nome,
                'imagem': produto.imagem,
                'preco': produto.preco,
                'qtd': qtd,
                'subtotal': subtotal
            })

    return render_template('cart.html', produtos=produtos, total=total)

# Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        senha = request.form['senha']

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado. Faça login.', 'warning')
            return redirect(url_for('login'))

        novo_usuario = Usuario(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            telefone=telefone,
            endereco=endereco
        )
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            return redirect(url_for('cart'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

# Adicionar ao carrinho
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    produto_id = request.form.get('produto_id')
    if not produto_id:
        flash('Produto inválido', 'danger')
        return redirect(url_for('index'))

    cart = session.get('cart', {})
    cart[produto_id] = cart.get(produto_id, 0) + 1
    session['cart'] = cart
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('index'))

# Remover do carrinho
@app.route('/remove_from_cart/<int:produto_id>')
def remove_from_cart(produto_id):
    cart = session.get('cart', {})
    cart.pop(str(produto_id), None)
    session['cart'] = cart
    flash('Produto removido do carrinho.', 'info')
    return redirect(url_for('cart'))

# Atualizar quantidade do carrinho
@app.route('/update_cart', methods=['POST'])
def update_cart():
    produto_id = request.form.get('produto_id')
    action = request.form.get('action')
    cart = session.get('cart', {})

    if produto_id in cart:
        if action == 'add':
            cart[produto_id] += 1
        elif action == 'remove':
            cart[produto_id] -= 1
            if cart[produto_id] <= 0:
                del cart[produto_id]

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/perfil')
def perfil():
    # Garante que o usuário esteja logado
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar o perfil.', 'warning')
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('perfil.html', usuario=usuario)

# Checkout
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para finalizar a compra.', 'warning')
        return redirect(url_for('login'))

    cart = session.get('cart', {})
    if not cart:
        flash('Seu carrinho está vazio!', 'warning')
        return redirect(url_for('cart'))

    produtos = Produto.query.filter(Produto.id.in_(cart.keys())).all()
    total = sum(p.preco * cart[str(p.id)] for p in produtos)

    usuario = Usuario.query.get(session['usuario_id'])
    forma_pagamento = request.form.get('forma_pagamento', 'Pix')

    pedido = Pedido(
        total=total,
        status=f"Pago via {forma_pagamento}",
        cliente_nome=usuario.nome,
        email_cliente=usuario.email
    )
    db.session.add(pedido)
    db.session.commit()

    session.pop('cart', None)
    flash('Compra finalizada com sucesso! Obrigado por comprar conosco 🧁', 'success')
    return redirect(url_for('index'))
@app.route('/reset_session')
def reset_session():
    session.clear()
    flash('Sessão limpa com sucesso!', 'info')
    return redirect(url_for('index'))
# Rodar app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
