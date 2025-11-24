#!/usr/bin/env python3
"""
Sistema de Agendamento de Consultas Médicas
Arquivo principal de execução

🔹 Conceitos de SO Demonstrados:
- Processos: Servidor web rodando como processo
- Threads: Processamento concorrente de requisições
- Sistema de Arquivos: Persistência em JSON
- Gerência de Memória: Cache LRU
- Sincronização: Locks para controle de concorrência
- I/O: Operações assíncronas de leitura/escrita
"""

import sys
import os
import logging

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, configurar_logging
from web.app import app


def banner():
    """Exibe banner do sistema"""
    print("\n" + "=" * 70)
    print("🏥 SISTEMA DE AGENDAMENTO DE CONSULTAS MÉDICAS")
    print("=" * 70)
    print("\n📋 Projeto: Sistemas Operacionais")
    print("🔹 Conceitos Implementados:")
    print("   • Processos e Threads")
    print("   • Sistema de Arquivos")
    print("   • Gerência de Memória (Cache)")
    print("   • Sincronização e Locks")
    print("   • Operações de I/O")
    print("   • Configuração Multi-plataforma")
    print("\n" + "=" * 70)


def verificar_estrutura():
    """Verifica e cria estrutura de diretórios"""
    print("\n📁 Verificando estrutura de diretórios...")

    try:
        config.criar_diretorios()
        print("✅ Estrutura de diretórios OK")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar diretórios: {str(e)}")
        return False


def iniciar_sistema():
    """Inicializa e inicia o sistema"""

    # Exibe banner
    banner()

    # Verifica estrutura
    if not verificar_estrutura():
        print("\n❌ Erro ao inicializar sistema")
        sys.exit(1)

    # Configura logging
    print("\n📝 Configurando sistema de logging...")
    try:
        configurar_logging(config.get_logs_dir())
        print("✅ Logging configurado")
    except Exception as e:
        print(f"❌ Erro ao configurar logging: {str(e)}")
        sys.exit(1)

    # Exibe informações do sistema
    print("\n💻 Informações do Sistema:")
    info = config.get_info_sistema()
    print(f"   Sistema Operacional: {info['sistema']}")
    print(f"   Arquitetura: {info['arquitetura']}")
    print(f"   Usuário: {info['usuario']}")
    print(f"   Diretório de Dados: {config.get_data_dir()}")

    # Informações do servidor
    print("\n🌐 Iniciando servidor web...")
    print("\n" + "=" * 70)
    print("🚀 SERVIDOR RODANDO")
    print("=" * 70)
    print(f"\n   🔗 URL: http://localhost:5000")
    print(f"   🔗 URL (rede): http://0.0.0.0:5000")
    print("\n   💡 Pressione Ctrl+C para parar o servidor")
    print("=" * 70 + "\n")

    # Inicia servidor Flask
    # 🔹 Conceito SO: Processo servidor com múltiplas threads
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Desativa debug em produção
            use_reloader=False,  # Evita reinicialização dupla
            threaded=True  # 🔹 Permite múltiplas threads para requisições
        )
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("🛑 SERVIDOR INTERROMPIDO PELO USUÁRIO")
        print("=" * 70)
        logging.info("Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO NO SERVIDOR: {str(e)}")
        logging.error(f"Erro no servidor: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    iniciar_sistema()