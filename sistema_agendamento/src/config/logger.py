"""
Sistema de Logging Centralizado
🔹 Conceito SO: Gerência de Dispositivos, Operações de I/O
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def configurar_logging(log_dir):
    """
    Configura sistema de logging com múltiplos handlers
    🔹 Conceito SO: Escrita em arquivo, Buffering, Flush

    Args:
        log_dir: Diretório onde os logs serão salvos

    Returns:
        Logger configurado
    """

    # 🔹 Conceito SO: Criação de diretório se não existir
    os.makedirs(log_dir, exist_ok=True)

    # Nome do arquivo de log
    log_filename = os.path.join(log_dir, 'sistema.log')
    erro_filename = os.path.join(log_dir, 'erros.log')

    # 🔹 Conceito SO: Formato com timestamp do sistema
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configuração do logger raiz
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # HANDLER 1: Arquivo principal com rotação
    # 🔹 Conceito SO: Rotação de arquivos, gerenciamento de espaço em disco
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=5 * 1024 * 1024,  # 5MB por arquivo
        backupCount=5,  # Mantém 5 arquivos de backup
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # HANDLER 2: Console (stdout)
    # 🔹 Conceito SO: Saída padrão, stream de I/O
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # HANDLER 3: Arquivo de erros separado
    # 🔹 Conceito SO: Separação de streams de erro
    error_handler = RotatingFileHandler(
        erro_filename,
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)

    # Log inicial do sistema
    logger.info("=" * 60)
    logger.info("🏥 Sistema de Agendamento Médico iniciado")
    logger.info(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📁 Logs salvos em: {log_dir}")
    logger.info("=" * 60)

    return logger


class LogManager:
    """
    Gerenciador de logs com estatísticas
    🔹 Conceito SO: Monitoramento de operações de I/O
    """

    def __init__(self):
        self.total_logs = 0
        self.logs_por_nivel = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }

    def log(self, nivel, mensagem):
        """
        Registra log e atualiza estatísticas
        🔹 Conceito SO: Auditoria de operações
        """
        self.total_logs += 1
        self.logs_por_nivel[nivel] += 1

        logger = logging.getLogger(__name__)

        if nivel == 'DEBUG':
            logger.debug(mensagem)
        elif nivel == 'INFO':
            logger.info(mensagem)
        elif nivel == 'WARNING':
            logger.warning(mensagem)
        elif nivel == 'ERROR':
            logger.error(mensagem)
        elif nivel == 'CRITICAL':
            logger.critical(mensagem)

    def log_operacao(self, operacao, entidade, detalhes=""):
        """
        Log padronizado de operações CRUD

        Args:
            operacao: CREATE, READ, UPDATE, DELETE
            entidade: paciente, medico, consulta
            detalhes: informações adicionais
        """
        mensagem = f"[{operacao}] {entidade}"
        if detalhes:
            mensagem += f" | {detalhes}"

        self.log('INFO', mensagem)
        return mensagem

    def get_estatisticas(self):
        """Retorna estatísticas de logging"""
        return {
            'total': self.total_logs,
            'por_nivel': self.logs_por_nivel.copy()
        }

    def imprimir_estatisticas(self):
        """Imprime estatísticas formatadas"""
        stats = self.get_estatisticas()
        print("\n" + "=" * 40)
        print("📊 ESTATÍSTICAS DE LOGS")
        print("=" * 40)
        print(f"Total de logs: {stats['total']}")
        print("\nPor nível:")
        for nivel, qtd in stats['por_nivel'].items():
            print(f"  {nivel:10s}: {qtd:5d}")
        print("=" * 40)


# Instância global do gerenciador
log_manager = LogManager()

if __name__ == "__main__":
    # Teste rápido
    import tempfile

    print("🧪 Testando sistema de logging...\n")

    # Configura logging em diretório temporário para teste
    temp_dir = tempfile.mkdtemp()
    configurar_logging(temp_dir)

    # Testa diferentes níveis
    log_manager.log('DEBUG', 'Mensagem de debug')
    log_manager.log('INFO', 'Mensagem informativa')
    log_manager.log('WARNING', 'Mensagem de aviso')
    log_manager.log('ERROR', 'Mensagem de erro')

    # Testa log de operação
    log_manager.log_operacao('CREATE', 'paciente', 'João Silva cadastrado')
    log_manager.log_operacao('READ', 'consulta', 'Listagem de 10 consultas')

    # Mostra estatísticas
    log_manager.imprimir_estatisticas()

    print(f"\n✅ Logs salvos em: {temp_dir}")
    print("✅ Sistema de logging OK!")