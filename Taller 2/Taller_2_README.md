
# Taller de Introducción a la IA — **Evolución Pokémon, Recomendador tipo Spotify y Controlador de Robot de Carreras**

**Autor:** Julián Yesid Nivia Méndez  
**Curso:** Introducción a la Inteligencia Artificial  
**Lenguaje:** Python 3.x

---

## 📦 Contenido del repositorio

- [`Punto_1.py`](sandbox:/mnt/data/Punto_1.py): **Algoritmo Genético (GA)** para evolucionar Pokémon (5 genes: `ataque`, `defensa`, `velocidad`, `vida`, `tipo`).
- [`Punto_2.py`](sandbox:/mnt/data/Punto_2.py): **Colonia de Hormigas (ACO)** para generar una playlist tipo Spotify (nodos=canciones, aristas=similitudes).
- [`Punto_3.py`](sandbox:/mnt/data/Punto_3.py): **Controlador híbrido** para un robot de carreras (GA + ACO + PSO).

> Todos los scripts son autocontenidos y fijan semillas para reproducibilidad.

---

## 🛠 Requisitos mínimos

- Python 3.8+  
- Paquetes estándar de la librería estándar. Para `Punto_1.py` (gráfica) se usa `matplotlib`:
  ```bash
  pip install matplotlib
  ```

---

# 1) **Punto 1 — Evolución de Pokémon con GA**

### 1.1. Representación
Cada Pokémon es un cromosoma con 5 genes:
- Continuos en \[0,1]: `ataque`, `defensa`, `velocidad`, `vida`  
- Categórico: `tipo ∈ {fuego, agua, planta, electrico, roca, hielo, lucha, fantasma}`

### 1.2. Fitness (resumen)
\[\n\text{fitness} = (0.30\,\text{ataque} + 0.20\,\text{defensa} + 0.25\,\text{velocidad} + 0.25\,\text{vida}) \times \text{BonoTipo} \times \text{Sinergias}\n\]

- **BonoTipo** (ej.): `fuego=1.10`, `electrico=1.07`, …  
- **Sinergias**: +3% si ataque y velocidad > 0.7 (atacante rápido), +2% si defensa y vida > 0.7 (tanque), −3% si vida<0.25 (frágil).

### 1.3. GA
- Inicialización aleatoria, **selección por torneo**, **crossover blend**, **mutación gaussiana**, **elitismo**.
- Hiperparámetros clave (en el script):
  - `POBLACION=80`, `GENERACIONES=60`, `ELITISMO=4`, `TAM_TORNEO=3`,
  - `PROB_MUTACION=0.20`, `SIGMA_MUT=0.10`, `PROB_MUT_TIPO=0.10`.

### 1.4. Ejecución
```bash
python Punto_1.py
```
El script imprime el mejor individuo y muestra la **curva de fitness** (mejor y promedio).

### 1.5. Qué reportar
- Tabla con hiperparámetros y su efecto (p. ej., aumentar `SIGMA_MUT` acelera exploración pero puede inestabilizar).  
- Captura de la curva de evolución y el mejor Pokémon encontrado (stats + tipo).

---

# 2) **Punto 2 — Playlist con ACO**

### 2.1. Datos simulados
12 canciones con rasgos: `genres` (conjunto), `energy`, `valence`, `dance`, `acoustic` y `tempo` (BPM).

### 2.2. Similitud y afinidad
- **Similitud canción–canción**: combinación 50/50 de **Jaccard**(géneros) y **coseno**(vector de rasgos normalizados).  
- **Afinidad usuario–canción**: promedio de pesos por género + cercanía gaussiana a `targets` del usuario (energy, valence, dance, acoustic, tempo). Resultado en \[0,1].

### 2.3. ACO
- Transición proporcional a `τ^α · η^β · afinidad^γ`.  
- Parámetros por defecto: `ants=24`, `iters=60`, `playlist_len=6`, `alpha=1.0`, `beta=2.2`, `gamma=2.0`, `rho=0.20`, `Q=2.5`.
- Evaporación y depósito refuerzan aristas (pares de canciones) que participan en playlists con buen score.

