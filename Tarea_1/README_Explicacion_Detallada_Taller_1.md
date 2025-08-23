# Tarea 1 – Inteligencia Artificial
**Conceptos:** Estado, Espacio de Estados, Acciones, Recompensa y Ambiente

Este taller parte de un código base (entregado por el docente) y lo evoluciona en 4 pasos para incorporar:
1) costo energético por movimiento,
2) bloqueo de movimiento con batería 0,
3) sistema de recompensas/castigos más rico y correcto (solo una vez al alcanzar objetivo),
4) estrategia de movimiento “mixta” que prioriza llegar al objetivo y luego maximiza puntos recargando.

---

## Estructura

```
Tarea_1/
├── Cative_Nivia_Tarea_1.py
└── README.md  ← este archivo
```

---

## Código original (docente) – resumen

Puntos clave:
- Mueve el robot en una grilla 3x3.
- Recompensa simple: **+5** por `recargar`, **+10** cuando `objetivo_alcanzado=True`, **−1** por moverse.
- Simulación con acciones **aleatorias**.
- La batería **no** se descuenta al moverse (solo `recargar` la pone en 100).
- La recompensa por “objetivo alcanzado” se evalúa **cada paso** si ya está en el objetivo.

```python
def recompensa(accion, nuevo_estado):
    if accion == "recargar":
        return 5
    elif nuevo_estado["objetivo_alcanzado"]:
        return 10
    elif accion in ["adelante","atras","izquierda","derecha"]:
        return -1
    else:
        return 0
```

---

## Código realizado (nuestra versión) – visión general

### Cambios globales
- Introducimos `COSTO_MOVIMIENTO = 10`.
- `mover_robot` descuenta batería **solo** en acciones de movimiento.
- **Paso 2:** si batería llega a **0**, el robot **no se mueve** (solo puede recargar).
- **Paso 3:** la **recompensa es aditiva** y premia el **momento de llegada** (solo una vez), comparando `estado_anterior` vs `nuevo_estado`.
- **Paso 4:** estrategia **mixta**: si batería ≤ umbral → `recargar`; si no, moverse a `(2,2)`; al llegar, **recargar infinito**.

---

## Paso a Paso de los cambios

### Paso 1 — Costo de movimiento
**Objetivo:** cada movimiento reduce la batería.

**Código clave:**
```python
COSTO_MOVIMIENTO = 10

if accion in ["adelante","atras","izquierda","derecha"]:
    estado["bateria"] = max(0, estado["bateria"] - COSTO_MOVIMIENTO)
```

**Motivación:** reflejar costo energético realista.

---

### Paso 2 — Bloqueo con batería 0
**Objetivo:** sin energía no hay movimiento (solo recarga).

**Código clave:**
```python
movimientos = ["adelante","atras","izquierda","derecha"]
if accion in movimientos and estado["bateria"] <= 0:
    print("Intento de moverse sin batería: acción ignorada")
    return estado
```

**Motivación:** coherencia con la física del sistema.

---

### Paso 3 — Recompensas/castigos (5+ reglas) y “objetivo alcanzado” una sola vez
**Objetivo:** enriquecer el sistema de recompensas y premiar la llegada solo en el instante en que ocurre.

**Código clave (aditivo + detección de llegada):**
```python
def recompensa(accion, estado_anterior, nuevo_estado, paso_actual, total_pasos):
    r = 0
    movs = ["adelante","atras","izquierda","derecha"]

    if accion == "recargar":
        r += 5
    if accion in movs:
        r += -1
    if accion in movs and nuevo_estado["bateria"] <= 0:
        r += -5

    if (not estado_anterior["objetivo_alcanzado"]) and nuevo_estado["objetivo_alcanzado"]:
        r += 10
        if paso_actual < 5:
            r += 20

    if (paso_actual > total_pasos // 2) and (not nuevo_estado["objetivo_alcanzado"]):
        r += -2

    return r
```

**Motivación:**
- Evitar premiar repetidamente por “estar” en el objetivo.
- Modelar eficiencia (llegada rápida) y penalizar la tardanza.

