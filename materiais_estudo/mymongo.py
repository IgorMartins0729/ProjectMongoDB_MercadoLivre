import pymongo
from pymongo.server_api import ServerApi

uri = "mongodb+srv://igormartins4_db_user:Wl49wDLRAQrew35A@cluster0.up0m3py.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = pymongo.MongoClient(
    uri,
    server_api = ServerApi("1")
)

try: 
    client.admin.command("ping")
    print("funcionou")
except Exception as e:
    print("erro")
    print(e)

db = client.test


global mydb
mydb = client.mercadolivre

def findSort():
    #Sort
    global mydb
    mycol = mydb.usuario
    print("\n####SORT####") 
    mydoc = mycol.find().sort("nome")
    for x in mydoc:
        print(x)

def findQuery():
    #Query
    global mydb
    mycol = mydb.usuario
    print("\n####QUERY####")
    myquery = { "nome": "Diogo Branquinho" }
    mydoc = mycol.find(myquery)
    for x in mydoc:
        print(x)

def insert(nome, cpf):
    #Insert
    global mydb
    mycol = mydb.usuario
    print("\n####INSERT####")
    mydict = { "nome": nome, "cpf":cpf}
    x = mycol.insert_one(mydict)
    print(x.inserted_id)


############# main

findSort()
findQuery()
insert("Mane eh mane", "123.123.123.11")

