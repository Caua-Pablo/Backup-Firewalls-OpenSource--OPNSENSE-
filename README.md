🔐 Backup Automático de Firewalls OPNSense com Ansible + Notificação por E-mail


Este repositório contém um script em Python que automatiza backups de firewalls OPNSense via Ansible, e envia alertas por e-mail em caso de falha (com opção de ativar envio em caso de sucesso também).

ESTRUTURA DO PROJETO
.
├── backup_opnsense.yml        # Playbook do Ansible que executa o backup
├── hosts                      # Inventário Ansible com os firewalls
├── logomarca.png              # Logo usada no corpo do e-mail
├── password.json              # Arquivo com credenciais de e-mail
├── run_backup.py              # Script principal


🚀 Como funciona?

    Lê os IPs e nomes dos firewalls definidos no inventário (hosts)

    Executa um ansible-playbook para cada um, um por vez

    Se algum falhar, envia um e-mail com o relatório das falhas

    O e-mail inclui uma logo, tabela com nomes/IPs e aviso automático


    ✅ Pré-requisitos

    Python 3.x

    Ansible instalado

    SSH configurado com chave privada

    SMTP configurado (interno ou externo)

    Acesso aos firewalls via SSH (root)

1. Inventário Ansible (hosts)

Exemplo:

    [firewalls]
FIREWALL_TESTE ansible_host=IP ansible_user=user ansible_python_interpreter=/usr/local/bin/python3 ansible_port=2222






