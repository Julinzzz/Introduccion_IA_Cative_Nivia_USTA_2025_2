# Resumen: Particle Swarm Optimisation (PSO) -- Revisión Histórica y Avances Actuales

## Introducción

El algoritmo de **Optimización por Enjambre de Partículas (PSO)** fue
introducido en 1995 por Eberhart y Kennedy, inspirado en el
comportamiento social de aves al buscar alimento. Se convirtió
rápidamente en una de las técnicas más populares de **inteligencia de
enjambre**, gracias a su simplicidad, independencia de supuestos
matemáticos fuertes y amplio rango de aplicaciones.

El objetivo de esta revisión es resumir la evolución de PSO, incluyendo
modificaciones, variantes, hibridaciones y aplicaciones prácticas hasta
la actualidad.

------------------------------------------------------------------------

## Conceptos Fundamentales

-   **Partículas:** Representan soluciones candidatas que se desplazan
    en el espacio de búsqueda.
-   **Velocidad y posición:** Se actualizan combinando información
    individual (mejor posición personal) y colectiva (mejor posición
    global).
-   **Modelos principales:**
    -   **Gbest:** Toda la población comparte la mejor posición global.
    -   **Lbest:** Cada partícula se comunica solo con sus vecinos, lo
        que mejora diversidad y exploración.

------------------------------------------------------------------------

## Mejoras en la Convergencia

1.  **Parámetro de inercia (ω):** Introducido por Shi y Eberhart (1998),
    regula el equilibrio entre exploración y explotación.
2.  **Factor de constricción (K):** Clerc (1999) garantizó estabilidad
    matemática y control de trayectorias.
3.  **Estrategias adaptativas:** Variaciones dinámicas de ω, pesos
    cognitivos y sociales, e incluso enfoques difusos para evitar
    convergencia prematura.

------------------------------------------------------------------------

## Arquitecturas de Vecindario

-   **Estáticas:** topologías de anillo, estrella, pirámide, von
    Neumann.
-   **Dinámicas:** adaptan conectividad según distancias o iteraciones.
-   **Interacciones cercanas (FDR):** Selección de vecinos basada en la
    relación entre distancia y aptitud, mejorando el rendimiento en
    problemas multimodales.

------------------------------------------------------------------------

## Problemas Identificados

-   **Convergencia prematura:** El enjambre puede atascarse en óptimos
    locales.
-   **Estancamiento:** Cuando todas las partículas coinciden en el mejor
    global y dejan de explorar.

Se desarrollaron variantes como **GCPSO (Guaranteed Convergence PSO)**
para mitigar estos problemas.

------------------------------------------------------------------------

## Variantes Importantes de PSO

1.  **Cooperative PSO (CPSO):** Divide el problema en subespacios
    optimizados por sub-enjambres.
2.  **Adaptive PSO (APSO):** Clasifica dinámicamente el estado evolutivo
    (exploración, explotación, convergencia, escape).
3.  **PSO para problemas con restricciones:** Métodos basados en
    penalización, preservación de soluciones factibles y mecanismos de
    "fly-back".
4.  **Optimización multiobjetivo (MOPSO):** Uso de repositorios externos
    para construir frentes de Pareto.
5.  **Optimización multimodal:** Métodos como **STPSO**, **NichePSO**,
    subpoblaciones y técnicas de especiación para encontrar múltiples
    óptimos.

------------------------------------------------------------------------

## Variantes Avanzadas

-   **FIPS (Fully Informed PSO):** Cada partícula recibe información de
    todos sus vecinos.
-   **PSO paralelo (PPSO):** Implementaciones en CPU y GPU para acelerar
    procesos de gran dimensión.
-   **Niching y multi-swarm:** Enjambres múltiples para explorar
    regiones diversas.

------------------------------------------------------------------------

## Hibridaciones con Otras Técnicas

-   **Con operadores evolutivos:** selección, cruces y mutaciones (EPSO,
    DNSPSO).
-   **Con Algoritmos Genéticos (GA):** Combinación de operadores de GA y
    dinámica de PSO.
-   **Con Diferential Evolution (DE):** Métodos híbridos como DEPSO y
    DEEPSO.
-   **Con Recocido Simulado (SA):** Algoritmos híbridos (SAPSO, HPSO)
    para escapar de óptimos locales.
-   **Con otras metaheurísticas:** ACO, Cuckoo Search, Artificial Bee
    Colony, etc.

------------------------------------------------------------------------

## Redes Neuronales y PSO

-   PSO se ha usado exitosamente para **entrenar redes neuronales
    artificiales (ANN)**.
-   Ventajas: rapidez de convergencia y menor probabilidad de quedar
    atrapado en mínimos locales frente al backpropagation.
-   Aplicaciones: clasificación de señales biomédicas, predicción de
    carga eléctrica, sistemas de control difusos, diseño de
    arquitecturas neuronales.

------------------------------------------------------------------------

## Conclusiones

-   PSO es un algoritmo **simple, flexible y robusto**, con gran
    adaptabilidad.
-   Sus limitaciones originales (convergencia prematura, pérdida de
    diversidad) han sido enfrentadas con numerosas variantes.
-   Es **independiente del problema**, aplicable a optimización
    continua, discreta, multiobjetivo y multimodal.
-   Continúa siendo uno de los algoritmos más influyentes de la
    inteligencia de enjambre y se proyecta como herramienta clave en
    inteligencia artificial y optimización compleja.

------------------------------------------------------------------------

## Bibliografía

Freitas, D., Lopes, L.G., & Morgado-Dias, F. (2020). *Particle Swarm
Optimisation: A Historical Review Up to the Current Developments*.
Entropy, 22(3), 362. https://doi.org/10.3390/e22030362
