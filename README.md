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



2. Arquivo de credenciais (password.json)

{
  "EMAIL": "seu@email.com",
  "PASSWORD": "sua_senha"
}



3. Chave SSH

Você precisa de uma chave privada configurada para acessar os dispositivos. O script suporta 2 formas de uso:
🔁 Opção 1: Temporária (recarregada a cada execução)

Já está implementado no run_backup.py:

ssh-agent bash -c './run_backup.py'

Ou rode diretamente:

python3 run_backup.py

💾 Opção 2: Persistente no boot (via systemd)

Crie um serviço para o ssh-agent no boot. Exemplo:

nano ~/.config/systemd/user/ssh-agent.service

[Unit]
Description=SSH key agent

[Service]
Type=simple
Environment=SSH_AUTH_SOCK=%t/ssh-agent.socket
ExecStart=/usr/bin/ssh-agent -D

[Install]
WantedBy=default.target

Ative com:

systemctl --user enable --now ssh-agent

🧪 Como executar
Rodar backup para todos os firewalls:

python3 run_backup.py

Rodar manualmente apenas para um host:

ansible-playbook -i hosts backup_opnsense.yml --limit Firewall_Teste

Testar conectividade:

ansible -i hosts Firewall_Teste -m ping

📬 Envio de e-mail

Por padrão, o script envia e-mail apenas quando houver falha no backup.
💡 (Opcional) Quer testar envio em caso de sucesso?

Você pode adicionar uma função send_success_email() e chamar após backups bem-sucedidos. Exemplo:

if not failed_firewalls:
    send_success_email()
