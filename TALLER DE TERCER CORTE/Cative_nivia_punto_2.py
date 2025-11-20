"""
bayes_spam.py 

Autores: Cative y Nivia

Pequeño algoritmo que calcula la probabilidad de que un correo sea spam
dado que contiene la palabra 'gratis', usando el teorema de Bayes.

También incluye una función sencilla para clasificar correos en función
de si contienen o no la palabra 'gratis'.
"""


def prob_spam_dado_gratis(
    p_spam: float = 0.3,
    p_gratis_dado_spam: float = 0.8,
    p_gratis_dado_no_spam: float = 0.1,
) -> float:
    """
    Calcula P(Spam | contiene 'gratis') usando el teorema de Bayes.

    Parámetros
    ----------
    p_spam : float
        Probabilidad a priori de que un correo sea spam, P(Spam).
    p_gratis_dado_spam : float
        Probabilidad de que aparezca la palabra 'gratis' en un correo spam,
        P('gratis' | Spam).
    p_gratis_dado_no_spam : float
        Probabilidad de que aparezca la palabra 'gratis' en un correo NO spam,
        P('gratis' | No Spam).

    Returns
    -------
    float
        Probabilidad posterior P(Spam | 'gratis').
    """
    # Probabilidad de no spam
    p_no_spam = 1.0 - p_spam

    # Probabilidad total de observar la palabra 'gratis'
    p_gratis = p_gratis_dado_spam * p_spam + p_gratis_dado_no_spam * p_no_spam

    if p_gratis == 0:
        raise ValueError(
            "La probabilidad total de 'gratis' es cero; "
            "revisa los parámetros de entrada."
        )

    # Teorema de Bayes: P(Spam | gratis) = P(gratis | Spam)*P(Spam) / P(gratis)
    p_spam_dado_gratis = (p_gratis_dado_spam * p_spam) / p_gratis
    return p_spam_dado_gratis


def clasificar_correo(contenido_correo: str, umbral: float = 0.5) -> tuple[float, bool]:
    """
    Clasifica un correo como SPAM o NO SPAM en función de si contiene
    la palabra 'gratis', usando el modelo de Bayes anterior.

    Parámetros
    ----------
    contenido_correo : str
        Texto completo del correo a evaluar.
    umbral : float
        Umbral de decisión sobre la probabilidad de spam.
        Si P(spam | correo) >= umbral, se clasifica como SPAM.

    Returns
    -------
    (probabilidad_spam, es_spam) : (float, bool)
        probabilidad_spam : probabilidad estimada de que el correo sea spam.
        es_spam : True si se clasifica como SPAM, False en caso contrario.
    """
    texto = contenido_correo.lower()
    contiene_gratis = "gratis" in texto

    if contiene_gratis:
        # Caso: el correo contiene 'gratis'
        p_spam = prob_spam_dado_gratis()
    else:
        # Caso simplificado: si no aparece 'gratis', se usa la probabilidad a priori.
        # Se podría extender para P(Spam | no 'gratis'), pero no es requerido
        # en el enunciado.
        p_spam = 0.3  # P(Spam) a priori

    es_spam = p_spam >= umbral
    return p_spam, es_spam


if __name__ == "__main__":
    # Ejemplo de uso
    ejemplo = "¡Obtén un curso GRATIS ahora mismo, solo por hoy!"
    probabilidad, es_spam = clasificar_correo(ejemplo, umbral=0.5)

    print("===== CLASIFICADOR DE SPAM CON BAYES =====")
    print(f"Correo de ejemplo: {ejemplo}")
    print(f"Probabilidad de SPAM dado el contenido: {probabilidad:.4f} "
          f"({probabilidad * 100:.2f}%)")
    print(f"Clasificación final: {'SPAM' if es_spam else 'NO SPAM'}")
