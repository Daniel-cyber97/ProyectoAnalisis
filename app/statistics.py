"""
Funciones de cálculos estadísticos

Este módulo contiene funciones para realizar diversos cálculos estadísticos
sobre conjuntos de datos, incluyendo medidas de tendencia central, dispersión, 
y análisis de variables.
"""

import numpy as np
import pandas as pd
from collections import Counter
import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns

def calcular_estadisticas(datos):
    """
    Calcula estadísticas descriptivas para un conjunto de datos numéricos.
    
    Args:
        datos (list): Lista de valores numéricos
        
    Returns:
        dict: Diccionario con las estadísticas calculadas
    """
    # Convertir a array numpy para optimizar cálculos
    data_np = np.array(datos)
    
    # Determinar el número óptimo de bins para el histograma
    # Regla de Sturges: k = ceil(log2(n) + 1)
    bins = int(np.ceil(np.log2(len(datos)) + 1))
    
    # Calcular estadísticas descriptivas
    estadisticas = {
        'count': len(datos),
        'minimo': float(np.min(data_np)),
        'maximo': float(np.max(data_np)),
        'rango': float(np.max(data_np) - np.min(data_np)),
        'media': float(np.mean(data_np)),
        'mediana': float(np.median(data_np)),
        'desviacion_estandar': float(np.std(data_np)),
        'varianza': float(np.var(data_np)),
        'q1': float(np.percentile(data_np, 25)),
        'q3': float(np.percentile(data_np, 75)),
        'rango_intercuartilico': float(np.percentile(data_np, 75) - np.percentile(data_np, 25)),
        'bins': bins
    }
    
    return estadisticas

def analizar_tipo_variable(datos):
    """
    Analiza el tipo de variable estadística basado en los datos proporcionados.
    
    Args:
        datos (list): Lista de valores (pueden ser numéricos o no)
        
    Returns:
        dict: Diccionario con el tipo de variable y estadísticas asociadas
    """
    # Intentar convertir a valores numéricos
    try:
        # Convertir y verificar si son todos números
        valores_numericos = [float(x) for x in datos]
        es_numerica = True
    except ValueError:
        # Si hay error de conversión, es una variable cualitativa
        es_numerica = False
    
    if es_numerica:
        # Verificar si todos son enteros
        todos_enteros = all(float(x).is_integer() for x in valores_numericos)
        
        if todos_enteros:
            tipo = 'cuantitativa discreta'
        else:
            tipo = 'cuantitativa continua'
        
        # Estadísticas básicas para variables numéricas
        resultado = {
            'tipo': 'cuantitativa',
            'subtipo': tipo,
            'minimo': min(valores_numericos),
            'maximo': max(valores_numericos),
            'rango': max(valores_numericos) - min(valores_numericos),
            'cantidad': len(valores_numericos)
        }
    else:
        # Análisis para variables cualitativas/categóricas
        # Contar frecuencias de cada categoría
        contador = Counter(datos)
        categorias = list(contador.keys())
        frecuencias = dict(contador)
        
        resultado = {
            'tipo': 'cualitativa',
            'categorias': categorias,
            'frecuencias': frecuencias,
            'cantidad': len(datos),
            'categorias_unicas': len(categorias)
        }
    
    return resultado

def generar_datos_aleatorios(param1, param2, cantidad, tipo='uniforme'):
    """
    Genera datos aleatorios siguiendo una distribución específica.
    
    Args:
        param1 (float): Primer parámetro (mínimo para uniforme, media para normal)
        param2 (float): Segundo parámetro (máximo para uniforme, desviación estándar para normal)
        cantidad (int): Número de datos a generar
        tipo (str): Tipo de distribución ('uniforme' o 'normal')
        
    Returns:
        list: Lista de datos aleatorios generados
    """
    np.random.seed(42)  # Para reproducibilidad
    
    if tipo == 'uniforme':
        # param1: mínimo, param2: máximo
        return list(np.random.uniform(param1, param2, cantidad))
    elif tipo == 'normal':
        # param1: media, param2: desviación estándar
        return list(np.random.normal(param1, param2, cantidad))
    else:
        # Por defecto, retornar distribución uniforme
        return list(np.random.uniform(param1, param2, cantidad))

def generar_grafico_histograma(datos, media=None, mediana=None, titulo="Histograma"):
    """
    Genera un histograma para un conjunto de datos numéricos.
    
    Args:
        datos (list): Lista de valores numéricos
        media (float, optional): Valor de la media para mostrar en el gráfico
        mediana (float, optional): Valor de la mediana para mostrar en el gráfico
        titulo (str): Título del gráfico
        
    Returns:
        str: URL de datos (base64) del gráfico generado
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(datos, kde=True)
    
    if media is not None:
        plt.axvline(media, color='r', linestyle='--', label=f'Media: {media:.2f}')
    
    if mediana is not None:
        plt.axvline(mediana, color='g', linestyle='-.', label=f'Mediana: {mediana:.2f}')
    
    plt.legend()
    plt.title(titulo)
    plt.tight_layout()
    
    # Guardar el gráfico en un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convertir el gráfico a una URL de datos para incrustar en HTML
    grafico_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return grafico_url

def generar_grafico_boxplot(datos, titulo="Diagrama de Caja"):
    """
    Genera un diagrama de caja (boxplot) para un conjunto de datos numéricos.
    
    Args:
        datos (list): Lista de valores numéricos
        titulo (str): Título del gráfico
        
    Returns:
        str: URL de datos (base64) del gráfico generado
    """
    plt.figure(figsize=(10, 4))
    sns.boxplot(x=datos)
    plt.title(titulo)
    plt.tight_layout()
    
    # Guardar el gráfico en un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convertir el gráfico a una URL de datos para incrustar en HTML
    grafico_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return grafico_url

def generar_grafico_barras_categoricas(categorias, frecuencias, titulo="Frecuencia de Categorías"):
    """
    Genera un gráfico de barras para variables categóricas.
    
    Args:
        categorias (list): Lista de nombres de categorías
        frecuencias (list): Lista de frecuencias para cada categoría
        titulo (str): Título del gráfico
        
    Returns:
        str: URL de datos (base64) del gráfico generado
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(x=categorias, y=frecuencias)
    plt.xticks(rotation=45)
    plt.title(titulo)
    plt.tight_layout()
    
    # Guardar el gráfico en un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convertir el gráfico a una URL de datos para incrustar en HTML
    grafico_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return grafico_url