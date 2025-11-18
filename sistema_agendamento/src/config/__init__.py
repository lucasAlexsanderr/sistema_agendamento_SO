"""
Módulo de configuração do sistema
"""

from .os_config import config, ConfigSO
from .logger import configurar_logging, log_manager

__all__ = ['config', 'ConfigSO', 'configurar_logging', 'log_manager']