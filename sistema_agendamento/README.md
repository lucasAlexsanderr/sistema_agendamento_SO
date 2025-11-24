# Sistema de Agendamento de Consultas Médicas

## 📋 Descrição
Sistema completo de agendamento que demonstra conceitos de Sistemas Operacionais.

## 🔹 Conceitos de SO Implementados

- ✅ **Processos e Threads**: Processamento concorrente de agendamentos
- ✅ **Sistema de Arquivos**: Persistência em JSON com operações atômicas
- ✅ **Gerência de Memória**: Cache LRU com TTL
- ✅ **Concorrência**: Locks para evitar race conditions
- ✅ **I/O**: Operações assíncronas de leitura/escrita
- ✅ **Configuração Multi-plataforma**: Detecção automática de SO

## 🚀 Instalação

### 1. Criar ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
```

### 2. Instalar dependências:
```bash
pip install -r requirements.txt
```

## ▶️ Executar
```bash
python src/main.py
```

Acesse: http://localhost:5000

## 🧪 Testes
```bash
# Fase 1: Configuração e Logging
python tests/test_fase1.py

# Fase 2: Models, Storage e Cache
python tests/test_fase2.py

# Fase 3: Interface Web e Concorrência
python tests/test_fase3.py
```

## 🛠️ Tecnologias

- Python 3.8+
- Flask (Web Framework)
- JSON (Persistência)
- Threading (Concorrência)
- ReportLab (Relatórios PDF)

## 📁 Estrutura
```
sistema_agendamento/
├── src/
│   ├── config/      # Configuração do SO e logging
│   ├── core/        # Models e lógica de negócio
│   ├── storage/     # Persistência em JSON
│   ├── concurrent/  # Threads e processamento paralelo
│   ├── reports/     # Geração de relatórios
│   └── web/         # Interface web Flask
├── data/
│   ├── consultas/   # Dados persistidos
│   ├── relatorios/  # Relatórios gerados
│   ├── logs/        # Arquivos de log
│   └── backups/     # Backups automáticos
└── tests/           # Testes automatizados
```

## 👨‍💻 Autor

Desenvolvido como projeto acadêmico de Sistemas Operacionais.