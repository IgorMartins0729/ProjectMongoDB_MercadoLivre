# 1. importar as bibliotecas que vou usar
import pymongo
import dotenv
import os 

# 2. carregar o arquivo .env
dotenv.load_dotenv("atlas-credentials.env")

# 3. ler a URI da variável de ambiente

uri = os.getenv("MONGODB_URI")

# 4. criar o cliente (a conexão)
client = pymongo.MongoClient(uri)

# 5. escolher o banco "mercadolivre"
db = client.mercadolivre

# 6. testar se conectou
try:
    client.admin.command("ping")
    print("Conectado")
except Exception as erro:
    print("Deu ruim", erro)    


# função create_vendedor
def create_vendedor():
#   1. pedir ao usuário o nome do responsável
    nome = input("Digite o nome do responsável/vendedor: ")
#   2. pedir o CNPJ ou CPF
    cnpj = input("Digite o CNPJ do vendedor: ")
#   3. pedir o nome da loja
    loja = input("Digite o nome da Loja do vendedor: ")
#   4. montar o documento com esses dados
    todos_valores = {
        "nome": nome,
        "cnpj": cnpj,
        "loja": loja
    }
#   5. inserir na coleção "vendedor"
    resultado = db.vendedor.insert_one(todos_valores)
#   6. avisar que deu certo 
    print(resultado.inserted_id)
    print("Registrado novo vendedor no banco")

# função read_vendedor
def read_vendedor(nome):
    #   1. avisar que vai listar
    print("Segue os vendedores cadastrados:") 
    #   2. se o nome foi informado: buscar só os vendedores com esse nome
    if nome != "":
        resultado = db.vendedor.find({"nome": nome})

    #   3. senão: buscar todos
    else:
        resultado = db.vendedor.find()  

#   4. para cada vendedor encontrado, mostrar os dados
    for x in resultado: 
        print(x["nome"], x["cnpj"],x["loja"])

# função update_vendedor(nome)
def update_vendedor(nome):
#   1. procurar o vendedor com esse nome
    vendedor = db.vendedor.find_one({"nome": nome})
    #   2. se não achou: avisar e sair da função
    if not vendedor:
        print("Não encontrado vendedor informado")
    else:
        print(vendedor)
        #3. pedir os novos valores (Enter para manter o atual)
        nome_novo = input("Novo nome (ou Enter para manter): ")
        cnpj_novo = input("Novo cnpj (ou Enter para manter): ")
        loja_novo = input("Nova loja (ou Enter para manter): ")

        mudancas = {}
        if nome_novo:
            mudancas["nome"] = nome_novo
        if cnpj_novo:
            mudancas["cnpj"] = cnpj_novo
        if loja_novo:
            mudancas["loja"] = loja_novo   
        #4. gravar a alteração no banco  
        if mudancas:
            resultado = db.vendedor.update_one({"_id": vendedor["_id"]}, {"$set": mudancas})
            print("Dados atualizados com sucesso. Foram alterados: ", resultado)
        else:
            print("Dados permanecem os mesmos")    
        

# função delete_vendedor(nome)
#   1. procurar o vendedor com esse nome
#   2. se não achou: avisar e sair
#   3. mostrar o vendedor e pedir confirmação (S/N)
#   4. se confirmou: apagar
#   5. senão: avisar que foi cancelado