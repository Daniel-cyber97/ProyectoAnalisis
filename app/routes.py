"""
Rutas de la aplicación Flask

Este módulo define todas las rutas y controladores de la aplicación web.
Gestiona las solicitudes HTTP y renderiza las plantillas correspondientes.
"""

from flask import render_template, request, redirect, url_for, flash, session
from app import app
from app.statistics import (
    calcular_estadisticas, analizar_tipo_variable, generar_datos_aleatorios,
    generar_grafico_histograma, generar_grafico_boxplot, generar_grafico_barras_categoricas
)
import numpy as np
import json

# Datos globales en memoria para mantener histórico (simulando una DB)
HISTORICO_ANALISIS = []
HISTORICO_VARIABLES = []

@app.route('/')
def index():
    """Ruta principal que muestra la página de inicio"""
    return render_template('index.html')

@app.route('/introduccion')
def introduccion():
    """Ruta que muestra la página de introducción a la estadística en IA"""
    return render_template('intro.html')

@app.route('/variables', methods=['GET', 'POST'])
def variables():
    """
    Ruta que maneja la página de variables estadísticas
    - GET: Muestra la página de variables
    - POST: Analiza el tipo de variable y guarda los resultados
    """
    resultado = None
    grafico_url = None
    
    if request.method == 'POST':
        # Obtener datos del formulario
        datos = request.form.get('datos', '').strip()
        
        if datos:
            # Analizar el tipo de variable
            datos_lista = [x.strip() for x in datos.split(',')]
            resultado = analizar_tipo_variable(datos_lista)
            
            # Si es una variable categórica, generar gráfico
            if resultado['tipo'] == 'cualitativa':
                categorias = resultado['categorias']
                frecuencias = [resultado['frecuencias'][cat] for cat in categorias]
                grafico_url = generar_grafico_barras_categoricas(
                    categorias, 
                    frecuencias, 
                    "Distribución de Frecuencias"
                )
                
                # Guardar en el histórico
                HISTORICO_VARIABLES.append({
                    'nombre': f"Variable - {resultado['categorias_unicas']} categorías",
                    'descripcion': "Variable categórica creada manualmente",
                    'tipo': 'cualitativa',
                    'categorias': categorias,
                    'frecuencias': frecuencias
                })
            else:
                # Para variables cuantitativas, generar histograma
                valores = [float(x) for x in datos_lista]
                grafico_url = generar_grafico_histograma(
                    valores, 
                    np.mean(valores), 
                    np.median(valores), 
                    "Distribución de Valores"
                )
                
                # Guardar en el histórico
                HISTORICO_VARIABLES.append({
                    'nombre': f"Variable - {resultado['subtipo']}",
                    'descripcion': "Variable numérica creada manualmente",
                    'tipo': 'cuantitativa',
                    'subtipo': resultado['subtipo'],
                    'datos': valores
                })
            
            # Mantener el histórico con un máximo de 5 elementos
            if len(HISTORICO_VARIABLES) > 5:
                HISTORICO_VARIABLES.pop(0)
    
    return render_template(
        'variables.html', 
        resultado=resultado, 
        grafico_url=grafico_url, 
        historico=HISTORICO_VARIABLES
    )

