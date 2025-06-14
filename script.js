let caminho = [];
let animalSugerido = null;

function iniciarJogo() {
  document.getElementById('botoes-inicio').style.display = 'none';
  document.getElementById('mensagem').innerText = 'Pensando...';

  fetch('http://127.0.0.1:5000/pergunta', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ caminho: [], resposta: 'iniciar' }) 
  })
  .then(r => r.json())
  .then(dados => {
    if (dados.tipo === 'pergunta') {
      caminho = dados.caminho;
      animalSugerido = null;
      document.getElementById('mensagem').innerText = dados.mensagem;
      toggleDisplay('botoes-pergunta', true);
    } else {
      document.getElementById('mensagem').innerText = 'Erro ao iniciar o jogo.';
    }
  });
}

function responder(resposta) {
  fetch('http://127.0.0.1:5000/pergunta', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ caminho, resposta })
  })
  .then(r => r.json())
  .then(dados => {
    if (dados.erro) {
      alert(dados.erro);
      return;
    }

    if (dados.tipo === 'folha') {
      caminho = dados.caminho;
      animalSugerido = dados.animal;
      document.getElementById('mensagem').innerText = dados.mensagem;
      toggleDisplay('botoes-pergunta', false);
      toggleDisplay('botoes-confirmacao', true);
    } else if (dados.tipo === 'pergunta') {
      caminho = dados.caminho;
      animalSugerido = null;
      document.getElementById('mensagem').innerText = dados.mensagem;
      toggleDisplay('botoes-pergunta', true);
      toggleDisplay('botoes-confirmacao', false);
    } else if (dados.tipo === 'incerto') {
      document.getElementById('mensagem').innerText = dados.mensagem;
    }
  });
}

function confirmar(resposta) {
  if (!animalSugerido) {
    alert("Nenhum animal sugerido para confirmar.");
    return;
  }

  fetch('http://127.0.0.1:5000/confirmar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ animal: animalSugerido, resposta })
  })
  .then(r => r.json())
  .then(dados => {
    document.getElementById('mensagem').innerText = dados.resultado;
    document.querySelectorAll('img').forEach(img => img.remove());

    if (dados.imagem) {
      const img = document.createElement('img');
      img.src = dados.imagem;
      img.alt = animalSugerido;
      img.style.maxWidth = '300px';
      document.body.appendChild(img);
    }

    toggleDisplay('botoes-pergunta', false);
    toggleDisplay('botoes-confirmacao', false);
    toggleDisplay('botoes-reiniciar', true);

    caminho = [];
    animalSugerido = null;
  });
}

function reiniciar() {
  document.querySelectorAll('img').forEach(img => img.remove());
  document.getElementById('mensagem').innerText = "Clique para começar!";
  toggleDisplay('botoes-pergunta', false);
  toggleDisplay('botoes-confirmacao', false);
  toggleDisplay('botoes-reiniciar', false);
  toggleDisplay('botoes-inicio', true);

  caminho = [];
  animalSugerido = null;
}


function toggleDisplay(id, mostrar) {
  document.getElementById(id).style.display = mostrar ? 'block' : 'none';
}

// Conectando botões aos handlers
document.getElementById('btn-iniciar').onclick = iniciarJogo;
document.getElementById('btn-sim').onclick = () => responder('sim');
document.getElementById('btn-nao').onclick = () => responder('não');
document.getElementById('btn-nao-sei').onclick = () => responder('não sei');
document.getElementById('btn-confirmar-sim').onclick = () => confirmar('sim');
document.getElementById('btn-confirmar-nao').onclick = () => confirmar('não');
document.getElementById('btn-nao-sei').onclick = () => responder('não sei');
document.getElementById('btn-reiniciar').onclick = reiniciar;
