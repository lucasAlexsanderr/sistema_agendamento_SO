"""Módulo core - lógica de negócio"""
from .models import Paciente, Medico, Consulta
from .cache import cache_manager, CacheManager

__all__ = ['Paciente', 'Medico', 'Consulta', 'cache_manager', 'CacheManager']