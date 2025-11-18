"""
Configuração específica por Sistema Operacional
🔹 Conceito SO: Chamadas de Sistema, Detecção de Plataforma
"""

import os
import platform
import logging
from pathlib import Path


class ConfigSO:
    """
    Detecta o SO e configura paths e permissões adequadas
    Demonstra: Detecção de plataforma, manipulação de sistema de arquivos
    """

    def __init__(self):
        # 🔹 Conceito SO: Chamadas de sistema para obter informações da plataforma
        self.sistema = platform.system()  # 'Linux', 'Windows', 'Darwin'
        self.versao = platform.version()
        self.arquitetura = platform.machine()  # x86_64, arm64, etc
        self.home = str(Path.home())

        # Diretório base do projeto
        self.base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )

        print(f"🐧 Sistema Operacional: {self.sistema} {self.versao}")
        print(f"💻 Arquitetura: {self.arquitetura}")
        print(f"🏠 Home: {self.home}")
        print(f"📁 Base: {self.base_dir}")

    def get_data_dir(self):
        """Retorna diretório de dados"""
        return os.path.join(self.base_dir, 'data')

    def get_consultas_dir(self):
        """Diretório para arquivos de consultas"""
        return os.path.join(self.get_data_dir(), 'consultas')

    def get_relatorios_dir(self):
        """Diretório para relatórios gerados"""
        return os.path.join(self.get_data_dir(), 'relatorios')

    def get_logs_dir(self):
        """Diretório para arquivos de log"""
        return os.path.join(self.get_data_dir(), 'logs')

    def get_backups_dir(self):
        """Diretório para backups automáticos"""
        return os.path.join(self.get_data_dir(), 'backups')

    def criar_diretorios(self):
        """
        Cria estrutura de diretórios necessária
        🔹 Conceito SO: Criação de estrutura de sistema de arquivos
        """
        diretorios = [
            self.get_data_dir(),
            self.get_consultas_dir(),
            self.get_relatorios_dir(),
            self.get_logs_dir(),
            self.get_backups_dir()
        ]

        for diretorio in diretorios:
            try:
                # 🔹 Conceito SO: Criação de diretórios
                os.makedirs(diretorio, exist_ok=True)
                print(f"✅ Diretório: {diretorio}")

                # 🔹 Conceito SO: Permissões de arquivo (Linux/macOS)
                if self.sistema in ['Linux', 'Darwin']:
                    os.chmod(diretorio, 0o755)  # rwxr-xr-x

            except Exception as e:
                print(f"❌ Erro ao criar {diretorio}: {str(e)}")
                raise

    def get_separator(self):
        """
        Retorna separador de path correto
        🔹 Conceito SO: Diferenças entre Windows (\) e Unix (/)
        """
        return os.sep

    def get_info_sistema(self):
        """
        Retorna informações completas do sistema
        🔹 Conceito SO: Informações de hardware e SO
        """
        import getpass

        return {
            'sistema': self.sistema,
            'versao': self.versao,
            'arquitetura': self.arquitetura,
            'usuario': getpass.getuser(),
            'home': self.home,
            'separador': self.get_separator(),
            'encoding': 'utf-8'
        }


# Instância global de configuração
config = ConfigSO()

if __name__ == "__main__":
    # Teste rápido
    print("\n" + "=" * 60)
    print("TESTE DE CONFIGURAÇÃO DO SO")
    print("=" * 60)

    info = config.get_info_sistema()
    for chave, valor in info.items():
        print(f"{chave}: {valor}")

    print("\nCriando diretórios...")
    config.criar_diretorios()
    print("\n✅ Configuração OK!")