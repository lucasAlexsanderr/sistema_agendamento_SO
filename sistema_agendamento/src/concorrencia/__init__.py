"""
Módulo de processamento concorrente
"""

from .threads import ThreadManager, BackgroundWorker, TaskQueue, thread_manager

__all__ = ['ThreadManager', 'BackgroundWorker', 'TaskQueue', 'thread_manager']