---

### Paso 4 — Estrategia (mixta + recarga infinita al llegar)
**Objetivo:** maximizar puntos usando una política simple.

**Código clave:**
```python
def estrategia_mixta(estado):
    x, y = estado["posicion"]

    if estado["objetivo_alcanzado"]:
        return "recargar"

    if estado["bateria"] <= 10:
        return "recargar"

    if x < 2:
        return "adelante"
    elif y < 2:
        return "derecha"
    else:
        return "recargar"
```

**Motivación:** capturar el bonus de llegada y luego capitalizar con +5 por recarga.

---

## Reglas de recompensa (resumen)

| Regla                                             | Valor  | Cuándo aplica                                     |
|---------------------------------------------------|--------|----------------------------------------------------|
| Recargar                                          | +5     | Acción = `recargar`                               |
| Costo por moverse                                 | −1     | Acción ∈ {adelante, atrás, izquierda, derecha}    |
| Intento de moverse con batería 0                  | −5     | Acción de movimiento y batería ≤ 0                 |
| Alcanzar el objetivo (solo una vez)               | +10    | Transición `False → True` en `objetivo_alcanzado` |
| Bonus por llegada rápida                          | +20    | Cuando se alcanza objetivo y `paso_actual < 5`     |
| Tardanza sin llegar (tras mitad de los pasos)     | −2     | Si `paso_actual > total_pasos//2` y no llegó       |

---

## Estrategia “mixta”

- Si ya llegó al objetivo → `recargar` (maximiza puntos).
- Si batería ≤ 10 → `recargar`.
- Si batería suficiente → moverse hacia `(2,2)` priorizando `x` y luego `y`.

Razonamiento: balance entre llegar pronto (capturar bonus) y no quedarse sin energía; luego capitalizar con recargas.

---

## Cómo correr el código (paso a paso)

1. Abrir PowerShell o CMD.
2. Ir a la carpeta raíz del repositorio (ajusta la ruta a la tuya):
   ```powershell
   cd "C:\Users\PC\OneDrive\Documents\Universidad Santo Tomas\Semestre 8 - 2025 1\Intro IA\Corte 1"
   ```
3. Asegurar que el archivo existe en `Tarea_1\Cative_Nivia_Tarea_1.py`.
4. Ejecutar el script:
   ```powershell
   python .\Tarea_1\Cative_Nivia_Tarea_1.py
   ```
   Si tienes varias versiones de Python instaladas, prueba con:
   ```powershell
   py -3.13 .\Tarea_1\Cative_Nivia_Tarea_1.py
   ```
5. Verificar la salida en consola: pasos, acciones, estado y recompensa total.
6. (Opcional) Para empezar la simulación con batería 100:
   ```python
   estado = {"posicion": (0, 0), "bateria": 100, "objetivo_alcanzado": False}
   # o
   estado = estado_robot.copy()
   ```

---

## Trazabilidad / commits

```bash
git add Tarea_1/Cative_Nivia_Tarea_1.py
git commit -m "estado inicial, codigo entregado por el docente"
git push origin main

git add Tarea_1/Cative_Nivia_Tarea_1.py
git commit -m "eestado inicial (Con Codigo)"
git push origin main

git add Tarea_1/Cative_Nivia_Tarea_1.py
git commit -m "Paso 1: costo por movimiento (COSTO_MOVIMIENTO) y descuento de batería"
git push origin main

git commit -am "Paso 2: bloqueo de movimiento con batería 0"
git push origin main

git commit -am "Paso 3: recompensa aditiva; objetivo alcanzado solo una vez; bonus llegada rápida"
git push origin main

git commit -am "Fix: recompensa aditiva; incluye bonus de llegada rápida y costo de movimiento"
git push origin main

git commit -am "Paso 4: estrategia mixta y recarga infinita al llegar"
git push origin main

git add Tarea_1/README_Explicacion_Detallada_Taller_1.md
git commit -m "Docs: README del Taller 1 (pasos, comparaciones y estrategia)"
git push origin main
```
