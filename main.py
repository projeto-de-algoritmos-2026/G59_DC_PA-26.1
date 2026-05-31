from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import networkx as nx

app = FastAPI(title="Estante 🐱📚")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Os 10 livros base (devem ser os mesmos do frontend) ───────────────────────
COMMON_BOOKS = [
    "O Nome do Vento", "O Senhor dos Anéis", "O Caminho dos Reis",
    "O Vale das Bonecas", "O Hobbit", "Harry Potter",
    "O Bebê de Rosemary", "Orgulho e Preconceito", "IT - A Coisa", "Fahrenheit 451"
]

# ── Perfis fictícios ──────────────────────────────────────────────────────────
PROFILES = {
    "Luna": {
        "bio": "Ama fantasia épica e Stormlight Archive 🐱",
        "rankings": {
            "O Nome do Vento": 1, "O Senhor dos Anéis": 2, "O Caminho dos Reis": 3,
            "O Hobbit": 4, "Harry Potter": 5, "Fahrenheit 451": 6,
            "Orgulho e Preconceito": 7, "O Vale das Bonecas": 8,
            "IT - A Coisa": 9, "O Bebê de Rosemary": 10,
        },
        "extra_books": ["As Crônicas de Nárnia", "A Roda do Tempo", "Mistborn"],
    },
    "Theo": {
        "bio": "Distopias e ficção científica são sua vida",
        "rankings": {
            "Fahrenheit 451": 1, "IT - A Coisa": 2, "O Bebê de Rosemary": 3,
            "O Caminho dos Reis": 4, "O Nome do Vento": 5, "O Senhor dos Anéis": 6,
            "O Hobbit": 7, "Harry Potter": 8, "Orgulho e Preconceito": 9,
            "O Vale das Bonecas": 10,
        },
        "extra_books": ["Admirável Mundo Novo", "O Conto da Aia", "Jogos Vorazes"],
    },
    "Mia": {
        "bio": "Prefere aventura leve e mundos mágicos aconchegantes",
        "rankings": {
            "Harry Potter": 1, "O Hobbit": 2, "O Senhor dos Anéis": 3,
            "O Nome do Vento": 4, "O Caminho dos Reis": 5, "Orgulho e Preconceito": 6,
            "O Vale das Bonecas": 7, "Fahrenheit 451": 8,
            "O Bebê de Rosemary": 9, "IT - A Coisa": 10,
        },
        "extra_books": ["Percy Jackson", "A Bússola de Ouro", "Eragon"],
    },
    "Kaladin": {
        "bio": "Clássicos e fantasia épica densa",
        "rankings": {
            "Orgulho e Preconceito": 1, "O Vale das Bonecas": 2, "O Caminho dos Reis": 3,
            "O Senhor dos Anéis": 4, "O Nome do Vento": 5, "Fahrenheit 451": 6,
            "O Hobbit": 7, "Harry Potter": 8, "IT - A Coisa": 9,
            "O Bebê de Rosemary": 10,
        },
        "extra_books": ["Morro dos Ventos Uivantes", "O Sol é para Todos", "A Louca da Casa"],
    },
    "Iris": {
        "bio": "Suspense e terror — quanto mais assustador melhor",
        "rankings": {
            "IT - A Coisa": 1, "O Bebê de Rosemary": 2, "Fahrenheit 451": 3,
            "O Vale das Bonecas": 4, "Orgulho e Preconceito": 5, "Harry Potter": 6,
            "O Hobbit": 7, "O Senhor dos Anéis": 8, "O Nome do Vento": 9,
            "O Caminho dos Reis": 10,
        },
        "extra_books": ["O Iluminado", "A Paciente Silenciosa", "Um Estudo em Vermelho"],
    },
}


# ── Algoritmos ────────────────────────────────────────────────────────────────
def count_inversions(arr: List[int]) -> int:
    """Merge sort para contar inversões em O(n log n)."""
    if len(arr) <= 1:
        return 0
    mid = len(arr) // 2
    left, right = arr[:mid], arr[mid:]

    def merge_count(left, right):
        result, inv = [], 0
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
                inv += len(left) - i
        result += left[i:] + right[j:]
        return result, inv

    def sort_count(arr):
        if len(arr) <= 1:
            return arr, 0
        mid = len(arr) // 2
        l, lc = sort_count(arr[:mid])
        r, rc = sort_count(arr[mid:])
        merged, mc = merge_count(l, r)
        return merged, lc + rc + mc

    _, inversions = sort_count(arr)
    return inversions