### 2.4. Métrica de calidad de la playlist
\[\n\text{score} = 0.5\,\text{user\_match} + 0.4\,\text{coherence} + 0.1\,\text{diversity}\n\]
- `user_match`: afinidad promedio con el usuario.  
- `coherence`: similitud media entre canciones consecutivas.  
- `diversity`: 1 − similitud media de todos los pares de la lista.

### 2.5. Ejecución
```bash
python Punto_2.py
```
Imprime la mejor playlist, su **puntaje total** y el desglose de métricas.

### 2.6. Sugerencias de experimento
- Cambia `start_mode` a `"random"` para exigir más exploración.  
- Aumenta `gamma` si quieres playlists más personalizadas (mayor peso a afinidad del usuario).

---

# 3) **Punto 3 — Controlador de Robot de Carreras (GA + ACO + PSO)**

### 3.1. Modelo
- **Pista:** `N_SEG` tramos con `curva∈[0,1]` y `largo` (m).  
- **Líneas (carriles):** `LANES=3` → `0=interior`, `1=ideal`, `2=exterior`.  
- **Controlador (3 genes en [0,1]):** `agresividad`, `conservador`, `adelantamiento`.  
- **Oponentes:** prob. de aparición por tramo `DT_OPP`; cuando aparece, limitan velocidad en ese tramo.

### 3.2. Dinámica simplificada
Límite de velocidad por tramo:
\[\n v_{\max} = V_{MAX\_BASE} \cdot (1 - 0.72\,\text{curva}) \cdot (1 + \text{lane\_factor}) \cdot \big( 1 + 0.35\,a - 0.30\,c \big) \n\]
- `lane_factor`: interior −0.05, ideal 0, exterior +0.05.  
- Efecto de **PSO** en sobrepaso: decide `shift` (cambio de carril) y `pace` (empuje) que reducen el tiempo en el tramo afectado por oponente, con una penalización (riesgo) dependiente de la curvatura, el cambio de carril y el estilo del conductor.  
- **ACO** aprende la secuencia de carriles (línea de carrera) por tramo.  
- **GA** evoluciona los 3 parámetros del controlador evaluando el tiempo de vuelta promedio (fitness = −tiempo).

### 3.3. Parámetros en el script actual (`Punto_3.py`)
- `N_SEG=5`, `LANES=3`, `V_MAX_BASE=69.0`, `DT_OPP=0.15`, `N_OPP_SAMPLES=2`.  
- **PSO:** `particles=18`, `iters=22`.  
- **ACO:** `ants=18`, `iters=18`, `evap=0.25`, `Q=150.0`.  
- **GA:** `pop=28`, `gens=18`, `elite=2`, `p_mut=0.25`, `sigma=0.18`, `torneo=3`.

### 3.4. Ejecución
```bash
python Punto_3.py
```
Imprime por generación el mejor **tiempo de vuelta** y el **promedio**, y al final el mejor controlador.

---

## 🔧 Cómo **reducir el tiempo de la carrera** (mejorar el *lap time*)

> Afecta la **calidad** del controlador/línea, no el tiempo de cómputo.

1) **Aumenta el techo de velocidad y la osadía del piloto**  
   En `Punto_3.py`:
   ```python
   V_MAX_BASE = 75.0   # antes 69.0
   # y/o ajustar el estilo del controlador con el GA o fijar un sesgo:
   style = 1.0 + 0.40*ctrl.agresividad - 0.25*ctrl.conservador
   ```
   *Efecto:* más velocidad en rectas/curvas, menor tiempo por tramo.

2) **Mejora la línea de carrera (ACO)**  
   - Aumenta el peso de heurística para premiar tramos rápidos:
     ```python
     ACOConfig(beta=2.5, Q=180.0, evap=0.20)
     ```
   - Con `LANES=3`, el **exterior** en curvas cerradas aumenta el radio y permite mayor velocidad; el ACO lo aprenderá más rápido con mayor `beta`.

