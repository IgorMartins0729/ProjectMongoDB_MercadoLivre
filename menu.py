import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(diretorio_atual, "atlas-credentials.env")

load_dotenv(caminho_env)

uri = os.getenv("MONGODB_URI")
print("Conectando ao MongoDB Atlas...")

client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def buscar_usuario_cpf():
    cpf = input("CPF do usuário: ")
    u = db.usuario.find_one({"cpf": cpf})
    if not u:
        print("Usuário não encontrado.")
    return u

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
    mycol.update_one({"_id": mydoc["_id"]}, newvalues)

    db.compras.update_many(
        {"usuario.usuario_id": mydoc["_id"]},
        {"$set": {
            "usuario.nome": mydoc["nome"],
            "usuario.sobrenome": mydoc.get("sobrenome", ""),
            "usuario.cpf": mydoc["cpf"]
        }}
    )
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

    mydoc = {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "vendedores": [{
            "vendedor_id": vendedor["_id"],
            "nome": vendedor["nome"],
            "loja": vendedor.get("loja", "")
        }]
    }
    x = mycol.insert_one(mydoc)
    print("Produto inserido com ID ", x.inserted_id)

def lojas_do_produto(p):
    lojas = [v.get("loja", "") for v in p.get("vendedores", [])]
    return ", ".join(lojas) if lojas else "Sem loja"

def read_produto(nome):
    global db
    mycol = db.produto
    print("Produtos existentes: ")
    if not len(nome):
        for x in mycol.find().sort("nome"):
            print(f"{x['nome']} - R$ {x.get('preco', 'Sem preço')} - Loja: {lojas_do_produto(x)}")
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
        mycol.update_one({"_id": mydoc["_id"]}, newvalues)
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
        mycol.update_one({"_id": mydoc["_id"]}, newvalues)

        db.produto.update_many(
            {"vendedores.vendedor_id": mydoc["_id"]},
            {"$set": {
                "vendedores.$[v].nome": mydoc["nome"],
                "vendedores.$[v].loja": mydoc.get("loja", "")
            }},
            array_filters=[{"v.vendedor_id": mydoc["_id"]}]
        )
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
# CRUD (Compras)
#===========================================================

def montar_item():
    produto = escolher_produto()
    if not produto:
        return None
    quantidade = int(input("Quantidade: ") or 1)
    return {
        "produto_id": produto["_id"],
        "nome": produto["nome"],
        "preco": produto.get("preco", 0.0),
        "quantidade": quantidade,
        "vendedores": [
            {"vendedor_id": v.get("vendedor_id"), "nome": v.get("nome", ""), "loja": v.get("loja", "")}
            for v in produto.get("vendedores", [])
        ]
    }

def resumo_compra(c):
    itens = ", ".join(f"{i['nome']} x{i['quantidade']}" for i in c.get("itens", []))
    return itens or "(sem itens)"

def create_compra():
    global db
    mycol = db.compras
    print("\nInserindo uma nova compra")
    usuario = buscar_usuario_cpf()
    if not usuario:
        return

    itens = []
    while True:
        item = montar_item()
        if item:
            existente = next((i for i in itens if i["produto_id"] == item["produto_id"]), None)
            if existente:
                existente["quantidade"] += item["quantidade"]
            else:
                itens.append(item)
        if not itens:
            print("Compra não cadastrada: é preciso escolher ao menos um item.")
            return
        if input("Deseja adicionar outro item (S/N)? ").upper() != 'S':
            break

    mydoc = {
        "usuario": {
            "usuario_id": usuario["_id"],
            "nome": usuario["nome"],
            "sobrenome": usuario.get("sobrenome", ""),
            "cpf": usuario["cpf"]
        },
        "data_compra": datetime.now(timezone.utc),
        "itens": itens
    }
    x = mycol.insert_one(mydoc)
    print("Compra inserida com ID", x.inserted_id)

