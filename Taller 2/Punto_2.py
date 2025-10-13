"""
Segundo Punto — Recomendador tipo Spotify con Optimización por Colonia de Hormigas (ACO)

Descripción breve:
- Cada canción es un nodo en un grafo completo ponderado por "similitud musical".
- Un usuario-hormiga construye una playlist caminando por el grafo.
- La probabilidad de transición usa feromonas (aprendidas), heurística (similitud)
  y afinidad usuario-canción.
- El algoritmo itera con evaporación de feromonas y refuerzo por la calidad
  de las playlists construidas.
"""
from __future__ import annotations
import random, math, json, csv, os
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

# ------------------------------------------------------------
# 1) Datos simulados: 12 canciones con rasgos "estilo Spotify"
# ------------------------------------------------------------
# Rasgos numéricos están en [0,1] excepto tempo (BPM).
# Los géneros se representan como conjuntos (para similitud Jaccard).
CANCIONES: Dict[str, Dict] = {
    "song01": {"genres": {"rock","indie"},        "energy":0.82,"valence":0.55,"dance":0.58,"acoustic":0.10,"tempo":138},
    "song02": {"genres": {"pop"},                  "energy":0.66,"valence":0.80,"dance":0.78,"acoustic":0.15,"tempo":118},
    "song03": {"genres": {"jazz"},                 "energy":0.40,"valence":0.50,"dance":0.32,"acoustic":0.72,"tempo":96},
    "song04": {"genres": {"hiphop","latin"},       "energy":0.74,"valence":0.71,"dance":0.86,"acoustic":0.05,"tempo":102},
    "song05": {"genres": {"edm"},                  "energy":0.90,"valence":0.68,"dance":0.92,"acoustic":0.03,"tempo":128},
    "song06": {"genres": {"classical"},            "energy":0.20,"valence":0.35,"dance":0.10,"acoustic":0.95,"tempo":72},
    "song07": {"genres": {"metal","rock"},         "energy":0.95,"valence":0.40,"dance":0.45,"acoustic":0.02,"tempo":160},
    "song08": {"genres": {"latin","reggaeton"},    "energy":0.78,"valence":0.84,"dance":0.93,"acoustic":0.08,"tempo":98},
    "song09": {"genres": {"folk","indie"},         "energy":0.35,"valence":0.60,"dance":0.40,"acoustic":0.88,"tempo":110},
    "song10": {"genres": {"pop","edm"},            "energy":0.86,"valence":0.76,"dance":0.90,"acoustic":0.04,"tempo":124},
    "song11": {"genres": {"jazz","classical"},     "energy":0.30,"valence":0.42,"dance":0.22,"acoustic":0.90,"tempo":88},
    "song12": {"genres": {"rock","pop"},           "energy":0.70,"valence":0.72,"dance":0.75,"acoustic":0.12,"tempo":122},
}

# ------------------------------------------------------------
# 2) Preferencias del usuario (puedes editar)
# ------------------------------------------------------------
PREF_USUARIO = {
    "genre_weights": {  # afinidad por género (0-1)
        "rock":0.9, "pop":0.85, "indie":0.8, "latin":0.6, "reggaeton":0.55,
        "edm":0.7, "hiphop":0.55, "jazz":0.35, "classical":0.25, "metal":0.4, "folk":0.6
    },
    "targets": {        # valores preferidos
        "energy":0.75,
        "valence":0.70,
        "dance":0.82,
        "acoustic":0.10,
        "tempo":120    # BPM preferido
    },
    "tolerances": {     # tolerancias (cuanto más pequeño, mayor penalización por desviarse)
        "energy":0.25,
        "valence":0.30,
        "dance":0.25,
        "acoustic":0.20,
        "tempo":20.0   # BPM
    }
}

# ------------------------------------------------------------
# 3) Utilidades: similitudes y afinidades
# ------------------------------------------------------------
SONGS = list(CANCIONES.keys())
MIN_TEMPO = min(CANCIONES[s]["tempo"] for s in SONGS)
MAX_TEMPO = max(CANCIONES[s]["tempo"] for s in SONGS)

def norm_tempo(bpm: float) -> float:
    """Normaliza tempo a [0,1] con min-max global."""
    if MAX_TEMPO == MIN_TEMPO: return 0.5
    return (bpm - MIN_TEMPO) / (MAX_TEMPO - MIN_TEMPO)

