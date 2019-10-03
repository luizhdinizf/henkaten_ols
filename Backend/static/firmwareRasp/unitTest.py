from mongoCli import *
wpInfo = { 
    "_id" : "5d9021cb0b84d14281061ed3", 
    "N" : 1, 
    "cliente" : "Fiat", 
    "area" : "Ato", 
    "linha" : "Vão Motor XMF", 
    "modelo" : "Vão Motor XMF", 
    "requisitos" : [
        "DIRECIONAMENTO", 
        "ACABAMENTO",
    ], 
    "colaboradores" : [
        "2536", 
        "2137", 
        "851"
    ], 
    "reconhecidos" : [

    ], 
    "mac" : "0x87fdb4b8ca2d"
    }


encodedFaces,nomes,missingSkills = getInformation(wpInfo)
print(encodedFaces)
print("\n")
print(nomes)
print("\n")
print(missingSkills)

print("\n\n\n")
wpInfo2=getWorkplaceInfo({'mac':'0x87fdb4b8ca2d'})
encodedFaces,nomes,missingSkills = getInformation(wpInfo2)
print(encodedFaces)
print("\n")
print(nomes)
print("\n")
print(missingSkills)



#print(a)
#print(b)