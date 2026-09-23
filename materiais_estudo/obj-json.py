import json

#texto
x =  '{ "name":"John", "age":30, "city":"New York"}'

#transformo para objeto
y = json.loads(x)

#manipulo obejeto
print(y["age"])
y["age"] = 35

if y["city"]:
    del y["city"]

if "nome" in y:
    del y["nome"]
else:
    print("Não existe...")

#transformo em texto
t = json.dumps(y)
print(t)