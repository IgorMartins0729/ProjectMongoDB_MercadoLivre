import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(diretorio_atual, "atlas-credentials.env")

# Carrega o arquivo
load_dotenv(caminho_env)

uri = os.getenv("MONGODB_URI")
print("Testando a URI:", uri)

client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

#===========================================================
#===========================================================

#CRUD (Usuário) - Criar usuário
def create_usuario():
    global db
    mycol = db.usuario
    print("\nInserindo um novo usuário")
    nome = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    cpf = input("CPF: ")
    key = 1
    end = []
    while (key != 'N'):
        rua = input("Rua: ")
        num = input("Num: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        estado = input("Estado: ")
        cep = input("CEP: ")
        endereco = {        #isso nao eh json, isso é chave-valor, eh um obj
            "rua":rua,
            "num": num,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        }
        end.append(endereco) #estou inserindo na lista
        key = input("Deseja cadastrar um novo endereço (S/N)? ")
    mydoc = { "nome": nome, "sobrenome": sobrenome, "cpf": cpf, "end": end }
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ",x.inserted_id)

#CRUD (Usuário) - Read usuário
def read_usuario(nome):
    global db
    mycol = db.usuario
    print("Usuários existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"],x["cpf"])
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

#CRUD (Usuário) - Update usuário
def update_usuario(nome):
    global db
    mycol = db.usuario
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    print("Dados do usuário: ",mydoc)
    nome = input("Mudar Nome:")
    if len(nome):
        mydoc["nome"] = nome

    sobrenome = input("Mudar Sobrenome:")
    if len(sobrenome):
        mydoc["sobrenome"] = sobrenome

    cpf = input("Mudar CPF:")
    if len(cpf):
        mydoc["cpf"] = cpf

    newvalues = { "$set": mydoc }
    mycol.update_one(myquery, newvalues)

#CRUD (Usuário) - Delete usuário
def delete_usuario(nome, sobrenome):
    global db
    mycol = db.usuario
    myquery = {"nome": nome, "sobrenome":sobrenome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o usuário ",mydoc)


#===========================================================
#===========================================================

#CRUD (Produto) - Criar Produto
def create_produto():
    global db
    mycol = db.produto
    print("\nInserindo um novo produto")
    nome = input("Nome do produto: ")
    descricao = input("Descrição: ")
    preco = input("Preço: ")

    mydoc = { "nome": nome, "descricao": descricao, "preco": preco }
    x = mycol.insert_one(mydoc)
    print("Produto inserido com ID ", x.inserted_id)

#CRUD (Produto) - Read Produto    
def read_produto(nome):
    global db
    mycol = db.produto
    print("Produtos existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"], "-", x.get("preco", "Sem preço"))
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)        

#CRUD (Produto) - Update Produto
def update_produto(nome):
    global db
    mycol = db.produto
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if mydoc: 
        print("Dados do produto: ", mydoc)
        novo_nome = input("Mudar Nome do Produto (ou enter para pular):")
        if len(novo_nome):
            mydoc["nome"] = novo_nome

        novo_preco = input("Mudar Preço (ou entender para pular):")
        if len(novo_preco):
            mydoc["preco"] = novo_preco

        newvalues = { "$set": mydoc }
        mycol.update_one(myquery, newvalues)
        print("Produto atualizado!")
    else:
        print("Produto não encontrado.")            

#CRUD (Produto) - Delete Produto    
def delete_produto(nome):
    global db
    mycol = db.produto
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o produto. Quantidade removida: ", mydoc.deleted_count)
    
#===========================================================
#===========================================================

#CRUD (Vendedor) - Criar vendedor
def create_vendedor():
    global db
    mycol = db.vendedor
    print("\nIserindo um novo vendedor")
    nome = input("Nome do vendedor/responsável: ")
    cnpj = input("CNPJ ou CPF: ")
    loja = input("Nome da loja: ")

    mydoc = { "nome": nome, "cnpj": cnpj, "loja": loja }
    x = mycol.insert_one(mydoc)
    print("Vendedor inserido com ID ", x.inserted_id)

#CRUD (Vendedor) - Read vendedor 
def read_vendedor(nome):
    global db
    mycol = db.vendedor
    print("Vendedor existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"],"-",x.get("loja", "Sem loja vinculada"))
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)    

#CRUD (Vendedor) - Update vendedor
def update_vendedor(nome):
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if mydoc:
        print("Dados do vendedor: ", mydoc)
        novo_nome = input("Mudar nome do vendedor (ou enter para pular)")
        if len(novo_nome):
            mydoc["nome"] = novo_nome

        nova_loja = input("Mudar nome da Loja (ou enter para pular):")
        if len(nova_loja):
            mydoc["loja"] = nova_loja

        newvalues = { "$set": mydoc }
        mycol.update_one(myquery, newvalues)
        print("Vendedor atualizado!")  
    else:
        print("Vendedor não encontrado.")          

#CRUD (Vendedor) - Delete vendedor
def delete_vendedor(nome):
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o vendedor. Quantidade removida ", mydoc.deleted_count)     

#===========================================================
#===========================================================

