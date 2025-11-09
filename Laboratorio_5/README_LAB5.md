# **Práctica: Búsqueda Local, Algoritmos Voraces y Adversariales**

## **Asignatura:** Introducción a la Inteligencia Artificial  
**Universidad Santo Tomás — Facultad de Ingeniería Electrónica**  
**Semestre:** 2025-2  
**Docente:** Mg. Diego Alejandro Barragán Vargas  
**Autores:** Cristian Cative — Julián Nivia  

---

## **1. Punto 1 — Organización de Sillas (Búsqueda Local)**

### **Objetivo**
Visualizar cómo pequeñas modificaciones locales pueden mejorar o no una solución inicial, aplicando el método de **Hill Climbing**.

### **Descripción del problema**
Se dispone de **6 sillas** y **6 personas**, donde cada persona tiene una “satisfacción” asociada a con quién se sienta a su lado.  
El objetivo consiste en encontrar una disposición que **maximice la satisfacción total**, considerando una mesa circular (cada persona tiene dos vecinos).

Para resolverlo, se implementó un algoritmo de **búsqueda local (Hill Climbing)**, donde en cada iteración se intercambian (swap) exactamente **dos personas** por turno. Se evalúa la ganancia de satisfacción y se acepta el cambio únicamente si mejora la solución actual.

### **Estrategia aplicada**
1. Se genera una disposición inicial aleatoria.  
2. Se calcula la satisfacción total del grupo.  
3. Se generan todos los posibles intercambios de dos personas.  
4. Se elige el intercambio que produzca la mayor mejora (best-ascent) o la primera mejora (first-ascent).  
5. El proceso continúa hasta alcanzar un óptimo local.  
6. Se puede utilizar un esquema de **reinicios aleatorios (random restarts)** para escapar de óptimos locales.

### **Código**
El siguiente fragmento ilustra la implementación en Python:

```python
def hill_climbing(inicial=None, modo="mejor", max_iter=500):
    if inicial is None:
        actual = PERSONAS.copy()
        random.shuffle(actual)
    valor = satisfaccion_total(actual)

    for _ in range(max_iter):
        vecinos = mejores_vecinos_swap(actual)
        if not vecinos or vecinos[0][2] <= 0:
            return actual, valor
        i, j, ganancia = vecinos[0]
        actual[i], actual[j] = actual[j], actual[i]
        valor += ganancia
    return actual, valor
```

### **Conclusión**
El método de Hill Climbing permite aproximarse a soluciones de alta calidad sin explorar todo el espacio de búsqueda. Sin embargo, puede quedar atrapado en **óptimos locales**, por lo que técnicas complementarias como **random restarts** o **simulated annealing** pueden ser útiles para mejorar el resultado global.

---

## **2. Punto 2 — Problema del Cambio de Monedas (Algoritmo Voraz)**

### **Objetivo**
Introducir el concepto de **decisión secuencial y equilibrio local** mediante un algoritmo **voraz (greedy)** que toma siempre la mejor decisión disponible en el momento.

### **Descripción del problema**
Se requiere entregar cambio por un valor de **$63**, utilizando monedas de denominaciones **50, 20, 10, 5 y 1**.  
El algoritmo debe seleccionar en cada paso la **moneda de mayor valor posible** que no exceda la cantidad restante.

### **Estrategia aplicada**
1. Ordenar las monedas en forma descendente.  
2. Dividir el monto restante por el valor de la moneda actual.  
3. Registrar cuántas monedas de ese tipo se usan.  
4. Continuar con las siguientes denominaciones hasta alcanzar el monto exacto.  

### **Código**
```python
def cambio_voraz(monto, monedas):
    monedas = sorted(monedas, reverse=True)
    uso = {m: 0 for m in monedas}
    restante = monto
    for m in monedas:
        cnt, restante = divmod(restante, m)
        uso[m] = cnt
    return uso
```

### **Ejemplo de ejecución**
Para un monto de **$63** con monedas [50, 20, 10, 5, 1]:

| Denominación | Cantidad | Total Parcial |
|---------------|-----------|----------------|
| 50 | 1 | 50 |
| 10 | 1 | 60 |
| 1  | 3 | 63 |

**Total:** 5 monedas.  
El algoritmo voraz encuentra una solución óptima, aunque no siempre garantiza optimalidad en sistemas no canónicos de monedas.

### **Conclusión**
El enfoque voraz permite obtener resultados rápidos y eficientes en problemas donde la estructura del sistema garantiza que la elección local óptima conduce a la solución global. Sin embargo, su aplicabilidad debe analizarse en función del tipo de sistema de denominaciones.

---

## **3. Punto 3 — Juego de Piedra, Papel o Tijera (Algoritmos Adversariales)**

### **Objetivo**
Evidenciar cómo la estrategia “siempre tomar lo mejor ahora” no necesariamente conduce a una solución óptima, e introducir el concepto de **equilibrio adversarial y estrategias mixtas**.

### **Descripción del problema**
El juego de **Piedra–Papel–Tijera** se modela como un **juego de suma cero** entre dos agentes racionales.  
Cada jugador puede elegir entre tres acciones, y la utilidad depende del enfrentamiento.  
Si ambos jugadores son racionales, el equilibrio óptimo (Nash) consiste en jugar **cada acción con probabilidad 1/3**.

### **Estrategia aplicada**
1. Se define la matriz de pagos del juego desde la perspectiva de un jugador.  
2. Se calcula la utilidad esperada frente a las probabilidades del oponente.  
3. Si el oponente juega racionalmente (1/3 cada opción), no existe una acción determinista mejor; la política óptima es **aleatoria uniforme**.

### **Código**
```python
PAGA = {
    "piedra": {"piedra":0, "papel":-1, "tijera":1},
    "papel": {"piedra":1, "papel":0, "tijera":-1},
    "tijera": {"piedra":-1, "papel":1, "tijera":0},
}

def mejor_respuesta(freq_opp):
    mejor, val_mejor = None, float("-inf")
    for a in ACCIONES:
        u = sum(PAGA[a][b] * freq_opp.get(b,0.0) for b in ACCIONES)
        if u > val_mejor:
            mejor, val_mejor = a, u
    return mejor
```

### **Conclusión**
El juego demuestra que en entornos adversariales, la mejor decisión no depende únicamente del valor inmediato, sino del comportamiento del oponente.  
El equilibrio de Nash en estrategias mixtas representa la **condición de estabilidad** donde ninguna de las partes puede mejorar su resultado unilateralmente.  
Este principio es fundamental en la **búsqueda adversarial**, aplicada en dominios como los juegos, la teoría de decisiones y la planificación estratégica.

---

## **Conclusión General**
Los tres ejercicios permiten comprender distintos enfoques de la toma de decisiones en Inteligencia Artificial:

| Tipo de algoritmo | Principio | Ejemplo aplicado | Riesgo principal |
|--------------------|------------|------------------|------------------|
| **Búsqueda Local (Hill Climbing)** | Mejora iterativa por cambios locales | Organización de sillas | Óptimos locales |
| **Voraz (Greedy)** | Selección de la mejor opción inmediata | Cambio de monedas | Falta de globalidad |
| **Adversarial (Minimax / Nash)** | Decisión en entornos competitivos | Piedra–Papel–Tijera | Equilibrios inestables o mixtos |

Cada técnica ilustra una forma de razonamiento autónomo y constituye la base para el estudio posterior de **metaheurísticas**, **aprendizaje por refuerzo** y **planificación multiagente** en IA.

