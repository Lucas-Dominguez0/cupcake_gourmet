from app import db, Produto, app

with app.app_context():
    # Cria as tabelas (caso ainda não existam)
    db.create_all()

    # Limpa produtos antigos
    Produto.query.delete()

    # Cria os produtos com imagens corretas
    produtos = [
        Produto(nome='Cupcake Chocolate', preco=10.0, categoria='Chocolate', imagem='cupcake3.jpg'),
        Produto(nome='Cupcake Baunilha', preco=9.0, categoria='Baunilha', imagem='cupcake1.jpg'),
        Produto(nome='Cupcake Morango', preco=11.0, categoria='Morango', imagem='cupcake2.jpg'),
    ]

    # Adiciona ao banco
    db.session.add_all(produtos)
    db.session.commit()

    print("Produtos inseridos com sucesso!")