#CRUD (Compras) - Criar compra
def create_compra():
    global db
    mycol = db.compras
    print("\nInserindo uma nova compra")
    usuario = input("Nome do usuário do comprador: ")
    produto = input("Nome do produto: ")
    quantidade = input("Quantidade: ")

    mydoc = { "usuario": usuario, "produto": produto, "quantidade": quantidade}
    x = mycol.insert_one(mydoc)
    print("Compra inserida com ID", x.inserted_id)

#CRUD (Compras) - Read compra
def read_compra(usuario):
    global db
    mycol = db.compras
    print("Compras existentes: ")
    if not len(usuario):
        mydoc = mycol.find().sort("usuario")
        for x in mydoc:
            print(x["usuario"], "-", x.get("produto", "Sem produto"))
    else:
        myquery = {"usuario": usuario}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

#CRUD (Compras) - Update compra
def update_compra(usuario):
    global db
    mycol = db.compras
    myquery = {"usuario": usuario}
    mydoc = mycol.find_one(myquery)
    if mydoc: 
        print("Dados da compra: ",mdoc)
        novo_produto = input("Mudar Produto (ou enter para pular):")
        if len(novo_produto):
            mydoc["quantidade"] = nova_produto

        nova_qtd = input("Mudar Quantidade (ou enter para pular):")
        if len(nova_qtd):
            mydoc["quantidade"] = nova_qtd


        newvalues = { "$set": mydoc }
        mycol.update_one(myquery, newvalues)
        print("Compra atualizada!")
    else:
        print("Compra não encontrada.")

#CRUD (Compras) - Delete compra
def delete_compra(usuario):
    global db
    mycol = db.compras
    myquery = {"usuario": usuario}
    mydoc = mycol.delete_one(myquery)
    print("Deletada a compra. Quantidade removida: ", mydoc.deleted_count)            

#===========================================================
#===========================================================

#CRUD (Favoritos) - Criar favorito
def create_favorito():
    global db
    mycol = db.favoritos
    print("\nInserindo um novo favorito")
    usuario = input("Nome do usuário: ")
    produto = input("Nome do produto favoritado: ")

    mydoc = { "usuario": usuario, "produto": produto }
    x = mycol.insert_one(mydoc)
    print("Favorito inserido com ID ", x.inserted_id)

#CRUD (Favoritos) - Read favorito
def read_favorito(usuario):
    global db
    mycol = db.favoritos
    print("Favoritos existentes: ")
    if not len(usuario):
        mydoc = mycol.find().sort("usuario")
        for x in mydoc:
            print(x["usuario"], "-", x.get("produto", "Sem produto"))
    else:
        myquery = {"usuario": usuario}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

#CRUD (Favoritos) - Update favorito
def update_favorito(usuario):
    global db
    mycol = db.favoritos
    myquery = {"usuario": usuario}
    mydoc = mycol.find_one(myquery)
    if mydoc:
        print("Dados do favorito: ", mydoc)
        novo_produto = input("Mudar Produto Favoritado (ou enter para pular):")
        if len(novo_produto):
            mydoc["produto"] = novo_produto

        newvalues = { "$set": mydoc }
        mycol.update_one(myquery, newvalues)
        print("Favorito atualizado!")
    else:
        print("Favorito não encontrado.")

#CRUD (Favoritos) - Delete favorito
def delete_favorito(usuario):
    global db
    mycol = db.favoritos
    myquery = {"usuario": usuario}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o favorito. Quantidade removida: ", mydoc.deleted_count)




key = 0
sub = 0
while (key != 'S'):
    print("\n1-CRUD Usuário")
    print("2-CRUD Vendedor")
    print("3-CRUD Produto")
    print("4-CRUD Compras")
    print("5-CRUD Favoritos")
    key = input("Digite a opção desejada? (S para sair) ")

    if (key == '1'):
        print("=======Menu do Usuário=======")
        print("1-Create Usuário")
        print("2-Read Usuário")
        print("3-Update Usuário")
        print("4-Delete Usuário")
        sub = input("Digite a opção desejada? (V para voltar) ")
        if (sub == '1'):
            print("Create usuario")
            create_usuario()
            
        elif (sub == '2'):
            nome = input("Read usuário, deseja algum nome especifico? ")
            read_usuario(nome)
        
        elif (sub == '3'):
            nome = input("Update usuário, deseja algum nome especifico? ")
            update_usuario(nome)

        elif (sub == '4'):
            print("delete usuario")
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
            nome = input("Read vendedor, deseja algum nome específico (Enter para todos)")
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
            nome = input("Read produto, deseja algum nome específico? (Enter para todos)")
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
            nome = input("Read compra, deseja buscar por um usuário específico? (Enter para todos)")
            read_compra(nome)
        elif (sub == '3'):
            nome = input("Update compra, digite o usuário da compra: ")
            update_compra(nome)
        elif (sub == '4'):
            nome = input("Delete compra, digite o usuário a ser deletado: ")
            delete_compra(nome)

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
            nome = input("Read favorito, deseja buscar por um usuário específico? (Enter para todos)")
            read_favorito(nome)
        elif (sub == '3'):
            nome = input("Update favorito, digite o usuário do favorito: ")
            update_favorito(nome)
        elif (sub == '4'):
            nome = input("Delete favorito, digite o usuário a ser deletado: ")
            delete_favorito(nome)                      

print("Tchau Prof...")

