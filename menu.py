import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(diretorio_atual, "atlas-credentials.env")

# Carrega o arquivo
load_dotenv(caminho_env)

uri = os.getenv("MONGODB_URI")
print("Conectando ao MongoDB Atlas...")

client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

# Busca o usuário pelo CPF (único). 
def buscar_usuario_cpf():
    cpf = input("CPF do usuário: ")
    u = db.usuario.find_one({"cpf": cpf})
    if not u:
        print("Usuário não encontrado.")
    return u

# Mostra uma lista numerada e devolve o documento escolhido
def escolher(docs, mostrar):
    docs = list(docs)
    if not docs:
        print("Nenhum registro encontrado.")
        return None
    for i, d in enumerate(docs, 1):
        print(f"{i}-{mostrar(d)}")
    op = input("Escolha o número: ")
    if op.isdigit() and 1 <= int(op) <= len(docs):
        return docs[int(op) - 1]
    print("Opção inválida.")
    return None

def escolher_produto():
    print("Escolha o produto:")
    return escolher(db.produto.find().sort("nome"), lambda p: f'{p["nome"]} - R$ {p.get("preco", "")}')

# Lista uma coleção trazendo os documentos ligados pelo _id
def com_nomes(colecao, filtro, joins):
    pipeline = [{"$match": filtro}]
    for campo, origem in joins:
        pipeline.append({"$lookup": {"from": origem, "localField": campo, "foreignField": "_id", "as": origem}})
    return list(db[colecao].aggregate(pipeline))

# Pega um campo do documento ligado; avisa se ele foi apagado.
def nome_ligado(d, origem, campo="nome"):
    return d[origem][0].get(campo) if d.get(origem) else "(removido)"

#===========================================================
# CRUD (Usuário)
#===========================================================

def create_usuario():
    global db
    mycol = db.usuario
    print("\nInserindo um novo usuário")
    nome = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    cpf = input("CPF: ")
    if mycol.find_one({"cpf": cpf}):
        print("Já existe um usuário com esse CPF.")
        return
    key = 1
    end = []
    while (key != 'N'):
        rua = input("Rua: ")
        num = input("Num: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        estado = input("Estado: ")
        cep = input("CEP: ")
        endereco = {
            "rua": rua, "num": num, "bairro": bairro,
            "cidade": cidade, "estado": estado, "cep": cep
        }
        end.append(endereco)
        key = input("Deseja cadastrar um novo endereço (S/N)? ").upper()
    
    # Inicializa o array "favoritos" vazio por padrão 
    mydoc = { "nome": nome, "sobrenome": sobrenome, "cpf": cpf, "end": end, "favoritos": [] }
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)

def read_usuario(nome):
    global db
    mycol = db.usuario
    print("Usuários existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"], x["cpf"])
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

def update_usuario(nome):
    global db
    mycol = db.usuario
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if not mydoc:
        print("Usuário não encontrado.")
        return
    print("Dados do usuário: ", mydoc)
    novo_nome = input("Mudar Nome: ")
    if len(novo_nome):
        mydoc["nome"] = novo_nome

    novo_sobrenome = input("Mudar Sobrenome: ")
    if len(novo_sobrenome):
        mydoc["sobrenome"] = novo_sobrenome

    novo_cpf = input("Mudar CPF: ")
    if len(novo_cpf):
        if mycol.find_one({"cpf": novo_cpf, "_id": {"$ne": mydoc["_id"]}}):
            print("Já existe outro usuário com esse CPF. CPF não alterado.")
        else:
            mydoc["cpf"] = novo_cpf

    newvalues = { "$set": mydoc }
    mycol.update_one(myquery, newvalues)
    print("Usuário atualizado!")

