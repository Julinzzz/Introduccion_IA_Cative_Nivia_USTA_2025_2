# Quiz – Mochila Fraccional (Greedy)
**Materia:** Introducción a IA  
**Autor:** Nivia Julian

## 1) Enunciado
Un aventurero tiene una mochila con **capacidad 50 kg**. Encuentra los objetos:

| Objeto | Peso (kg) | Valor (monedas) |
|:-----:|:---------:|:----------------:|
| A     | 10        | 60               |
| B     | 20        | 100              |
| C     | 30        | 120              |

**Pregunta:** ¿Qué combinación maximiza el valor sin exceder 50 kg usando un **algoritmo voraz (greedy)** para **mochila fraccional**?

---

## 2) Idea Greedy (Mochila Fraccional)
- Criterio: **densidad de valor** $ \text{densidad} = \frac{\text{valor}}{\text{peso}} $.
- Ordenar de mayor a menor densidad y **tomar completo** cada objeto; si el último no cabe, **tomar solo la fracción necesaria**.

Densidades:
- A: $60/10 = 6$
- B: $100/20 = 5$
- C: $120/30 = 4$

**Orden voraz:** A → B → C.

**Selección:**
- A completo (10 kg, 60) → quedan 40 kg  
- B completo (20 kg, 100) → quedan 20 kg  
- C fraccionado $20/30 = 2/3$ (20 kg, **80**)

**Resultado óptimo (fraccional):** $A + B + \tfrac{2}{3}\,\text{de } C$  
**Peso total:** 50 kg — **Valor total:** **240** monedas.

---

## 3) ¿Cuándo usar un algoritmo voraz?
Apropiado cuando la **mejor decisión local conduce al óptimo global** (propiedad de intercambio).  
Ejemplos típicos: **Mochila fraccional**, **árbol de expansión mínima** (Kruskal/Prim), **Huffman**, **selección de actividades**, **cambio de monedas** (en sistemas canónicos).

### Limitaciones
- **Mochila 0-1** (sin fracciones): **no** garantiza óptimo.  
- Múltiples restricciones o dependencias entre ítems → el criterio local puede fallar.  
- Decisiones **irrevocables**: un mal comienzo no se corrige.  
- Costos/valores **no lineales** o negativos rompen el criterio.

**Complejidad:** \(O(n \log n)\) por la ordenación.

---

## 4) Código básico (Python)

Guarda como `mochila_fraccional.py` y ejecútalo con `python mochila_fraccional.py`.

```python
# Nivia Julian - Quiz Mochila Fraccional (Greedy)
# ---------------------------------------------------------------
# Algoritmo voraz: ordena por valor/peso, toma completos y fracciona el último.
# Imprime (objeto, fracción, peso usado, valor aportado) y los totales.
# Complejidad: O(n log n). Válido para mochila fraccional.
# ---------------------------------------------------------------

# Datos: (nombre, peso, valor)
items = [("A", 10, 60), ("B", 20, 100), ("C", 30, 120)]
capacidad = 50

# Ordenar por densidad (valor/peso) desc
items = sorted(items, key=lambda x: x[2] / x[1], reverse=True)

valor_total = 0.0
seleccion = []
restante = capacidad

for nombre, peso, valor in items:
    if restante == 0:
        break
    if peso <= restante:
        seleccion.append((nombre, 1.0, peso, valor))
        valor_total += valor
        restante -= peso
    else:
        frac = restante / peso
        aporte = valor * frac
        seleccion.append((nombre, frac, restante, aporte))
        valor_total += aporte
        restante = 0

print("Selección (objeto, fracción, peso usado, valor):")
for nombre, frac, p, v in seleccion:
    print(f"{nombre}: {frac:.2f}  {p} kg  {v:.0f} monedas")

print(f"\nPeso total usado: {capacidad} kg")
print(f"Valor total: {valor_total:.0f} monedas")
```

---

## 5) Reflexión rápida
- Este greedy funciona porque **se permiten fracciones**.  
- Si los ítems fueran 0-1, necesitaríamos **DP / programación entera** para asegurar el óptimo.

---
