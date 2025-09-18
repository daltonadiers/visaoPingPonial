# 🏓 Visão Ping Ponial

Um sistema inteligente de **marcação de pontos em partidas de Ping Pong**, desenvolvido com **OpenCV** e técnicas de **Machine Learning/Deep Learning**.  
Nosso objetivo é resolver um problema recorrente: **esquecermos a pontuação durante o jogo**, o que gera discussões e perda de tempo.  

Este projeto busca automatizar a contagem de pontos através do **reconhecimento de gestos manuais** usando uma câmera, que identificará ações específicas dos jogadores e atualizará o placar em tempo real.

---

## 🎯 Motivação

Durante nossas partidas de ping pong, a contagem de pontos é feita manualmente, apenas em conversa. Isso frequentemente gera dúvidas, discussões e até reinícios de partida.  
A solução proposta combina **visão computacional** e **aprendizado de máquina** para criar um marcador inteligente, justo e confirmado por ambos os jogadores.

---

## 🔍 Abordagem

- Utilizaremos **OpenCV** aliado a técnicas de **Deep Learning** para reconhecimento de gestos manuais.  
- Cada gesto corresponderá a uma ação no placar:
  - ✋ ➕ **+1 ponto**
  - ✌️ ➕ **+2 pontos**
  - 👊 ➕ **+1 ponto e -1 ponto do adversário**
  - 🤟 ➕ **+2 pontos e -1 ponto do adversário**
  - ❌ ➖ **Retirada de pontos (em caso de erro)**  

- **Confirmação obrigatória:** sempre que um jogador informar um gesto, o adversário deve confirmar com um 👍 para que a pontuação seja validada.  
- O sistema rodará em um **servidor local** ou em uma **máquina dedicada**, exibindo o placar atualizado em tempo real.

---

## 🛠️ Tecnologias

- [Python](https://www.python.org/)  
- [OpenCV](https://opencv.org/)  
- [TensorFlow](https://www.tensorflow.org/) ou [PyTorch](https://pytorch.org/)  
- [CUDA](https://developer.nvidia.com/cuda-zone) (para aceleração em GPU)  

---

## 📌 Funcionalidades Planejadas

- [ ] Reconhecimento de gestos via câmera em tempo real  
- [ ] Definição de múltiplos gestos para diferentes regras do jogo  
- [ ] Sistema de confirmação por adversário  
- [ ] Interface para exibição do placar  
- [ ] Histórico da partida  

---

