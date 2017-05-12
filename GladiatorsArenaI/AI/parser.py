from sys import *

def parse_weights(numberExpectedParams, filename):
    
    f = open(filename, 'r')
    contents = f.readlines()
    
    params = []
    linenumber=0
    for i in contents:
        linenumber = linenumber + 1
        i = i.strip()
        if i == "":
            continue
                
        try:
            paramVal = float(i)
            params.append(paramVal)
        except ValueError:
            print "Ao ler arquivo de parametros (%s), esperava um numero real na linha %d, mas encontrou '%s'. Verifique" % (filename, linenumber, i)
            exit()

    if len(params) != numberExpectedParams:
        print "Numero incorreto de pesos no arquivo informado! Foram encontrados %d pesos, mas o seu controlador utiliza %d" % (len(params), numberExpectedParams)
        exit()
        
    print "Leitura de %d pesos teve sucesso: %s" % (numberExpectedParams, params)

    return params