@app.route('/central', methods=['GET', 'POST'])
def central():
    """
    Ruta que maneja la página de medidas centrales
    - GET: Muestra la página de medidas centrales
    - POST: Calcula las medidas centrales de los datos proporcionados
    """
    resultado = None
    grafico_url = None
    
    if request.method == 'POST':
        # Obtener datos del formulario
        datos_str = request.form.get('datos', '').strip()
        
        if datos_str:
            try:
                # Convertir string a lista de números
                datos = [float(x.strip()) for x in datos_str.split(',')]
                
                if datos:
                    # Calcular estadísticas
                    resultado = {}
                    resultado['datos'] = datos
                    resultado['datos_ordenados'] = sorted(datos)
                    resultado['media'] = np.mean(datos)
                    resultado['media_manual'] = sum(datos) / len(datos)
                    resultado['mediana'] = np.median(datos)
                    
                    # Cálculo manual de la mediana
                    datos_ordenados = sorted(datos)
                    n = len(datos_ordenados)
                    if n % 2 == 0:  # Si el número de datos es par
                        resultado['mediana_manual'] = (datos_ordenados[n//2 - 1] + datos_ordenados[n//2]) / 2
                    else:  # Si el número de datos es impar
                        resultado['mediana_manual'] = datos_ordenados[n//2]
                    
                    # Generar gráfico
                    grafico_url = generar_grafico_histograma(
                        datos, 
                        resultado['media'], 
                        resultado['mediana'],
                        'Distribución de datos con Media y Mediana'
                    )
                    
                    # Guardar en el histórico
                    HISTORICO_ANALISIS.append({
                        'nombre': "Medidas centrales",
                        'descripcion': "Cálculo de media y mediana",
                        'tipo': 'central',
                        'datos': datos,
                        'media': resultado['media'],
                        'mediana': resultado['mediana']
                    })
                    
                    # Mantener el histórico con un máximo de 5 elementos
                    if len(HISTORICO_ANALISIS) > 5:
                        HISTORICO_ANALISIS.pop(0)
                
            except ValueError:
                flash('Error: Los datos deben ser números separados por comas', 'error')
    
    return render_template('central.html', resultado=resultado, grafico_url=grafico_url)

@app.route('/analisis', methods=['GET', 'POST'])
def analisis():
    """
    Ruta que maneja la página de análisis estadístico completo
    - GET: Muestra la página de análisis
    - POST: Realiza un análisis estadístico completo de los datos
    """
    resultado = None
    histograma_url = None
    boxplot_url = None
    
    if request.method == 'POST':
        # Obtener datos según el tipo seleccionado
        tipo_dataset = request.form.get('tipo_dataset')
        nombre_dataset = request.form.get('nombre_dataset', 'Análisis')
        descripcion = request.form.get('descripcion', 'Análisis estadístico')
        
        datos = []
        
        # Procesar según el tipo de conjunto de datos
        if tipo_dataset == 'manual':
            datos_str = request.form.get('datos_manual', '').strip()
            if datos_str:
                try:
                    datos = [float(x.strip()) for x in datos_str.split(',')]
                except ValueError:
                    flash('Error: Los datos deben ser números separados por comas', 'error')
                    return redirect(url_for('analisis'))
        
        elif tipo_dataset == 'historico':
            indice_historico = int(request.form.get('indice_historico', 0))
            if 0 <= indice_historico < len(HISTORICO_ANALISIS):
                item_historico = HISTORICO_ANALISIS[indice_historico]
                datos = item_historico.get('datos', [])
                nombre_dataset = f"Reanálisis de: {item_historico.get('nombre', 'Datos previos')}"
        
        elif tipo_dataset == 'aleatorio':
            try:
                min_val = float(request.form.get('min_val', 0))
                max_val = float(request.form.get('max_val', 100))
                count = int(request.form.get('cantidad', 30))
                
                if count <= 0:
                    flash('La cantidad debe ser mayor que cero', 'error')
                    return redirect(url_for('analisis'))
                
                datos = generar_datos_aleatorios(min_val, max_val, count, tipo='uniforme')
            except ValueError:
                flash('Error en los parámetros para datos aleatorios', 'error')
                return redirect(url_for('analisis'))
        
        elif tipo_dataset == 'normal':
            try:
                media = float(request.form.get('media', 50))
                desviacion = float(request.form.get('desviacion', 10))
                count = int(request.form.get('cantidad_normal', 30))
                
                if count <= 0:
                    flash('La cantidad debe ser mayor que cero', 'error')
                    return redirect(url_for('analisis'))
                
                datos = generar_datos_aleatorios(media, desviacion, count, tipo='normal')
            except ValueError:
                flash('Error en los parámetros para distribución normal', 'error')
                return redirect(url_for('analisis'))
        
        # Si hay datos, realizar el análisis
        if datos:
            # Calcular estadísticas
            resultado = calcular_estadisticas(datos)
            
            # Generar histograma
            histograma_url = generar_grafico_histograma(
                datos, 
                resultado['media'], 
                resultado['mediana'],
                'Histograma de distribución'
            )
            
            # Generar boxplot
            boxplot_url = generar_grafico_boxplot(datos, 'Diagrama de caja (Boxplot)')
            
            # Guardar en el histórico
            HISTORICO_ANALISIS.append({
                'nombre': nombre_dataset,
                'descripcion': descripcion,
                'tipo': tipo_dataset,
                'datos': datos,
                'estadisticas': resultado
            })
            
            # Mantener el histórico con un máximo de 5 elementos
            if len(HISTORICO_ANALISIS) > 5:
                HISTORICO_ANALISIS.pop(0)
    
    return render_template(
        'analisis.html', 
        resultado=resultado, 
        histograma_url=histograma_url, 
        boxplot_url=boxplot_url,
        historico=HISTORICO_ANALISIS
    )