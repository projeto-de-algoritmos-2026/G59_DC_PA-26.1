# 📚🐱 Estante — Recomendação por Contagem de Inversões

## Aluno

| Nome | Matrícula |
|------|-----------|
| Leticia de Carvalho dos Santos | 222022135 |

## Apresentação

🎥 [Vídeo de apresentação](https://www.youtube.com/link-aqui)

---
## Como funciona

1. Você ordena 10 livros do favorito ao menos favorito
2. O algoritmo compara seu ranking com 5 perfis fictícios usando **contagem de inversões** (O(n log n) via Merge Sort)
3. Menos inversões = gosto mais parecido
4. Um **grafo de afinidade** é montado com NetworkX mostrando a distância entre todos os perfis
5. O perfil mais próximo de você recomenda livros que você ainda não leu

## Instalação

```bash
pip install fastapi uvicorn networkx
```

## Rodando

**Terminal 1 — Backend:**
```bash
cd estante
python main.py
```
> API disponível em http://localhost:8000
> Docs automáticas em http://localhost:8000/docs

**Terminal 2 — Frontend:**
Abra o arquivo `index.html` direto no navegador (duplo clique), ou:
```bash
python -m http.server 3000
# acesse http://localhost:3000
```

## Estrutura

```
estante/
├── main.py       # FastAPI: algoritmos + endpoints
└── index.html    # Frontend: drag-and-drop + grafo SVG
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /books | Lista os 10 livros base |
| POST | /analyze | Recebe ranking, retorna afinidades + grafo + recomendações |

## Algoritmo

A contagem de inversões compara dois rankings assim:
- Dado o ranking do usuário [A, B, C] e um perfil [B, A, C]
- O par (A, B) está invertido → 1 inversão
- Normalizado: `similaridade = 1 - inversões / inversões_máximas`
- Máximo de inversões para n elementos: `n*(n-1)/2`
