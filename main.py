import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from controllers.animal_controller import gerar_arvore_decisao
from copy import deepcopy
import duckduckgo_search

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}})


arvore_global = gerar_arvore_decisao()

@app.route('/arvore', methods=['GET'])
def endpoint_arvore():
    return jsonify(arvore_global)

def animais_possiveis(no):
    if no['tipo'] == 'folha':
        return [no['animal']]
    else:
        return animais_possiveis(no['true']) + animais_possiveis(no['false'])


@app.route('/pergunta', methods=['POST'])
def endpoint_pergunta():
    dados = request.get_json()
    caminho = dados.get('caminho', [])
    resposta = dados.get('resposta', '').lower()
    if not caminho and resposta in ['', 'iniciar']:
        no_inicial = deepcopy(arvore_global)

        if no_inicial['tipo'] == 'folha':
            return jsonify({
                'tipo': 'folha',
                'animal': no_inicial['animal'],
                'mensagem': f"Acho que o seu animal é um {no_inicial['animal']}. Estou certo?",
                'caminho': caminho,
            })

        return jsonify({
            'tipo': 'pergunta',
            'atributo': no_inicial['atributo'],
            'mensagem': f"O animal tem a característica '{no_inicial['atributo']}'?",
            'caminho': caminho
        })


    no_atual = deepcopy(arvore_global)
    for passo in caminho:
        if no_atual['tipo'] == 'folha':
            break
        no_atual = no_atual.get(passo)

    animais_antes = animais_possiveis(no_atual)

    if no_atual['tipo'] == 'folha':
        return jsonify({
            'tipo': 'folha',
            'animal': no_atual['animal'],
            'mensagem': f"Acho que o seu animal é um {no_atual['animal']}. Estou certo?",
            'caminho': caminho,
        })

    if resposta == 'sim':
        caminho.append('true')
    elif resposta in ['não', 'nao']:
        caminho.append('false')
    elif resposta in ['não sei', 'nao sei']:
        proximo_lado = random.choice(['true', 'false'])
        no_proximo = no_atual[proximo_lado]

        if no_proximo['tipo'] == 'folha':
            return jsonify({
                'tipo': 'folha',
                'animal': no_proximo['animal'],
                'mensagem': f"Acho que o seu animal é um {no_proximo['animal']}. Estou certo?",
                'caminho': caminho  
            })
        else:
            return jsonify({
                'tipo': 'pergunta',
                'atributo': no_proximo['atributo'],
                'mensagem': f"Ok, vamos tentar outra. O animal tem a característica '{no_proximo['atributo']}'?",
                'caminho': caminho  
            })

    else:
        return jsonify({'erro': 'Resposta inválida'}), 400

    no_proximo = deepcopy(arvore_global)
    for passo in caminho:
        if no_proximo['tipo'] == 'folha':
            break
        no_proximo = no_proximo.get(passo)

    animais_depois = animais_possiveis(no_proximo)
    descartados = [a for a in animais_antes if a not in animais_depois]

    if descartados:
        print(f"Animais descartados nessa pergunta: {descartados}")

    if no_proximo['tipo'] == 'folha':
        return jsonify({
            'tipo': 'folha',
            'animal': no_proximo['animal'],
            'mensagem': f"Acho que o seu animal é um {no_proximo['animal']}. Estou certo?",
            'caminho': caminho,
        })
    else:
        return jsonify({
            'tipo': 'pergunta',
            'atributo': no_proximo['atributo'],
            'mensagem': f"O animal tem a característica '{no_proximo['atributo']}'?",
            'caminho': caminho,
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
                return resultado['image']  # Garante que vai pegar a primeira imagem válida
        return None
    except Exception as e:
        print(f"Erro ao buscar imagem: {e}")
        return None


def main():
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()