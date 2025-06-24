import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from controllers.animal_controller import gerar_arvore_decisao
from copy import deepcopy
import duckduckgo_search
import matplotlib.pyplot as plt
import networkx as nx

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}})

perguntas = { 
    'mamifero': "O seu animal se alimenta de leite quando filhote?", 
    'ave': "O seu animal consegue voar durante um tempo?", 
    'reptil': "O seu animal tem sangue frio (réptil) ?", 
    'anfibio': "O seu animal vive parte do tempo na água e parte em terra?", 
    'carnivoro': "O seu animal se alimenta de carne ou insetos?", 
    'herbivoro': "O seu animal se alimenta de plantas?", 
    'pelos': "O seu animal tem pelos cobrindo o corpo?", 
    'penas': "O seu animal tem o corpo coberto penas?", 
    'escamas': "O corpo do seu animal é tem o corpo coberto por escamas?", 
    'aquatico': "O seu animal vive somente na água?", 
    'terrestre': "O seu animal vive em terra firme uma boa parte do tempo?", 
    'aereo': "O seu animal costuma voar?", 
    'chifre': "O seu animal tem chifres?", 
    'presas': "O seu animal possui presas, dentes caninos grandes?", 
    'pescoco': "O seu animal tem um pescoço longo?", 
    'dentes': "O seu animal possui dentes?", 
    'ovos': "O seu animal bota ovos?", 
    'bipede': "O seu animal anda em duas patas?", 
    'venenoso': "O seu animal é venenoso?", 
    'listras': "O seu animal tem listras no corpo?", 
    'cauda': "O seu animal possui cauda longa?" 
}
arvore_global = gerar_arvore_decisao()

@app.route('/arvore', methods=['GET'])
def endpoint_arvore():
    return jsonify(arvore_global)

def animais_possiveis(no):
    if no['tipo'] == 'folha':
        return [no['animal']]
    else:
        return animais_possiveis(no['true']) + animais_possiveis(no['false'])
def criar_grafo_arvore(no, G=None, parent=None, edge_label=None):
    if G is None:
        G = nx.DiGraph()

    if no['tipo'] == 'folha':
        G.add_node(no['animal'], label=no['animal'])
        if parent:
            G.add_edge(parent, no['animal'], label=edge_label)
    else:
        G.add_node(no['atributo'], label=no['atributo'])
        if parent:
            G.add_edge(parent, no['atributo'], label=edge_label)
        criar_grafo_arvore(no['true'], G, no['atributo'], 'sim')
        criar_grafo_arvore(no['false'], G, no['atributo'], 'não')

    return G