def delete_usuario(nome, sobrenome):
    global db
    mycol = db.usuario
    myquery = {"nome": nome, "sobrenome": sobrenome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o usuário. Quantidade removida: ", mydoc.deleted_count)

#===========================================================
# CRUD (Produto)
#===========================================================

def create_produto():
    global db
    mycol = db.produto
    print("\nInserindo um novo produto")
    nome = input("Nome do produto: ")
    descricao = input("Descrição: ")
    preco = float(input("Preço: ") or 0.0)
    print("Qual vendedor vende este produto?")
    vendedor = escolher(db.vendedor.find().sort("nome"), lambda v: f'{v["nome"]} ({v.get("loja", "")})')
    if not vendedor:
        print("Produto não cadastrado: é preciso escolher um vendedor.")
        return

    mydoc = { "nome": nome, "descricao": descricao, "preco": preco, "vendedor_id": vendedor["_id"] }
    x = mycol.insert_one(mydoc)
    print("Produto inserido com ID ", x.inserted_id)

def read_produto(nome):
    global db
    mycol = db.produto
    print("Produtos existentes: ")
    if not len(nome):
        for x in sorted(com_nomes("produto", {}, [("vendedor_id", "vendedor")]), key=lambda p: p["nome"]):
            print(f"{x['nome']} - R$ {x.get('preco', 'Sem preço')} - Loja: {nome_ligado(x, 'vendedor', 'loja')}")
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)        

def update_produto(nome):
    global db
    mycol = db.produto
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if mydoc: 
        print("Dados do produto: ", mydoc)
        novo_nome = input("Mudar Nome do Produto (ou enter para pular): ")
        if len(novo_nome):
            mydoc["nome"] = novo_nome

        novo_preco = input("Mudar Preço (ou enter para pular): ")
        if len(novo_preco):
            mydoc["preco"] = float(novo_preco)

        newvalues = { "$set": mydoc }
        mycol.update_one(myquery, newvalues)
        print("Produto atualizado!")
    else:
        print("Produto não encontrado.")            

def delete_produto(nome):
    global db
    mycol = db.produto
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o produto. Quantidade removida: ", mydoc.deleted_count)
    
#===========================================================
# CRUD (Vendedor)
#===========================================================

def create_vendedor():
    global db
    mycol = db.vendedor
    print("\nInserindo um novo vendedor")
    nome = input("Nome do vendedor/responsável: ")
    cnpj = input("CNPJ ou CPF: ")
    loja = input("Nome da loja: ")

    mydoc = { "nome": nome, "cnpj": cnpj, "loja": loja }
    x = mycol.insert_one(mydoc)
    print("Vendedor inserido com ID ", x.inserted_id)

def read_vendedor(nome):
    global db
    mycol = db.vendedor
    print("Vendedores existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"], "-", x.get("loja", "Sem loja vinculada"))
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)    

def update_vendedor(nome):
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if mydoc:
        print("Dados do vendedor: ", mydoc)
        novo_nome = input("Mudar nome do vendedor (ou enter para pular): ")
        if len(novo_nome):
            mydoc["nome"] = novo_nome

        nova_loja = input("Mudar nome da Loja (ou enter para pular): ")
        if len(nova_loja):
            mydoc["loja"] = nova_loja

        newvalues = { "$set": mydoc }
        mycol.update_one(myquery, newvalues)
        print("Vendedor atualizado!")  
    else:
        print("Vendedor não encontrado.")          

def delete_vendedor(nome):
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o vendedor. Quantidade removida: ", mydoc.deleted_count)    

#===========================================================
# CRUD (Compras - Com Snapshot Histórico)
#===========================================================

def create_compra():
    global db
    mycol = db.compras
    print("\nInserindo uma nova compra")
    usuario = buscar_usuario_cpf()
    if not usuario:
        return
    produto = escolher_produto()
    if not produto:
        return
    quantidade = int(input("Quantidade: ") or 1)

    # Salvando um Snapshot do produto no momento da compra 
    mydoc = {
        "usuario_id": usuario["_id"],
        "quantidade": quantidade,
        "data_compra": datetime.utcnow(),
        "produto_snapshot": {
            "produto_id": produto["_id"],
            "nome": produto["nome"],
            "preco": produto.get("preco", 0.0)
        }
    }
    x = mycol.insert_one(mydoc)
    print("Compra inserida com ID", x.inserted_id)

