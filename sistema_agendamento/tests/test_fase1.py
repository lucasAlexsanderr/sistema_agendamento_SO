"""
Teste da Fase 1: Configuração e Logging
"""

import sys
import os

# Adiciona o diretório src ao path
projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(projeto_dir, 'src')
sys.path.insert(0, src_dir)

# Agora importa normalmente
from config import config, configurar_logging, log_manager


def teste_configuracao_so():
    """Testa detecção do SO e criação de diretórios"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 1: Configuração do Sistema Operacional")
    print("=" * 60)

    # Testa detecção do SO
    info = config.get_info_sistema()
    print("\n📋 Informações do Sistema:")
    for chave, valor in info.items():
        print(f"   {chave:15s}: {valor}")

    # Testa criação de diretórios
    print("\n📁 Criando estrutura de diretórios...")
    config.criar_diretorios()

    # Verifica se diretórios foram criados
    diretorios_criados = []
    diretorios = [
        config.get_data_dir(),
        config.get_consultas_dir(),
        config.get_relatorios_dir(),
        config.get_logs_dir(),
        config.get_backups_dir()
    ]

    for diretorio in diretorios:
        if os.path.exists(diretorio):
            diretorios_criados.append(diretorio)
            print(f"   ✅ {diretorio}")
        else:
            print(f"   ❌ {diretorio}")

    assert len(diretorios_criados) == len(diretorios), "Nem todos os diretórios foram criados"

    print("\n✅ TESTE 1 PASSOU!")
    return True


def teste_logging():
    """Testa sistema de logging"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 2: Sistema de Logging")
    print("=" * 60)

    # Configura logging
    log_dir = config.get_logs_dir()
    configurar_logging(log_dir)

    print(f"\n📁 Logs configurados em: {log_dir}")

    # Testa diferentes níveis de log
    print("\n📝 Testando diferentes níveis de log...")
    log_manager.log('DEBUG', 'Teste de DEBUG')
    log_manager.log('INFO', 'Teste de INFO')
    log_manager.log('WARNING', 'Teste de WARNING')
    log_manager.log('ERROR', 'Teste de ERROR')

    # Testa log de operações
    print("\n📝 Testando logs de operações CRUD...")
    log_manager.log_operacao('CREATE', 'paciente', 'Paciente P001 criado')
    log_manager.log_operacao('READ', 'consulta', 'Consulta C001 lida')
    log_manager.log_operacao('UPDATE', 'medico', 'Médico M001 atualizado')
    log_manager.log_operacao('DELETE', 'paciente', 'Paciente P002 removido')

    # Verifica arquivo de log
    log_file = os.path.join(log_dir, 'sistema.log')
    if os.path.exists(log_file):
        print(f"\n✅ Arquivo de log criado: {log_file}")

        # Mostra tamanho do arquivo
        tamanho = os.path.getsize(log_file)
        print(f"   Tamanho: {tamanho} bytes")
    else:
        print(f"\n❌ Arquivo de log NÃO criado")
        return False

    # Mostra estatísticas
    log_manager.imprimir_estatisticas()

    print("\n✅ TESTE 2 PASSOU!")
    return True


def teste_integracao():
    """Testa integração entre módulos"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 3: Integração")
    print("=" * 60)

    # Testa se consegue usar ambos os módulos juntos
    print("\n🔗 Testando integração entre módulos...")

    info = config.get_info_sistema()
    log_manager.log('INFO', f"Sistema detectado: {info['sistema']}")
    log_manager.log('INFO', f"Usuário: {info['usuario']}")
    log_manager.log('INFO', f"Arquitetura: {info['arquitetura']}")

    print("   ✅ Configuração + Logging funcionando juntos")

    print("\n✅ TESTE 3 PASSOU!")
    return True


def executar_todos_testes():
    """Executa todos os testes da Fase 1"""
    print("\n" + "🚀" * 30)
    print("INICIANDO TESTES DA FASE 1")
    print("🚀" * 30)

    testes_passaram = []

    try:
        testes_passaram.append(teste_configuracao_so())
    except Exception as e:
        print(f"\n❌ TESTE 1 FALHOU: {str(e)}")
        testes_passaram.append(False)

    try:
        testes_passaram.append(teste_logging())
    except Exception as e:
        print(f"\n❌ TESTE 2 FALHOU: {str(e)}")
        testes_passaram.append(False)

    try:
        testes_passaram.append(teste_integracao())
    except Exception as e:
        print(f"\n❌ TESTE 3 FALHOU: {str(e)}")
        testes_passaram.append(False)

    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 60)

    total = len(testes_passaram)
    passou = sum(testes_passaram)

    print(f"✅ Testes passaram: {passou}/{total}")
    print(f"❌ Testes falharam: {total - passou}/{total}")

    if passou == total:
        print("\n🎉 TODOS OS TESTES DA FASE 1 PASSARAM!")
        print("✅ Pronto para avançar para Fase 2!")
        return True
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False


if __name__ == "__main__":
    sucesso = executar_todos_testes()
    sys.exit(0 if sucesso else 1)