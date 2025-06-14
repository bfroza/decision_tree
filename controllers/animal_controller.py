import os
from models.arvore_model import carregar_animais, construir_arvore

def gerar_arvore_decisao():
    caminho_csv = os.path.join('data', 'animais.csv')  # Caminho atualizado
    animais = carregar_animais(caminho_csv)
    atributos = [k for k in animais[0].keys() if k != 'animal']
    arvore = construir_arvore(animais, atributos)
    return arvore
