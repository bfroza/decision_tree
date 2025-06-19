let caminho = [];
let animalSugerido = null;
let handUp = true // Corrigido

function iniciarJogo() {
  document.getElementById('botoes-inicio').style.display = 'none';
  document.getElementById('mensagem').innerText = 'Pensando...';
  setCharacterImage('up');
  handUp = false;

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
  })
  .catch(err => {
    document.getElementById('mensagem').innerText = 'Erro ao conectar com o servidor.';
    console.error(err);
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

    setCharacterImage(handUp ? 'up' : 'down');
    handUp = !handUp;

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
  })
  .catch(err => {
    document.getElementById('mensagem').innerText = 'Erro ao comunicar com o servidor.';
    console.error(err);
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

    if (resposta === 'sim') {
      setCharacterImage('opened');
    }

    if (dados.imagem) {
      const img = document.createElement('img');
      img.src = dados.imagem;
      img.alt = animalSugerido;
      img.style.maxWidth = '500px';
      img.id = 'img-animal';

      let container = document.getElementById('container-animal');
      if (!container) {
        container = document.createElement('div');
        container.id = 'container-animal';
        container.style.textAlign = 'center';
        container.style.marginTop = '20px';
        document.body.appendChild(container);
      }

      container.innerHTML = '';
      container.appendChild(img);
    }

    toggleDisplay('botoes-pergunta', false);
    toggleDisplay('botoes-confirmacao', false);
    toggleDisplay('botoes-reiniciar', true);

    caminho = [];
    animalSugerido = null;
  })
  .catch(err => {
    document.getElementById('mensagem').innerText = 'Erro ao confirmar resposta.';
    console.error(err);
  });
}

function reiniciar() {
  const imgAnimal = document.getElementById('img-animal');
  if (imgAnimal) imgAnimal.remove();
  
  document.getElementById('mensagem').innerText = "Clique para começar!";
  toggleDisplay('botoes-pergunta', false);
  toggleDisplay('botoes-confirmacao', false);
  toggleDisplay('botoes-reiniciar', false);
  toggleDisplay('botoes-inicio', true);
  const personagemDiv = document.querySelector('.character');
  const novaImagem = document.createElement('img');
  novaImagem.src = 'img/HandCrossed.png';
  novaImagem.alt = '';
  personagemDiv.appendChild(novaImagem);

  caminho = [];
  animalSugerido = null;
}

function toggleDisplay(id, mostrar) {
  document.getElementById(id).style.display = mostrar ? 'block' : 'none';
}

function setCharacterImage(state) {
  const imgCharacter = document.getElementById('imgCharacter');
  if (!imgCharacter) return;

  switch (state) {
    case 'up':
      imgCharacter.src = "img/HandUp.png";
      break;
    case 'down':
      imgCharacter.src = "img/HandDown.png";
      break;
    case 'opened':
      imgCharacter.src = "img/HandOpened.png";
      break;
    case 'crossed':
      imgCharacter.src = "img/HandCrossed.png";
    default:
      imgCharacter.src = "img/HandCrossed.png";
  }
}

// Conectando botões aos handlers
document.getElementById('btn-iniciar').onclick = iniciarJogo;
document.getElementById('btn-sim').onclick = () => responder('sim');
document.getElementById('btn-nao').onclick = () => responder('não');
document.getElementById('btn-nao-sei').onclick = () => responder('não sei');
document.getElementById('btn-confirmar-sim').onclick = () => confirmar('sim');
document.getElementById('btn-confirmar-nao').onclick = () => confirmar('não');
document.getElementById('btn-reiniciar').onclick = reiniciar;