def build_affinity_graph(user_ranking: Dict[str, int]) -> dict:
    """Compara ranking do usuário com perfis via inversões e monta grafo."""
    common = [b for b in COMMON_BOOKS if b in user_ranking]
    if not common:
        return {}

    user_order = [user_ranking[b] for b in common]
    results = {}

    for name, profile in PROFILES.items():
        profile_order = [profile["rankings"][b] for b in common]
        # Normaliza para índices relativos antes de contar inversões
        def to_relative(ranks):
            sorted_vals = sorted(range(len(ranks)), key=lambda i: ranks[i])
            rel = [0] * len(ranks)
            for pos, idx in enumerate(sorted_vals):
                rel[idx] = pos
            return rel

        u_rel = to_relative(user_order)
        p_rel = to_relative(profile_order)

        # Conta inversões: para cada posição do usuário, quantas estão fora de ordem vs perfil
        diff = [u_rel[i] - p_rel[i] for i in range(len(common))]
        inversions = count_inversions(u_rel[:])
        # Similaridade real: inversões entre a ordem do usuário reindexada pelo perfil
        reindexed = []
        p_sorted = sorted(range(len(common)), key=lambda i: p_rel[i])
        reindexed = [u_rel[i] for i in p_sorted]
        inversions = count_inversions(reindexed)

        max_inversions = len(common) * (len(common) - 1) // 2
        similarity = round(100 * (1 - inversions / max_inversions) if max_inversions > 0 else 100, 1)
        results[name] = {"inversions": inversions, "similarity": similarity, "bio": profile["bio"]}

    # Grafo com NetworkX
    G = nx.Graph()
    G.add_node("Você")
    for name, data in results.items():
        G.add_node(name)
        G.add_edge("Você", name, weight=data["similarity"], inversions=data["inversions"])

    # Arestas entre perfis
    for n1 in PROFILES:
        for n2 in PROFILES:
            if n1 >= n2:
                continue
            o1 = [PROFILES[n1]["rankings"][b] for b in common]
            o2 = [PROFILES[n2]["rankings"][b] for b in common]
            p_sorted2 = sorted(range(len(common)), key=lambda i: to_relative(o2)[i])
            reind = [to_relative(o1)[i] for i in p_sorted2]
            inv = count_inversions(reind)
            max_inv = len(common) * (len(common) - 1) // 2
            sim = round(100 * (1 - inv / max_inv) if max_inv > 0 else 100, 1)
            G.add_edge(n1, n2, weight=sim, inversions=inv)

    nodes = [{"id": n, "isUser": n == "Você"} for n in G.nodes()]
    edges = [{"source": u, "target": v, "weight": d["weight"], "inversions": d["inversions"]}
             for u, v, d in G.edges(data=True)]

    return {"nodes": nodes, "edges": edges, "similarities": results}


# ── Schemas ───────────────────────────────────────────────────────────────────
class RankingInput(BaseModel):
    rankings: Dict[str, int]  # {livro: posição}


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/books")
def get_books():
    return {"books": COMMON_BOOKS}


@app.post("/analyze")
def analyze(data: RankingInput):
    graph_data = build_affinity_graph(data.rankings)
    if not graph_data:
        return {"error": "Nenhum livro comum encontrado"}

    similarities = graph_data["similarities"]
    best_match = max(similarities, key=lambda k: similarities[k]["similarity"])
    best_profile = PROFILES[best_match]

    user_books = set(data.rankings.keys())
    recommendations = [b for b in best_profile["extra_books"] if b not in user_books]

    # Segundo melhor também recomenda
    sorted_profiles = sorted(similarities, key=lambda k: similarities[k]["similarity"], reverse=True)
    second_match = sorted_profiles[1] if len(sorted_profiles) > 1 else None
    if second_match:
        for b in PROFILES[second_match]["extra_books"]:
            if b not in user_books and b not in recommendations:
                recommendations.append(b)

    return {
        "graph": {"nodes": graph_data["nodes"], "edges": graph_data["edges"]},
        "similarities": similarities,
        "best_match": {"name": best_match, **similarities[best_match], "bio": best_profile["bio"]},
        "recommendations": recommendations[:6],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)