def read_compra(cpf):
    global db
    print("Compras existentes: ")
    filtro = {}
    if len(cpf):
        filtro = {"usuario.cpf": cpf}

    compras = list(db.compras.find(filtro))
    if not compras:
        print("Nenhuma compra encontrada.")
        return

    for c in compras:
        cli = c.get("usuario", {})
        print(f"\nCliente: {cli.get('nome')} {cli.get('sobrenome', '')} | Data: {c['data_compra']:%d/%m/%Y %H:%M}")
        total = 0
        for i in c.get("itens", []):
            vend = ", ".join(f"{v.get('nome')} ({v.get('loja')})" for v in i.get("vendedores", [])) or "Sem vendedor"
            subtotal = i.get("preco", 0) * i["quantidade"]
            total += subtotal
            print(f"  - {i['nome']} | Vendedor: {vend} | R$ {i.get('preco')} x {i['quantidade']} = R$ {subtotal:.2f}")
        print(f"  Total: R$ {total:.2f}")

def update_compra():
    global db
    u = buscar_usuario_cpf()
    if not u:
        return
    compras_usuario = list(db.compras.find({"usuario.usuario_id": u["_id"]}))
    compra = escolher(compras_usuario, resumo_compra)
    if not compra:
        return

    print("1-Alterar quantidade de um item")
    print("2-Adicionar outro item")
    print("3-Remover um item")
    op = input("Digite a opção desejada: ")

    if op == '1':
        item = escolher(compra["itens"], lambda i: f"{i['nome']} - Qtd: {i['quantidade']}")
        if not item:
            return
        nova_qtd = input("Mudar Quantidade (ou enter para pular): ")
        if len(nova_qtd):
            idx = compra["itens"].index(item)
            db.compras.update_one({"_id": compra["_id"]}, {"$set": {f"itens.{idx}.quantidade": int(nova_qtd)}})
            print("Compra atualizada!")
        else:
            print("Nada foi alterado.")

    elif op == '2':
        item = montar_item()
        if not item:
            return
        r = db.compras.update_one(
            {"_id": compra["_id"], "itens.produto_id": item["produto_id"]},
            {"$inc": {"itens.$.quantidade": item["quantidade"]}}
        )
        if r.matched_count == 0:
            db.compras.update_one({"_id": compra["_id"]}, {"$push": {"itens": item}})
        print("Item adicionado à compra!")

    elif op == '3':
        if len(compra["itens"]) == 1:
            print("A compra só tem um item. Use Delete Compra para removê-la.")
            return
        item = escolher(compra["itens"], lambda i: f"{i['nome']} - Qtd: {i['quantidade']}")
        if not item:
            return
        db.compras.update_one({"_id": compra["_id"]}, {"$pull": {"itens": {"produto_id": item["produto_id"]}}})
        print("Item removido da compra!")

    else:
        print("Opção inválida.")

def delete_compra():
    global db
    u = buscar_usuario_cpf()
    if not u:
        return
    compras_usuario = list(db.compras.find({"usuario.usuario_id": u["_id"]}))
    compra_escolhida = escolher(compras_usuario, resumo_compra)
    if not compra_escolhida:
        return

    r = db.compras.delete_one({"_id": compra_escolhida["_id"]})
    print("Compra deletada. Quantidade removida: ", r.deleted_count)

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
    global db
    usuario = buscar_usuario_cpf()
    if not usuario:
        return

    favoritos = usuario.get("favoritos", [])
    if not favoritos:
        print("O usuário não possui favoritos cadastrados.")
        return

    print("Escolha o favorito a ser trocado:")
    atual = escolher(favoritos, lambda f: f'{f["nome"]} - R$ {f.get("preco", "")}')
    if not atual:
        return

    novo = escolher_produto()
    if not novo:
        return

    if any(f["produto_id"] == novo["_id"] for f in favoritos):
        print("Este produto já está na lista de favoritos do usuário.")
        return

    novo_favorito = {
        "produto_id": novo["_id"],
        "nome": novo["nome"],
        "descricao": novo.get("descricao", ""),
        "preco": novo.get("preco", 0.0)
    }

    db.usuario.update_one(
        {"_id": usuario["_id"], "favoritos.produto_id": atual["produto_id"]},
        {"$set": {"favoritos.$": novo_favorito}}
    )
    print("Favorito trocado com sucesso!")

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

    db.usuario.update_one(
        {"_id": usuario["_id"]},
        {"$pull": {"favoritos": {"produto_id": escolhido["produto_id"]}}}
    )
    print("Produto removido dos favoritos!")

#===========================================================
# MENU PRINCIPAL
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