def read_compra(cpf):
    global db
    print("Compras existentes: ")
    filtro = {}
    if len(cpf):
        u = db.usuario.find_one({"cpf": cpf})
        if not u:
            print("Usuário não encontrado.")
            return
        filtro = {"usuario_id": u["_id"]}
    
    # Traz as compras cruzando apenas com o usuário para exibir o nome dele
    pipeline = [{"$match": filtro}]
    pipeline.append({"$lookup": {"from": "usuario", "localField": "usuario_id", "foreignField": "_id", "as": "usuario"}})
    
    compras = list(db.compras.aggregate(pipeline))
    if not compras:
        print("Nenhuma compra encontrada.")
        return
        
    for c in compras:
        nome_cli = c["usuario"][0]["nome"] if c.get("usuario") else "(removido)"
        prod = c.get("produto_snapshot", {})
        print(f"Cliente: {nome_cli} | Produto: {prod.get('nome')} | Preço Pago: R$ {prod.get('preco')} | Qtd: {c['quantidade']}")

def update_compra():
    global db
    u = buscar_usuario_cpf()
    if not u:
        return
    compras_usuario = list(db.compras.find({"usuario_id": u["_id"]}))
    compra_escolhida = escolher(compras_usuario, lambda c: f"Produto: {c['produto_snapshot']['nome']} - Qtd: {c['quantidade']}")
    if not compra_escolhida:
        return
        
    nova_qtd = input("Mudar Quantidade (ou enter para pular): ")
    if len(nova_qtd):
        db.compras.update_one({"_id": compra_escolhida["_id"]}, {"$set": {"quantidade": int(nova_qtd)}})
        print("Compra atualizada!")
    else:
        print("Nada foi alterado.")

def delete_favorito():
    global db
    usuario = buscar_usuario_cpf()
    if not usuario:
        return

    favoritos = usuario.get("favoritos", [])
    if not favoritos:
        print("O usuário não possui favoritos cadastrados.")
        return

    escolhido = escolher(favoritos, lambda f: f'{f["nome"]} - R$ {f.get("preco", "")}')
    if not escolhido:
        return

    # $pull remove do array o subdocumento cujo produto_id bate
    db.usuario.update_one(
        {"_id": usuario["_id"]},
        {"$pull": {"favoritos": {"produto_id": escolhido["produto_id"]}}}
    )
    print("Produto removido dos favoritos!")

#===========================================================
# CRUD (Favoritos)
#===========================================================

def create_favorito():
    global db
    print("\nAdicionando produto aos favoritos")
    usuario = buscar_usuario_cpf()
    if not usuario:
        return
    produto = escolher_produto()
    if not produto:
        return


    if db.usuario.find_one({"_id": usuario["_id"], "favoritos.produto_id": produto["_id"]}):
        print("Este produto já está na lista de favoritos do usuário.")
        return

    favorito = {
        "produto_id": produto["_id"],
        "nome": produto["nome"],
        "descricao": produto.get("descricao", ""),
        "preco": produto.get("preco", 0.0)
    }

    db.usuario.update_one(
        {"_id": usuario["_id"]},
        {"$push": {"favoritos": favorito}}
    )
    print("Produto adicionado aos favoritos com sucesso!")

def read_favorito(cpf):
    global db
    print("Favoritos existentes: ")
    if not len(cpf):
        print("Para listar favoritos, informe o CPF do usuário.")
        return
    
    u = db.usuario.find_one({"cpf": cpf})
    if not u:
        print("Usuário não encontrado.")
        return
    
    favoritos = u.get("favoritos", [])
    if not favoritos:
        print("O usuário não possui produtos favoritos.")
        return

    print(f"\nFavoritos de {u['nome']}:")
    for f in favoritos:
        print(f"- {f['nome']} | {f.get('descricao', '')} | R$ {f.get('preco', 'Sem preço')}")

def update_favorito():
    print("No modelo embutido, utilize Adicionar (1) ou Deletar (4) para gerenciar favoritos.")

def delete_favorito():
    global db
    usuario = buscar_usuario_cpf()
    if not usuario:
        return
    
    produto_ids = usuario.get("favoritos", [])
    if not produto_ids:
        print("O usuário não possui favoritos cadastrados.")
        return
    
    escolhido = escolher(favoritos, lambda f: f'{f["nome"]} - R$ {f.get("preco", "")}')
    if not escolhido:
        return

    db.usuario.update_one(
        {"_id": usuario["_id"]},
        {"$pull": {"favoritos": {"produto_id": escolhido["produto_id"]}}}
    )
    print("Produto removido dos favoritos!")
    
    # $pull remove o ID do produto do array do usuário de forma limpa
    db.usuario.update_one(
        {"_id": usuario["_id"]},
        {"$pull": {"favoritos": produto_escolhido["_id"]}}
    )
    print("Produto removido dos favoritos!")

