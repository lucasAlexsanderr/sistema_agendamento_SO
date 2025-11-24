"""
Verificador de Estrutura do Projeto
Verifica se todos os arquivos e diretórios necessários existem
"""

import os
import sys

# Estrutura esperada do projeto
ESTRUTURA_ESPERADA = {
    'diretorios': [
        'src',
        'src/config',
        'src/core',
        'src/storage',
        'src/concorrencia',
        'src/reports',
        'src/web',
        'src/web/templates',
        'src/web/static',
        'data',
        'data/consultas',
        'data/relatorios',
        'data/logs',
        'data/backups',
        'docs',
        'tests',
    ],
    'arquivos': [
        # Raiz
        'requirements.txt',
        'README.md',

        # Config
        'src/__init__.py',
        'src/config/__init__.py',
        'src/config/os_config.py',
        'src/config/logger.py',

        # Core
        'src/core/__init__.py',
        'src/core/models.py',
        'src/core/cache.py',

        # Storage
        'src/storage/__init__.py',
        'src/storage/json_storage.py',

        # Tests
        'tests/test_fase1.py',
        'tests/test_fase2.py',
    ]
}

# Arquivos que vamos criar na Fase 3
PROXIMA_FASE = {
    'diretorios': [
        'src/concorrencia',
        'src/web',
        'src/web/templates',
        'src/web/static',
    ],
    'arquivos': [
        'src/core/agendamento.py',
        'src/concorrencia/__init__.py',
        'src/concorrencia/threads.py',
        'src/web/__init__.py',
        'src/web/app.py',
        'src/main.py',
        'tests/test_fase3.py',
    ]
}


def verificar_estrutura():
    """Verifica a estrutura atual do projeto"""
    print("\n" + "=" * 70)
    print("🔍 VERIFICAÇÃO DA ESTRUTURA DO PROJETO")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Verifica diretórios
    print("\n📁 VERIFICANDO DIRETÓRIOS...")
    diretorios_ok = []
    diretorios_faltando = []

    for diretorio in ESTRUTURA_ESPERADA['diretorios']:
        caminho = os.path.join(base_dir, diretorio)
        if os.path.exists(caminho) and os.path.isdir(caminho):
            print(f"   ✅ {diretorio}")
            diretorios_ok.append(diretorio)
        else:
            print(f"   ❌ {diretorio} (FALTANDO)")
            diretorios_faltando.append(diretorio)

    # Verifica arquivos
    print("\n📄 VERIFICANDO ARQUIVOS...")
    arquivos_ok = []
    arquivos_faltando = []

    for arquivo in ESTRUTURA_ESPERADA['arquivos']:
        caminho = os.path.join(base_dir, arquivo)
        if os.path.exists(caminho) and os.path.isfile(caminho):
            tamanho = os.path.getsize(caminho)
            if tamanho > 0:
                print(f"   ✅ {arquivo} ({tamanho} bytes)")
                arquivos_ok.append(arquivo)
            else:
                print(f"   ⚠️  {arquivo} (VAZIO)")
                arquivos_faltando.append(arquivo)
        else:
            print(f"   ❌ {arquivo} (FALTANDO)")
            arquivos_faltando.append(arquivo)

    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"Diretórios OK: {len(diretorios_ok)}/{len(ESTRUTURA_ESPERADA['diretorios'])}")
    print(f"Arquivos OK: {len(arquivos_ok)}/{len(ESTRUTURA_ESPERADA['arquivos'])}")

    # Próxima fase
    print("\n" + "=" * 70)
    print("🔮 PRÓXIMA FASE (Fase 3)")
    print("=" * 70)
    print("\n📁 Diretórios a criar:")
    for diretorio in PROXIMA_FASE['diretorios']:
        caminho = os.path.join(base_dir, diretorio)
        if os.path.exists(caminho):
            print(f"   ✅ {diretorio} (já existe)")
        else:
            print(f"   📝 {diretorio} (será criado)")

    print("\n📄 Arquivos a criar:")
    for arquivo in PROXIMA_FASE['arquivos']:
        caminho = os.path.join(base_dir, arquivo)
        if os.path.exists(caminho):
            print(f"   ✅ {arquivo} (já existe)")
        else:
            print(f"   📝 {arquivo} (será criado)")

    # Verifica dependências
    print("\n" + "=" * 70)
    print("📦 VERIFICANDO DEPENDÊNCIAS")
    print("=" * 70)

    try:
        import flask
        print(f"   ✅ Flask {flask.__version__}")
    except ImportError:
        print("   ❌ Flask (NÃO INSTALADO)")

    try:
        import reportlab
        print(f"   ✅ ReportLab instalado")
    except ImportError:
        print("   ❌ ReportLab (NÃO INSTALADO)")

    try:
        import dateutil
        print(f"   ✅ python-dateutil instalado")
    except ImportError:
        print("   ❌ python-dateutil (NÃO INSTALADO)")

    # Decisão final
    print("\n" + "=" * 70)

    if diretorios_faltando or arquivos_faltando:
        print("⚠️  ATENÇÃO: Alguns arquivos/diretórios estão faltando!")
        print("\n🔧 AÇÕES NECESSÁRIAS:")

        if diretorios_faltando:
            print("\n1. Criar diretórios faltantes:")
            for d in diretorios_faltando:
                print(f"   mkdir -p {d}")

        if arquivos_faltando:
            print("\n2. Criar/corrigir arquivos faltantes:")
            for a in arquivos_faltando:
                print(f"   - {a}")

        return False
    else:
        print("✅ ESTRUTURA ATUAL COMPLETA!")
        print("✅ Pronto para iniciar Fase 3!")
        return True


def criar_diretorios_faltantes():
    """Cria automaticamente os diretórios faltantes"""
    print("\n🔧 Criando diretórios faltantes...")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    for diretorio in ESTRUTURA_ESPERADA['diretorios'] + PROXIMA_FASE['diretorios']:
        caminho = os.path.join(base_dir, diretorio)
        if not os.path.exists(caminho):
            try:
                os.makedirs(caminho, exist_ok=True)
                print(f"   ✅ Criado: {diretorio}")
            except Exception as e:
                print(f"   ❌ Erro ao criar {diretorio}: {e}")


if __name__ == "__main__":
    print("\n" + "🔍" * 35)

    # Verifica estrutura
    ok = verificar_estrutura()

    if not ok:
        print("\n❓ Deseja criar os diretórios faltantes automaticamente? (s/n)")
        resposta = input("> ").lower().strip()

        if resposta == 's':
            criar_diretorios_faltantes()
            print("\n✅ Diretórios criados! Execute este script novamente para verificar.")
        else:
            print("\n⚠️  Crie os diretórios manualmente antes de continuar.")
            sys.exit(1)

    print("\n" + "🔍" * 35)