def mostrar_arvore_com_caminho(arvore, caminho=[]):
    G = criar_grafo_arvore(arvore)

    pos = nx.spring_layout(G, seed=42)

    labels = nx.get_node_attributes(G, 'label')
    edge_labels = nx.get_edge_attributes(G, 'label')

    plt.figure(figsize=(12, 8))

    node_colors = []
    for node in G.nodes():
        # Destacar em verde claro os nós do caminho escolhido
        if node in caminho or any(n in caminho for n in G.predecessors(node)):
            node_colors.append('lightgreen')
        else:
            node_colors.append('lightblue')

    nx.draw(G, pos, labels=labels, with_labels=True, node_color=node_colors, node_size=2000, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Árvore de Decisão do Animal (Caminho Destacado)")
    plt.show()



@app.route('/pergunta', methods=['POST'])
def endpoint_pergunta():
    dados = request.get_json()
    caminho = dados.get('caminho', [])
    resposta = dados.get('resposta', '').lower()
    perguntas_restantes = dados.get('perguntas_restantes', list(perguntas.keys()))

    if not caminho and resposta in ['', 'iniciar']:
        perguntas_restantes = list(perguntas.keys())
        atributo_sorteado = random.choice(perguntas_restantes)
        perguntas_restantes.remove(atributo_sorteado)
        mensagem_personalizada = perguntas[atributo_sorteado]

        mostrar_arvore_com_caminho(arvore_global, caminho)

        return jsonify({
            'tipo': 'pergunta',
            'atributo': atributo_sorteado,
            'mensagem': mensagem_personalizada,
            'caminho': caminho,
            'perguntas_restantes': perguntas_restantes,
        })

    no_atual = deepcopy(arvore_global)
    for passo in caminho:
        if no_atual['tipo'] == 'folha':
            break
        no_atual = no_atual.get(passo)

    if no_atual['tipo'] == 'folha':
        mostrar_arvore_com_caminho(arvore_global, caminho)
        return jsonify({
            'tipo': 'folha',
            'animal': no_atual['animal'],
            'mensagem': f"Acho que o seu animal é um {no_atual['animal']}. Estou certo?",
            'caminho': caminho,
        })

    if resposta == 'sim':
        caminho.append('true')
        if no_atual['atributo'] in perguntas_restantes:
            perguntas_restantes.remove(no_atual['atributo'])
    elif resposta in ['não', 'nao']:
        caminho.append('false')
        if no_atual['atributo'] in perguntas_restantes:
            perguntas_restantes.remove(no_atual['atributo'])
    elif resposta in ['não sei', 'nao sei']:
        mensagem_personalizada = perguntas.get(no_atual['atributo'], f"O animal tem a característica '{no_atual['atributo']}'?")
        mostrar_arvore_com_caminho(arvore_global, caminho)
        return jsonify({
            'tipo': 'pergunta',
            'atributo': no_atual['atributo'],
            'mensagem': mensagem_personalizada,
            'caminho': caminho,
            'perguntas_restantes': perguntas_restantes,
        })
    else:
        return jsonify({'erro': 'Resposta inválida'}), 400

    no_proximo = deepcopy(arvore_global)
    for passo in caminho:
        if no_proximo['tipo'] == 'folha':
            break
        no_proximo = no_proximo.get(passo)

    mostrar_arvore_com_caminho(arvore_global, caminho)

    if no_proximo['tipo'] == 'folha':
        return jsonify({
            'tipo': 'folha',
            'animal': no_proximo['animal'],
            'mensagem': f"Acho que o seu animal é um {no_proximo['animal']}. Estou certo?",
            'caminho': caminho,
            'perguntas_restantes': perguntas_restantes,
        })
    else:
        if perguntas_restantes:
            atributo_sorteado = random.choice(perguntas_restantes)
            perguntas_restantes.remove(atributo_sorteado)
            mensagem_personalizada = perguntas.get(atributo_sorteado, f"O animal tem a característica '{atributo_sorteado}'?")
            return jsonify({
                'tipo': 'pergunta',
                'atributo': atributo_sorteado,
                'mensagem': mensagem_personalizada,
                'caminho': caminho,
                'perguntas_restantes': perguntas_restantes,
            })
        else:
            return jsonify({
                'tipo': 'fim',
                'mensagem': "Não há mais perguntas para fazer.",
                'caminho': caminho,
                'perguntas_restantes': perguntas_restantes,
            })

@app.route('/confirmar', methods=['POST'])
def confirmar():
    dados = request.json
    animal = dados.get('animal')
    resposta = dados.get('resposta')

    if not animal or not resposta:
        return jsonify({'resultado': "Dados incompletos na requisição."}), 400

    if resposta.lower() == 'sim':
        url_imagem = buscar_imagem(animal)
        if url_imagem:
            return jsonify({'resultado': f"Acertei! Aqui está uma imagem do {animal}.", 'imagem': url_imagem})
        else:
            return jsonify({'resultado': f"Acertei, mas não encontrei imagem do {animal}."})
    else:
        return jsonify({'resultado': "Poxa, não consegui adivinhar. Vamos recomeçar!"})

def buscar_imagem(animal):
    try:
        with duckduckgo_search.DDGS() as ddgs:
            resultados = ddgs.images(
                keywords=animal,
                region="wt-wt",
                safesearch="off",
                max_results=1
            )
            for resultado in resultados:
                return resultado['image'] 
        return None
    except Exception as e:
        print(f"Erro ao buscar imagem: {e}")
        return None
    
    
def main():
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
