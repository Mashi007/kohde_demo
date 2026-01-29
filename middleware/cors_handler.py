"""
Middleware para manejo mejorado de CORS y headers para el frontend.
"""
from flask import request, jsonify
from functools import wraps


def add_cors_headers(response):
    """
    Agrega headers CORS apropiados a las respuestas.
    
    Args:
        response: Response object de Flask
        
    Returns:
        Response con headers CORS agregados
    """
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response


def handle_options_request():
    """
    Maneja requests OPTIONS (preflight) de CORS.
    
    Returns:
        Response apropiada para preflight request
    """
    response = jsonify({'status': 'ok'})
    return add_cors_headers(response), 200
