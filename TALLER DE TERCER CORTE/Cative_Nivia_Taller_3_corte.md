# Taller: Aprendizaje por refuerzo, Teorema de Bayes y algoritmos de IA

## 0. Contexto general

Este documento aborda tres temas clave dentro de la introducción a la inteligencia artificial:

1. El funcionamiento del **aprendizaje por refuerzo** (Reinforcement Learning, RL).
2. El uso del **teorema de Bayes** para construir un clasificador sencillo de correo spam.
3. Una exploración de los **algoritmos de IA más utilizados** actualmente en la academia y la industria.

---

## 1. Aprendizaje por refuerzo (Reinforcement Learning, RL)

El aprendizaje por refuerzo es un paradigma de aprendizaje automático en el que un **agente** aprende a tomar decisiones mediante **interacción directa con un entorno**.  
En lugar de recibir ejemplos “entrada–salida” ya etiquetados, el agente recibe **recompensas** (positivas o negativas) que indican qué tan buena fue una acción en un estado determinado, y con base en esa experiencia ajusta su estrategia de decisión.

Formalmente, muchos problemas de RL se modelan como un **proceso de decisión de Markov (MDP)** caracterizado por:

- Un conjunto de estados $S$.
- Un conjunto de acciones $A$.
- Una función de transición de estados $P(s' \mid s, a)$.
- Una función de recompensa $R(s, a)$.
- Un factor de descuento $\gamma \in [0,1]$ que pondera recompensas futuras.

El objetivo del agente es aprender una **política** $\pi(a \mid s)$ que maximice la recompensa acumulada esperada a largo plazo (retorno).

### 1.1 Componentes básicos de un problema de RL

En casi cualquier formulación de RL aparecen los siguientes elementos:

- **Agente**  
  Sistema de decisión que aprende (el algoritmo de RL).

- **Entorno (environment)**  
  Todo aquello con lo que interactúa el agente: simulador, robot físico, videojuego, proceso industrial, etc.

- **Estado ($s$)**  
  Información que describe la situación actual del entorno desde el punto de vista del agente  
  (por ejemplo: posición y velocidad de un robot, precios actuales en un sistema financiero, etc.).

- **Acción ($a$)**  
  Decisión que toma el agente en un estado concreto: mover un actuador, comprar/vender, acelerar/frenar, etc.

- **Recompensa inmediata ($r$)**  
  Señal escalar que indica qué tan buena fue la acción tomada en ese estado  
  (puede ser positiva, cero o negativa).

- **Política ($\pi$)**  
  Regla de decisión del agente: puede ser una tabla, una función matemática o una red neuronal que,
  dado un estado, selecciona una acción (determinista o probabilísticamente).

- **Función de valor ($V(s)$ o $Q(s,a)$)**  
  Estimación de “lo bueno” que es un estado (o un par estado–acción) en términos de la recompensa total futura esperada.

- **Modelo del entorno (opcional)**  
  Aproximación interna que el agente tiene de las dinámicas del entorno  
  ($\hat{P}(s' \mid s,a)$, $\hat{R}(s,a)$).  
  Si el agente usa un modelo explícito, se habla de **RL basado en modelo**.

- **Episodio**  
  Secuencia finita estado–acción–recompensa que comienza en un estado inicial y termina
  cuando se llega a un estado terminal (por ejemplo, fin de juego).

---

### 1.2 ¿Cómo puede un agente aprender decisiones óptimas en un entorno incierto? (Pregunta 1a)

En un entorno incierto, el agente **no conoce a priori** las consecuencias exactas de sus acciones. El aprendizaje por refuerzo permite que el agente mejore su comportamiento mediante un ciclo continuo de **prueba y error**:

1. El agente observa el estado actual $s_t$ del entorno.
2. La política $\pi$ del agente selecciona una acción $a_t$  
   (por ejemplo, siguiendo una estrategia de exploración/explotación como $\epsilon$-greedy).
3. El entorno responde:
   - Cambia a un nuevo estado $s_{t+1}$.
   - Entrega una recompensa $r_t$.
4. El agente **actualiza sus estimaciones** internas (por ejemplo, la función de valor $Q(s,a)$ o los parámetros de su política $\theta$) usando el cuádruple $(s_t, a_t, r_t, s_{t+1})$.
5. El ciclo continúa hasta completar un episodio; luego se repiten muchos episodios.

La idea clave es que el agente busca maximizar el **retorno esperado**:

$$
G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k+1}
$$

donde $\gamma \in [0,1)$ es el factor de descuento.  
Durante el aprendizaje, el agente ajusta su política para que las secuencias de acciones produzcan valores de $G_t$ cada vez mayores.

El carácter **incierto** del entorno (ruido, transiciones probabilísticas, recompensas variables) se maneja mediante:

- Uso de **expectativas** y promedios sobre múltiples episodios.
- Estrategias de **exploración** para recopilar información (no solo explotar lo ya conocido).
- Algoritmos de **actualización incremental** (por ejemplo, métodos de diferencias temporales).

De esta forma, sin conocer exactamente las probabilidades del entorno, el agente converge —bajo ciertas condiciones— a una política cercana a la óptima.

---

### 1.3 Tipos de algoritmos de aprendizaje por refuerzo y sus arquitecturas (Pregunta 1b)

La clasificación más habitual distingue varios ejes:

- **Con modelo (model-based) vs sin modelo (model-free).**
- **Basados en valores (value-based) vs basados en políticas (policy-based) vs actor–critic.**
- **On-policy vs off-policy.**
- **Tabulares vs con aproximación de funciones (por ejemplo, redes neuronales).**

A continuación se describe cada grupo junto con sus elementos y arquitectura general.

#### 1.3.1 RL basado en modelo vs RL sin modelo

1. **Algoritmos basados en modelo (model-based RL)**  
   - El agente **aprende o dispone** de un modelo explícito del entorno:  
     $\hat{P}(s' \mid s,a)$ y $\hat{R}(s,a)$.
   - Con ese modelo puede **planear**: simular trayectorias, evaluar políticas y mejorar su estrategia
     sin interactuar directamente con el entorno real.
   - Ejemplos:  
     - Métodos de **programación dinámica** (Value Iteration, Policy Iteration).  
     - Enfoques tipo **Dyna**, donde se combinan experiencias reales con simuladas.
     - Algoritmos inspirados en **AlphaZero**, que usan búsqueda tipo Monte Carlo Tree Search.

2. **Algoritmos sin modelo (model-free RL)**  
   - El agente **no aprende explícitamente** un modelo de las transiciones.
   - Aprende directamente una función de valor o una política a partir de la experiencia.
   - Ejemplos: Q-learning, SARSA, Deep Q-Network (DQN), métodos de gradiente de políticas, PPO, DDPG, SAC.

Arquitectura típica (model-free):

- Entrada: estado actual $s$ (vector de características, imagen, etc.).
- Bloque de aproximación de función:  
  - Tabla de valores (en problemas pequeños), o  
  - Red neuronal / modelo paramétrico.
- Salida:  
  - Valores $Q(s,a)$ para cada acción (value-based), o  
  - Probabilidades de acción $\pi(a \mid s)$ (policy-based).
- Módulo de actualización:  
  - Regla de actualización TD (diferencias temporales) para $Q$, o  
  - Gradiente de la política para los parámetros de $\pi$.

---

#### 1.3.2 Algoritmos basados en valores (value-based)

En los métodos value-based el agente aprende una **función de valor** y deriva la política a partir de ella:

- **Función Q:** $Q(s,a)$ = valor esperado de escoger la acción $a$ en el estado $s$ y seguir la política actual.
- **Política implícita:** suele elegirse como  

  $$
  \pi(s) = \arg\max_a Q(s,a)
  $$

  con algún mecanismo de exploración (por ejemplo, $\epsilon$-greedy).

Ejemplos:

- **Q-learning (tabular)**  
  Actualiza una tabla de valores $Q(s,a)$ con una regla de actualización basada en TD.

- **SARSA**  
  Similar a Q-learning, pero la actualización usa la acción realmente tomada en el siguiente estado,
  lo que lo hace on-policy.

- **Deep Q-Network (DQN)**  
  Extiende Q-learning usando una **red neuronal profunda** para aproximar $Q(s,a)$ a partir de estados de alta dimensión (imágenes de videojuegos, por ejemplo).

Elementos de la arquitectura value-based:

- Representación del estado (features o imágenes).
- Aproximador de $Q$ (tabla o red neuronal).
- Mecanismo de selección de acciones.
- Regla de actualización de $Q$ usando recompensas y el valor estimado futuro.

---

#### 1.3.3 Algoritmos basados en políticas (policy-based)

En los métodos policy-based se busca aprender directamente una política **parametrizada** $\pi_\theta(a \mid s)$, sin pasar explícitamente por una función de valor:

- $\theta$ son los parámetros de la política (por ejemplo, pesos de una red neuronal).
- Se maximiza el rendimiento esperado $J(\theta)$ mediante **gradiente ascendente**:

$$
\theta \leftarrow \theta + \alpha \nabla_\theta J(\theta)
$$

Ejemplos:

- **REINFORCE**  
  Método básico de gradiente de política que actualiza $\theta$ a partir de episodios completos.

- **Métodos avanzados de política proximal, como PPO (Proximal Policy Optimization)**  
  Mejoran la estabilidad del entrenamiento limitando cuánto cambia la política en cada actualización.

Arquitectura típica policy-based:

- Entrada: estado $s$.
- Red neuronal: produce parámetros de la distribución sobre acciones  
  (por ejemplo, probabilidades para acciones discretas o media/varianza para acciones continuas).
- Módulo de muestreo: genera la acción $a$ a partir de la distribución.
- Cálculo del **gradiente de la política** usando recompensas acumuladas.

---

#### 1.3.4 Algoritmos Actor–Critic

Los métodos actor–critic combinan ideas de los dos enfoques anteriores:

- **Actor**  
  Componente que representa la política $\pi_\theta(a \mid s)$ y decide qué acción tomar.

- **Crítico (critic)**  
  Componente que estima una función de valor $V^\omega(s)$ o $Q^\omega(s,a)$ y evalúa la calidad de las acciones del actor.

El crítico proporciona una señal de **error de ventaja** o de TD al actor para mejorar la política.

Ejemplos:

- A2C / A3C (Advantage Actor–Critic).
- DDPG (Deep Deterministic Policy Gradient) para acciones continuas.
- SAC (Soft Actor–Critic), que añade principios de máxima entropía.

Arquitectura:

- Una red neuronal para la política (actor).
- Una red neuronal para la función de valor (critic).  
  A veces comparten algunas capas.

---

#### 1.3.5 Otras clasificaciones útiles

- **On-policy vs off-policy**
  - On-policy: la política que se evalúa es la misma que se usa para explorar (por ejemplo, SARSA, algunos actor–critic).
  - Off-policy: se aprende sobre una política objetivo mientras se explora con otra (por ejemplo, Q-learning, DQN).

- **Tabular vs aproximación de funciones**
  - Tabular: tabla explícita de valores para cada par estado–acción (útil solo para espacios pequeños).
  - Aproximación de funciones: redes neuronales, árboles, modelos lineales, etc., aptos para espacios continuos o de alta dimensión.

---

### 1.4 Aplicaciones industriales del aprendizaje por refuerzo (Pregunta 1c)

En la práctica, el aprendizaje por refuerzo se utiliza en múltiples sectores:

- **Robótica y automatización**  
  - Control de brazos robóticos, agarre y manipulación de objetos.  
  - Locomoción de robots bípedos, cuadrúpedos o drones.  

- **Vehículos autónomos y conducción asistida**  
  - Toma de decisiones de alto nivel (planificación de rutas, cambios de carril, adaptación a tráfico).

- **Optimización de redes de comunicaciones y computación en la nube**  
  - Asignación dinámica de recursos, control de congestión, enrutamiento adaptativo.

- **Energía y sistemas eléctricos**  
  - Gestión de microredes, almacenamiento de energía, despacho económico bajo incertidumbre de demanda y generación renovable.

- **Finanzas y trading algorítmico**  
  - Estrategias de compra–venta, gestión de portafolios, market making.

- **Sistemas de recomendación y publicidad**  
  - Recomendación secuencial de productos o contenidos (recomendador que aprende de la interacción continua con usuarios).

- **Salud y medicina personalizada**  
  - Optimización de planes de tratamiento, dosificación adaptativa, control de bombas de infusión.

- **Juegos, entretenimiento y simulación**  
  - Agentes que juegan videojuegos, ajedrez, Go, etc., usados tanto en productos de ocio como en plataformas de prueba y entrenamiento.

En todos estos casos se aprovecha la capacidad del RL para **aprender políticas complejas en entornos dinámicos e inciertos**, usando simulaciones o datos históricos cuando la experimentación directa sería costosa o peligrosa.

---

## 2. Teorema de Bayes aplicado a la detección de spam

### 2.1 Enunciado del problema

Se dispone de la siguiente información histórica sobre los correos recibidos por una empresa:

- El **30 %** de todos los correos son spam:  

  $$
  P(\text{Spam}) = 0.3
  $$

- El **80 %** de los correos spam contienen la palabra “gratis”:  

  $$
  P(\text{“gratis”} \mid \text{Spam}) = 0.8
  $$

- El **10 %** de los correos **no spam** contienen la palabra “gratis”:  

  $$
  P(\text{“gratis”} \mid \text{No Spam}) = 0.1
  $$

Se desea calcular:

$$
P(\text{Spam} \mid \text{“gratis”})
$$

es decir, la probabilidad de que un correo sea spam dado que contiene la palabra “gratis”.

---

### 2.2 Recordatorio: Teorema de Bayes

El teorema de Bayes relaciona probabilidades condicionadas de la siguiente forma:

$$
P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)}
$$

donde:

- $P(A \mid B)$: probabilidad posterior (lo que se desea calcular).
- $P(A)$: probabilidad a priori del evento $A$.
- $P(B \mid A)$: verosimilitud (qué tan probable es observar $B$ si $A$ es cierto).
- $P(B)$: probabilidad total de observar $B$.

En este caso:

- $A = \text{Spam}$
- $B = \text{“gratis”}$

---

### 2.3 Cálculo paso a paso de $P(\text{Spam} \mid \text{“gratis”})$

1. **Probabilidad a priori de spam**  

   $$
   P(\text{Spam}) = 0.3
   $$

   Por tanto:

   $$
   P(\text{No Spam}) = 1 - 0.3 = 0.7
   $$

2. **Verosimilitudes conocidas**

   $$
   P(\text{“gratis”} \mid \text{Spam}) = 0.8
   $$

   $$
   P(\text{“gratis”} \mid \text{No Spam}) = 0.1
   $$

3. **Probabilidad total de observar la palabra “gratis”**

   Se descompone en dos casos mutuamente excluyentes:  
   (correo es spam) o (correo no es spam):

   $$
   \begin{aligned}
   P(\text{“gratis”}) &= P(\text{“gratis”} \mid \text{Spam})P(\text{Spam}) \\
                      &\quad + P(\text{“gratis”} \mid \text{No Spam})P(\text{No Spam}) \\
                     &= 0.8 \cdot 0.3 + 0.1 \cdot 0.7 \\
                     &= 0.24 + 0.07 \\
                     &= 0.31
   \end{aligned}
   $$

4. **Aplicación del teorema de Bayes**

   $$
   \begin{aligned}
   P(\text{Spam} \mid \text{“gratis”})
     &= \frac{P(\text{“gratis”} \mid \text{Spam}) P(\text{Spam})}
             {P(\text{“gratis”})} \\
     &= \frac{0.8 \cdot 0.3}{0.31} \\
     &= \frac{0.24}{0.31} \\
     &\approx 0.7742
   \end{aligned}
   $$

Por tanto, la probabilidad de que un correo sea spam dado que contiene la palabra “gratis” es aproximadamente:

$$
P(\text{Spam} \mid \text{“gratis”}) \approx 0.7742 \approx 77.4\%
$$

**Interpretación:**  
Aunque inicialmente solo el 30 % de los correos son spam, el hecho de que el correo contenga la palabra “gratis” hace que la probabilidad de que sea spam aumente hasta alrededor del 77.4 %.

---

### 2.4 Diseño de un algoritmo basado en el teorema de Bayes

A partir del cálculo anterior, se puede diseñar un algoritmo sencillo que:

1. **Defina los parámetros del problema**
   - $P(\text{Spam})$
   - $P(\text{“gratis”} \mid \text{Spam})$
   - $P(\text{“gratis”} \mid \text{No Spam})$

2. **Calcule la probabilidad total de la palabra “gratis”**

   $$
   P(\text{“gratis”}) = P(\text{“gratis”} \mid \text{Spam}) P(\text{Spam}) +
                        P(\text{“gratis”} \mid \text{No Spam}) P(\text{No Spam})
   $$

3. **Calcule la probabilidad posterior**

   $$
   P(\text{Spam} \mid \text{“gratis”}) =
   \frac{P(\text{“gratis”} \mid \text{Spam}) P(\text{Spam})}
        {P(\text{“gratis”})}
   $$

4. **Opcional: tomar una decisión de clasificación**
   - Fijar un umbral $\tau$ (por ejemplo, $\tau = 0.5$).
   - Si $P(\text{Spam} \mid \text{“gratis”}) \ge \tau$, se clasifica el correo como **SPAM**; en caso contrario, como **NO SPAM**.

Este mismo esquema se puede generalizar a un **clasificador Naive Bayes** con muchas palabras, asumiendo independencia condicional entre ellas.

---

## 3. Algoritmos de IA más utilizados en la academia e industria

En la práctica, la IA moderna combina varias familias de algoritmos. A continuación se presenta una exploración de los más utilizados, organizada por tipo de aprendizaje.

### 3.1 Algoritmos de aprendizaje supervisado

En el aprendizaje supervisado se dispone de ejemplos de entrenamiento $(x, y)$ donde $x$ son características y $y$ es la etiqueta o valor a predecir.

#### 3.1.1 Regresión lineal y regresión logística

- **Tipo de problema**
  - Regresión lineal: predicción de valores continuos.
  - Regresión logística: clasificación binaria (y extensiones para multiclase).

- **Características principales**
  - Modelos **simples e interpretables**.
  - Asumen una relación aproximadamente lineal entre entradas y salida (en un espacio de características).

- **Ventajas**
  - Entrenamiento rápido.
  - Buena línea base para comparar otros métodos.
  - Coeficientes interpretables (importancia de cada variable).

- **Limitaciones**
  - Poca capacidad para modelar relaciones fuertemente no lineales.
  - Sensibles a variables muy correlacionadas y a outliers (si no se tratan adecuadamente).

---

#### 3.1.2 Árboles de decisión

- **Tipo de problema**
  - Clasificación y regresión.

- **Características principales**
  - Modelo jerárquico en forma de árbol de reglas “si… entonces…”.
  - Divide recursivamente el espacio de características según criterios de pureza (gini, entropía, etc.).

- **Ventajas**
  - Altamente interpretables (especialmente árboles pequeños).
  - Pueden manejar características numéricas y categóricas.

- **Limitaciones**
  - Un solo árbol puede ser inestable y propenso al sobreajuste.
  - Rendimiento inferior a métodos de ensamble en problemas complejos.

---

#### 3.1.3 Random Forest (Bosques aleatorios)

- **Tipo de problema**
  - Clasificación y regresión.

- **Características principales**
  - Ensamble de muchos árboles de decisión entrenados sobre subconjuntos aleatorios de datos y características.
  - La predicción final es un promedio (regresión) o votación mayoritaria (clasificación).

- **Ventajas**
  - Muy buen rendimiento en muchos datasets tabulares.
  - Reduce sobreajuste respecto a un árbol individual.
  - Maneja bien datos mixtos (categóricos y numéricos).

- **Limitaciones**
  - Menos interpretables que un solo árbol.
  - Modelos grandes en memoria; inferencia más costosa que modelos lineales.

---

#### 3.1.4 Gradient Boosting (XGBoost, LightGBM, CatBoost)

- **Tipo de problema**
  - Clasificación y regresión.

- **Características principales**
  - Construyen un modelo como suma de árboles de decisión débiles, añadidos secuencialmente.
  - Cada árbol nuevo corrige los errores de los anteriores (gradiente del error).

- **Ventajas**
  - Suelen ofrecer **rendimiento de estado del arte** en problemas tabulares.
  - Permiten ajustar finamente regularización y complejidad del modelo.

- **Limitaciones**
  - Muchos hiperparámetros; requieren más cuidado en el ajuste.
  - Entrenamiento más pesado que modelos lineales sencillos.

---

#### 3.1.5 Máquinas de soporte vectorial (SVM)

- **Tipo de problema**
  - Clasificación (binaria y multiclase), regresión (SVR).

- **Características principales**
  - Buscan un hiperplano que maximiza el margen entre clases.
  - Uso de **kernels** para manejar relaciones no lineales.

- **Ventajas**
  - Buen rendimiento en espacios de alta dimensión.
  - Teoría bien establecida sobre generalización.

- **Limitaciones**
  - Escalan peor con datasets muy grandes.
  - Más complejas de interpretar.

---

#### 3.1.6 Redes neuronales feedforward (MLP)

- **Tipo de problema**
  - Clasificación y regresión general.

- **Características principales**
  - Capas de neuronas conectadas totalmente (fully connected).
  - Capacidad para aproximar funciones muy complejas (teorema de aproximación universal).

- **Ventajas**
  - Gran flexibilidad para modelar no linealidades.
  - Base de los modelos de deep learning.

- **Limitaciones**
  - Requieren más datos y potencia de cómputo que modelos clásicos.
  - Menor interpretabilidad.

---

### 3.2 Deep Learning: CNN, RNN y Transformers

#### 3.2.1 Redes neuronales convolucionales (CNN)

- **Aplicaciones típicas**
  - Visión por computador: clasificación de imágenes, detección de objetos, segmentación.
  - Video, imágenes médicas, etc.

- **Características principales**
  - Capas convolucionales que explotan la estructura espacial de los datos (vecindad de píxeles).
  - Extracción jerárquica de características (bordes, formas, objetos).

- **Ventajas**
  - Desempeño muy superior a métodos clásicos en imágenes.
  - Reutilización de pesos en convoluciones reduce parámetros efectivos.

- **Limitaciones**
  - Necesitan grandes cantidades de datos etiquetados.
  - Costosas computacionalmente (pero muy optimizadas en GPUs).

---

#### 3.2.2 Redes recurrentes (RNN, LSTM, GRU)

- **Aplicaciones típicas**
  - Series de tiempo.
  - Procesamiento de lenguaje natural (antes del dominio de los transformers).
  - Señales secuenciales (audio, sensores).

- **Características principales**
  - Mantienen un **estado interno** que resume información pasada.
  - Variantes LSTM y GRU resuelven problemas de gradientes desvanecidos.

- **Ventajas**
  - Adecuadas para secuencias de longitud variable.
  - Modelan dependencias temporales.

- **Limitaciones**
  - Entrenamiento más difícil que las CNN.
  - En muchos problemas de NLP han sido desplazadas por transformers.

---

#### 3.2.3 Transformers

- **Aplicaciones típicas**
  - Procesamiento de lenguaje natural: traducción, resumen, clasificación de texto, chatbots.
  - Visión: Vision Transformers (ViT).
  - Multimodal (texto + imagen, texto + audio, etc.).

- **Características principales**
  - Arquitectura basada en **mecanismos de atención** (self-attention).
  - Permite procesar secuencias en paralelo (no recurrente).
  - Base de los modelos de lenguaje grandes (LLMs).

- **Ventajas**
  - Estado del arte en muchas tareas de NLP y visión.
  - Muy escalables en datos y parámetros.

- **Limitaciones**
  - Enormes requerimientos de cómputo y memoria para entrenamiento desde cero.
  - Menor interpretabilidad; uso de técnicas específicas para explicación.

---

### 3.3 Aprendizaje no supervisado

En el aprendizaje no supervisado solo se dispone de las entradas $x$, sin etiquetas $y$.

#### 3.3.1 K-Means

- **Tipo**
  - Algoritmo de **clustering** (agrupamiento).

- **Características**
  - Divide los datos en $k$ grupos, minimizando la distancia dentro de cada cluster.
  - Itera entre asignar puntos a centroides y recalcular dichos centroides.

- **Ventajas**
  - Sencillo y rápido.
  - Buena introducción al clustering.

- **Limitaciones**
  - Requiere elegir $k$ de antemano.
  - Sensible a la inicialización y a la escala de las características.
  - Solo captura clusters aproximadamente esféricos.

---

#### 3.3.2 Modelos de mezcla gaussiana (GMM)

- **Tipo**
  - Modelo probabilístico de clustering.

- **Características**
  - Supone que los datos provienen de una mezcla de varias distribuciones gaussianas.
  - Utiliza el algoritmo EM (Expectation–Maximization) para ajustar parámetros.

- **Ventajas**
  - Clusters con formas elípticas y distintos tamaños.
  - Proporciona **probabilidades de pertenencia** a cada cluster.

- **Limitaciones**
  - Asume gaussianidad (lo que no siempre se cumple).
  - Puede atascarse en óptimos locales.

---

#### 3.3.3 Análisis de componentes principales (PCA)

- **Tipo**
  - Reducción de dimensionalidad.

- **Características**
  - Encuentra las direcciones (componentes principales) que explican la mayor varianza de los datos.
  - Proyecta los datos a un subespacio de menor dimensión manteniendo la mayor información posible.

- **Ventajas**
  - Útil para visualización (2D/3D).
  - Reduce ruido y colinealidad.

- **Limitaciones**
  - Transformación lineal; no capta estructuras muy no lineales.
  - Componentes no siempre son fáciles de interpretar.

---

### 3.4 Aprendizaje por refuerzo en el panorama actual

El aprendizaje por refuerzo, descrito en la sección 1, también forma parte de los algoritmos relevantes hoy en día, en especial cuando se combina con deep learning:

- **Q-learning y DQN**
  - Adecuados para entornos con pocos controles pero estados de alta dimensión (videojuegos, simulaciones).

- **Métodos actor–critic modernos (PPO, SAC, DDPG)**
  - Muy utilizados en control continuo (robótica, vehículos, simuladores físicos).

Sus características principales son:

- Aprendizaje por prueba y error con recompensas.
- Necesidad de simuladores o entornos donde experimentar.
- Uso intensivo de redes neuronales profundas para manejar observaciones complejas.

---

### 3.5 Comentarios finales

En la práctica, la selección de un algoritmo depende fuertemente del tipo de problema:

- **Datos tabulares estructurados**  
  Suele preferirse el uso de **árboles de decisión** y, sobre todo, **métodos de ensamble** como Random Forest o Gradient Boosting.

- **Imágenes y video**  
  Las **CNN** y modelos derivados dominan la mayoría de aplicaciones prácticas.

- **Texto y lenguaje natural**  
  Los **transformers** se han convertido en el estándar de facto.

- **Series temporales y secuencias**  
  Se utilizan RNN/LSTM, transformers para secuencias y modelos clásicos como ARIMA según el caso.

- **Control secuencial / decisiones dinámicas**  
  Se emplea **aprendizaje por refuerzo**, a menudo combinado con redes profundas.

Este conjunto de algoritmos constituye el “núcleo duro” de la IA moderna tanto en la academia como en la industria, y proporciona una base sólida para estudios más avanzados en la asignatura de Introducción a la IA.