3) **Optimiza mejor los sobrepasos (PSO)**  
   - Permite más exploración local:
     ```python
     PSOConfig(particles=24, iters=28, c1=1.7, c2=1.7, w=0.50)
     ```
   - Aumenta el impacto del empuje en el tramo (en el evaluador del PSO):
     ```python
     pace_gain = (0.10 + 0.28*ctrl.adelantamiento) * pace * (1.0 - 0.5*seg.curva)
     ```
   - Si el tráfico es alto (`DT_OPP` grande), sube `adelantamiento` del controlador o su peso en el GA.

4) **Reduce penalizaciones conservadoras** (si tu rúbrica lo permite)  
   - En el costo del PSO, baja la penalización por riesgo:
     ```python
     penalty = 0.28 * risk    # antes 0.35
     ```
   - En `lane_factor`, considera un exterior ligeramente más beneficioso:
     ```python
     def lane_factor(lane):
         return {-0.04, 0.00, +0.06}[lane]
     ```

5) **Menos tráfico** (escenario más “limpio”):  
   ```python
   DT_OPP = 0.10  # probabilidad de oponente por tramo
   ```
   *Efecto:* menos tramos limitados por rivales → vuelta más rápida.

> **Sugerencia:** ejecuta 3–5 corridas con semillas distintas y reporta el **promedio** y la **mejor** para una comparación justa entre configuraciones.

---

## ⚡ Cómo **acelerar la ejecución** (menos tiempo de cómputo)

- **Bajar complejidad por técnica:**
  - GA: `pop` y `gens` más pequeños (p. ej., 10×6).  
  - ACO: reducir `ants` e `iters` (p. ej., 8×8).  
  - PSO: menos `particles` e `iters` (p. ej., 8×8).
- **Menos segmentos:** `N_SEG=28` → `N_SEG=16` (o en tu script ya está en 5 para pruebas).  
- **Menos muestras de oponentes:** `N_OPP_SAMPLES=1`.  
- **Regla práctica:** start con un **perfil FAST** para prototipar y luego sube progresivamente la fidelidad.

---

## 🧪 Guía de experimentos y reporte

1. **Diseño experimental**  
   - Define 2–3 configuraciones (Baseline, FAST, Exploit) y fija semillas.  
   - Para cada una: ejecuta 5 corridas y reporta `promedio ± DE` del tiempo de vuelta.

2. **Qué subir al informe**  
   - **Punto 1:** curva de fitness + mejor Pokémon (JSON/tabla).  
   - **Punto 2:** mejor playlist, métricas y breve análisis de transición (qué géneros predominan y por qué).  
   - **Punto 3:** tabla de hiperparámetros, evolución de mejor/promedio por generación, mejor controlador (`agresividad`, `conservador`, `adelantamiento`) y una explicación de la línea de carrera aprendida (interior/ideal/exterior por tramos con 2–3 capturas de ejemplo o una lista resumida).

3. **Buenas prácticas**  
   - Usa control de versiones (commits por experimento).  
   - Deja comentado en los scripts qué cambiaste y por qué.  
   - Mantén las **semillas** para reproducibilidad.

---

## 🧾 Créditos y licencia

Este material es para fines **académicos** en la asignatura *Introducción a la IA*. Se autoriza su reutilización citando al autor y la materia.

---

### Anexo — Mapas de variables útiles (Punto 3)
- **Tiempo por tramo (sin rival):** `t = largo / vmax_segmento(...)`  
- **Penalización por riesgo (PSO):** `penalty = 0.35 * risk`  
- **Riesgo:** depende de `curva`, `shift`, `pace`, `agresividad`, `conservador`.  
- **Línea de carrera (ACO):** feromonas `tau[seg][lane]`, heurística `1/t`.  
- **Fitness del GA:** `- tiempo_de_vuelta_promedio`.

Si necesitas que deje **dos perfiles listos** en el código (FAST y FULL) con un `switch`, lo agrego directamente.
