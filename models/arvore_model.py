import csv
import math

def carregar_animais(caminho_arquivo):
    animais = []
    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            animal = {}
            for k, v in linha.items():
                if k == 'animais':
                    animal['animal'] = v
                else:
                    animal[k] = (v == 'True')
            animais.append(animal)
    return animais

def entropia(exemplos):
    total = len(exemplos)
    if total == 0:
        return 0
    freq = {}
    for e in exemplos:
        animal = e['animal']
        freq[animal] = freq.get(animal, 0) + 1
    ent = 0
    for c in freq.values():
        p = c / total
        ent -= p * math.log2(p)
    return ent

def ganho_informacao(exemplos, atributo):
    total = len(exemplos)
    if total == 0:
        return 0
    ent_inicial = entropia(exemplos)
    subset_true = [e for e in exemplos if e[atributo]]
    subset_false = [e for e in exemplos if not e[atributo]]
    ent_true = entropia(subset_true)
    ent_false = entropia(subset_false)
    ent_ponderada = (len(subset_true)/total)*ent_true + (len(subset_false)/total)*ent_false
    return ent_inicial - ent_ponderada

def construir_arvore(exemplos, atributos):
    animais = set(e['animal'] for e in exemplos)
    if len(animais) == 1:
        return {'tipo': 'folha', 'animal': exemplos[0]['animal']}

    if not atributos:
        freq = {}
        for e in exemplos:
            freq[e['animal']] = freq.get(e['animal'], 0) + 1
        animal_mais_comum = max(freq, key=freq.get)
        return {'tipo': 'folha', 'animal': animal_mais_comum}

    ganhos = [(atributo, ganho_informacao(exemplos, atributo)) for atributo in atributos]
    atributo_melhor, ganho_max = max(ganhos, key=lambda x: x[1])

    if ganho_max == 0:
        freq = {}
        for e in exemplos:
            freq[e['animal']] = freq.get(e['animal'], 0) + 1
        animal_mais_comum = max(freq, key=freq.get)
        return {'tipo': 'folha', 'animal': animal_mais_comum}

    exemplos_true = [e for e in exemplos if e[atributo_melhor]]
    exemplos_false = [e for e in exemplos if not e[atributo_melhor]]
    atributos_restantes = [a for a in atributos if a != atributo_melhor]

    return {
        'tipo': 'nó',
        'atributo': atributo_melhor,
        'true': construir_arvore(exemplos_true, atributos_restantes),
        'false': construir_arvore(exemplos_false, atributos_restantes)
    }
