"""
Inicialización de la aplicación Flask

Este módulo configura y crea la instancia de la aplicación Flask.
"""

from flask import Flask
import os

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'estadistica_key_secreto'  # Clave para las sesiones

# Importar rutas después de crear la app para evitar importaciones circulares
from app import routes