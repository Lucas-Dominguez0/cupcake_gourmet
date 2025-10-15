# create_db.py
from app import app, db
from app import Produto, Usuario

# Lista de produtos iniciais
produtos_iniciais = [
    {"nome": "Cupcake Chocolate", "preco": 8.00, "categoria": "Chocolate", "imagem": "https://i.imgur.com/1bK7R9J.jpg"},
    {"nome": "Cupcake Baunilha", "preco": 7.50, "categoria": "Baunilha", "imagem": "https://i.imgur.com/ODdMZcV.jpg"},
    {"nome": "Cupcake Morango", "preco": 9.00, "categoria": "Morango", "imagem": "https://i.imgur.com/XH6t7tS.jpg"},
    {"nome": "Cupcake Chocolate Branco", "preco": 8.50, "categoria": "Chocolate", "imagem": "https://i.imgur.com/yPp2zZP.jpg"},
    {"nome": "Cupcake Baunilha com Frutas", "preco": 9.00, "categoria": "Baunilha", "imagem": "https://i.imgur.com/0pSJu5k.jpg"},
    {"nome": "Cupcake Morango com Chocolate", "preco": 9.50, "categoria": "Morango", "imagem": "https://i.imgur.com/6dK6xQH.jpg"}
]

# Cria as tabelas e popula os produtos dentro do contexto do Flask
with app.app_context():
    # Cria todas as tabelas
    db.create_all()
    print("Banco de dados e tabelas criadas com sucesso!")

    # Popula os produtos iniciais, evitando duplicatas
    for p in produtos_iniciais:
        if not Produto.query.filter_by(nome=p["nome"]).first():
            novo_produto = Produto(**p)
            db.session.add(novo_produto)

    db.session.commit()
    print("Produtos inseridos com sucesso!")