#===========================================================
# MENU PRINCIPAL (CLI)
#===========================================================

key = 0
sub = 0
while (key != 'S'):
    print("\n1-CRUD Usuário")
    print("2-CRUD Vendedor")
    print("3-CRUD Produto")
    print("4-CRUD Compras")
    print("5-CRUD Favoritos")
    key = input("Digite a opção desejada? (S para sair) ").upper()

    if (key == '1'):
        print("=======Menu do Usuário=======")
        print("1-Create Usuário")
        print("2-Read Usuário")
        print("3-Update Usuário")
        print("4-Delete Usuário")
        sub = input("Digite a opção desejada? (V para voltar) ")
        if (sub == '1'):
            create_usuario()
        elif (sub == '2'):
            nome = input("Read usuário, deseja algum nome específico? (Enter para todos): ")
            read_usuario(nome)
        elif (sub == '3'):
            nome = input("Update usuário, digite o nome do usuário: ")
            update_usuario(nome)
        elif (sub == '4'):
            nome = input("Nome a ser deletado: ")
            sobrenome = input("Sobrenome a ser deletado: ")
            delete_usuario(nome, sobrenome)
            
    elif (key == '2'):
        print("========Menu do Vendedor========") 
        print("1-Create Vendedor")
        print("2-Read Vendedor")
        print("3-Update Vendedor")
        print("4-Delete Vendedor")
        sub = input("Digite a opção desejada? (V para voltar) ")

        if (sub == '1'):
            create_vendedor()
        elif (sub == '2'):
            nome = input("Read vendedor, deseja algum nome específico (Enter para todos): ")
            read_vendedor(nome)
        elif (sub == '3'):
            nome = input("Update vendedor, digite o nome atual do vendedor: ")
            update_vendedor(nome)
        elif (sub == '4'):
            nome = input("Delete vendedor, digite o nome a ser deletado: ")
            delete_vendedor(nome)            
               
    elif (key == '3'):
        print("========Menu do Produto=======")  
        print("1-Create Produto")
        print("2-Read Produto")
        print("3-Update Produto")
        print("4-Delete Produto") 
        sub = input("Digite a opção desejada? (V para voltar) ")   

        if (sub == '1'):
            create_produto()
        elif (sub == '2'):
            nome = input("Read produto, deseja algum nome específico? (Enter para todos): ")
            read_produto(nome)
        elif (sub == '3'):
            nome = input("Update produto, digite o nome atual do produto: ")
            update_produto(nome)
        elif (sub == '4'):
            nome = input("Delete produto, digite o nome a ser deletado: ")
            delete_produto(nome)      

    elif (key == '4'):
        print("========Menu de Compras=======")  
        print("1-Create Compra")
        print("2-Read Compra")
        print("3-Update Compra")
        print("4-Delete Compra") 
        sub = input("Digite a opção desejada? (V para voltar) ")   

        if (sub == '1'):
            create_compra()
        elif (sub == '2'):
            cpf = input("Read compra, CPF do usuário (Enter para todos): ")
            read_compra(cpf)
        elif (sub == '3'):
            update_compra()
        elif (sub == '4'):
            delete_compra()

    elif (key == '5'):
        print("========Menu de Favoritos=======")  
        print("1-Create Favorito")
        print("2-Read Favorito")
        print("3-Update Favorito")
        print("4-Delete Favorito") 
        sub = input("Digite a opção desejada? (V para voltar) ")   

        if (sub == '1'):
            create_favorito()
        elif (sub == '2'):
            cpf = input("Read favorito, CPF do usuário (Enter para todos): ")
            read_favorito(cpf)
        elif (sub == '3'):
            update_favorito()
        elif (sub == '4'):
            delete_favorito()                     

print("Tchau Prof...")