def jaccard(a: set, b: set) -> float:
    """Similitud Jaccard para conjuntos (géneros)."""
    inter = len(a & b)
    union = len(a | b)
    return 0.0 if union == 0 else inter/union

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Similitud coseno para vectores cortos."""
    dot = sum(x*y for x,y in zip(vec1, vec2))
    n1  = math.sqrt(sum(x*x for x in vec1))
    n2  = math.sqrt(sum(y*y for y in vec2))
    if n1 == 0 or n2 == 0: return 0.0
    return dot/(n1*n2)

def features_vector(s: str) -> List[float]:
    """Vector de rasgos numéricos para similitud (tempo normalizado)."""
    c = CANCIONES[s]
    return [c["energy"], c["valence"], c["dance"], 1.0 - c["acoustic"], norm_tempo(c["tempo"])]

def song_similarity(a: str, b: str) -> float:
    """Similitud global canción-canción ∈ [0,1]."""
    ca, cb = CANCIONES[a], CANCIONES[b]
    sim_gen = jaccard(ca["genres"], cb["genres"])
    sim_feat= cosine_similarity(features_vector(a), features_vector(b))
    return 0.5*sim_gen + 0.5*sim_feat

def user_affinity(song: str) -> float:
    """Afinidad usuario-canción ∈ [0,1] basada en géneros y cercanía a targets."""
    c = CANCIONES[song]
    # afinidad por géneros (promedio de pesos presentes)
    if len(c["genres"]) == 0:
        ag = 0.0
    else:
        ag = sum(PREF_USUARIO["genre_weights"].get(g, 0.0) for g in c["genres"]) / len(c["genres"])
    # cercanía a targets (gaussiana por rasgo)
    closeness = 1.0
    for k in ["energy","valence","dance","acoustic"]:
        mu = PREF_USUARIO["targets"][k]
        tol= PREF_USUARIO["tolerances"][k]
        closeness *= math.exp(-((c[k]-mu)**2)/(2*tol*tol))
    # tempo (en BPM)
    mu_t = PREF_USUARIO["targets"]["tempo"]
    tol_t= PREF_USUARIO["tolerances"]["tempo"]
    closeness *= math.exp(-((c["tempo"]-mu_t)**2)/(2*tol_t*tol_t))
    # normalización heurística
    return max(0.0, min(1.0, 0.5*ag + 0.5*closeness))

# Precomputar matrices de similitud y afinidad
SIM: Dict[Tuple[str,str], float] = {}
for i in SONGS:
    for j in SONGS:
        if i == j:
            SIM[(i,j)] = 0.0
        else:
            SIM[(i,j)] = song_similarity(i,j)
AFFINITY: Dict[str, float] = {s: user_affinity(s) for s in SONGS}

# ------------------------------------------------------------
# 4) Modelo ACO (Colonia de Hormigas)
# ------------------------------------------------------------
@dataclass
class ACOConfig:
    seed: int = 7
    ants: int = 20
    iters: int = 50
    playlist_len: int = 6
    alpha: float = 1.0       # peso de feromonas
    beta: float = 2.0        # peso de heurística (similitud canción-canción)
    gamma: float = 2.0       # peso de afinidad usuario-canción
    rho: float = 0.25        # evaporación
    Q: float = 2.0           # depósito base de feromonas
    start_mode: str = "top_affinity"  # "top_affinity" | "random"

class Ant:
    def __init__(self, conf: ACOConfig):
        self.conf = conf
        self.playlist: List[str] = []

    def start_song(self) -> str:
        if self.conf.start_mode == "random":
            return random.choice(SONGS)
        # top afinidad (romper empates al azar)
        sorted_songs = sorted(SONGS, key=lambda s: AFFINITY[s], reverse=True)
        topk = sorted_songs[:max(3, len(sorted_songs)//4)]
        return random.choice(topk)

    def choose_next(self, current: str, pher: Dict[Tuple[str,str], float], visited: set) -> str | None:
        candidatos = [s for s in SONGS if s not in visited and s != current]
        if not candidatos: return None
        alpha, beta, gamma = self.conf.alpha, self.conf.beta, self.conf.gamma

        # prob de transición proporcional a tau^alpha * eta^beta * affinity^gamma
        scores = []
        for s in candidatos:
            tau = pher[(current, s)]
            eta = SIM[(current, s)]
            aff = AFFINITY[s]
            score = (tau**alpha) * (max(1e-6, eta)**beta) * (max(1e-6, aff)**gamma)
            scores.append(score)

        total = sum(scores)
        if total <= 0.0:
            return random.choice(candidatos)

        # ruleta
        r = random.random() * total
        acc = 0.0
        for s, sc in zip(candidatos, scores):
            acc += sc
            if acc >= r: return s
        return candidatos[-1]

# ------------------------------------------------------------
# 5) Métricas de calidad para la playlist
# ------------------------------------------------------------
def playlist_quality(playlist: List[str]) -> Tuple[float, Dict[str,float]]:
    """Retorna puntaje total y descomposición de métricas."""
    if len(playlist) <= 1:
        return 0.0, {"user_match":0.0,"coherence":0.0,"diversity":0.0}

    # user_match: promedio de afinidad individual
    user_match = sum(AFFINITY[s] for s in playlist) / len(playlist)

    # coherence: promedio de similitud entre consecutivas
    coh = 0.0
    for a, b in zip(playlist[:-1], playlist[1:]):
        coh += SIM[(a,b)]
    coherence = coh / (len(playlist)-1)

    # diversity: 1 - similitud media de todos los pares (busca evitar repetición)
    sims = []
    for i in range(len(playlist)):
        for j in range(i+1, len(playlist)):
            sims.append(SIM[(playlist[i], playlist[j])])
    diversity = 1.0 - (sum(sims)/len(sims))

    # combinación (ajusta pesos si quieres otra conducta)
    score = 0.5*user_match + 0.4*coherence + 0.1*diversity
    return score, {"user_match":user_match, "coherence":coherence, "diversity":diversity}

# ------------------------------------------------------------
# 6) Bucle principal ACO
# ------------------------------------------------------------
def run_aco(conf: ACOConfig):
    random.seed(conf.seed)

    # feromonas iniciales uniformes (pequeñas) en aristas dirigidas
    pher = {(i,j): 0.1 for i in SONGS for j in SONGS if i != j}

    best_playlist, best_score, best_metrics = [], -1.0, {}

    # logging
    history = []

    for it in range(conf.iters):
        ants_playlists: List[List[str]] = []
        ants_scores: List[float] = []

        # --- construir playlists
        for _ in range(conf.ants):
            ant = Ant(conf)
            current = ant.start_song()
            visited = {current}
            ant.playlist = [current]

            while len(ant.playlist) < conf.playlist_len:
                nxt = ant.choose_next(current, pher, visited)
                if nxt is None: break
                ant.playlist.append(nxt)
                visited.add(nxt)
                current = nxt

            score, _metrics = playlist_quality(ant.playlist)
            ants_playlists.append(ant.playlist)
            ants_scores.append(score)

            # registrar mejor global
            if score > best_score:
                best_score, best_metrics = score, _metrics
                best_playlist = ant.playlist[:]

        # --- evaporación
        for k in list(pher.keys()):
            pher[k] *= (1.0 - conf.rho)

        # --- depósito proporcional al score de cada hormiga (refuerzo de aristas usadas)
        for plist, score in zip(ants_playlists, ants_scores):
            if len(plist) < 2: continue
            deposit = conf.Q * max(0.0, score) / (len(plist)-1)
            for a,b in zip(plist[:-1], plist[1:]):
                pher[(a,b)] += deposit

        history.append((it, sum(ants_scores)/len(ants_scores), max(ants_scores)))

        # progreso en consola
        if (it % 5 == 0) or (it == conf.iters-1):
            print(f"Iter {it:02d} | promedio={history[-1][1]:.4f} | mejor_iter={history[-1][2]:.4f} | mejor_global={best_score:.4f}")

    return {
        "best_playlist": best_playlist,
        "best_score": best_score,
        "best_metrics": best_metrics,
        "pheromones": pher,
        "history": history
    }
# ------------------------------------------------------------
# 7) Ejecución de ejemplo
# ------------------------------------------------------------
if __name__ == "__main__":
    conf = ACOConfig(
        seed=25,
        ants=24,
        iters=60,
        playlist_len=6,
        alpha=1.0,
        beta=2.2,
        gamma=2.0,
        rho=0.20,
        Q=2.5,
        start_mode="top_affinity"  # o "random"
    )
    results = run_aco(conf)

    print("\nMejor playlist encontrada:")
    for i, s in enumerate(results["best_playlist"], 1):
        print(f" {i:02d}. {s:6s}  genres={CANCIONES[s]['genres']}  "
              f"energy={CANCIONES[s]['energy']:.2f}  dance={CANCIONES[s]['dance']:.2f}")

    print("\nPuntaje total:", round(results["best_score"], 4))
    print("Desglose métricas:", results["best_metrics"])