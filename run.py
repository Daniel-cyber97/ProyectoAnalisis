"""
Script principal para ejecutar la aplicación Flask

Este archivo inicializa y ejecuta la aplicación Flask para el proyecto
de Análisis de Principios y Variables Estadísticas.
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True)