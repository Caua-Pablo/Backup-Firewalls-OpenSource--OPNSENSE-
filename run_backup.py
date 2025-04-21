import subprocess
import os
import re
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Configurações do servidor de e-mail
with open("password.json", "r") as f:
    password = json.load(f)

email = password.get("EMAIL")
senha = password.get("PASSWORD")
HOST = "IP DO E-MAIL"
PORT = PORTA DO E-MAIL

# Destinatário fixo
RECIPIENT = "email@email.com"

# Caminho do arquivo de hosts
HOSTS_FILE = "hosts"

# Listas para armazenar os resultados
failed_firewalls = []
successful_firewalls = []

# Caminho da chave privada
SSH_PRIVATE_KEY = "caminho da chave privada"


def start_ssh_agent():
    """Garante que o ssh-agent esteja rodando e adiciona a chave ao cache"""
    if "SSH_AUTH_SOCK" not in os.environ:
        print("Iniciando ssh-agent...")
        agent_output = subprocess.check_output(["ssh-agent", "-s"], text=True)

        for line in agent_output.splitlines():
            if line.startswith("SSH_AUTH_SOCK"):
                os.environ["SSH_AUTH_SOCK"] = line.split(";")[0].split("=")[1]
            elif line.startswith("SSH_AGENT_PID"):
                os.environ["SSH_AGENT_PID"] = line.split(";")[0].split("=")[1]

    result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
    if "no identities" in result.stdout:
        try:
            subprocess.run(["ssh-add", SSH_PRIVATE_KEY], check=True)
            print("Chave SSH adicionada com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao adicionar chave SSH: {e}")
            exit(1)
    else:
        print("Chave SSH já carregada.")


def read_firewall_ips():
    """Lê os IPs e nomes dos firewalls no arquivo 'hosts'."""
    ip_name_mapping = {}
    try:
        with open(HOSTS_FILE, "r") as file:
            for line in file:
                if line.strip().startswith("[") or not line.strip():
                    continue

                parts = line.split()
                name = parts[0]
                ip_match = re.search(r"ansible_host=([\d\.]+)", line)

                if ip_match:
                    ip = ip_match.group(1)
                    ip_name_mapping[ip] = name
    except FileNotFoundError:
        print(f"Erro: Arquivo {HOSTS_FILE} não encontrado.")
    return ip_name_mapping


def run_backup(firewall_mapping):
    """Executa o backup e armazena os resultados"""
    for firewall_ip, firewall_name in firewall_mapping.items():
        print(f"Executando backup para o firewall {firewall_name} ({firewall_ip})...")
        try:
            result = subprocess.run(
                ["ansible-playbook", "-i", "hosts", "--limit", firewall_name, "backup_opnsense.yml"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Backup do firewall {firewall_name} ({firewall_ip}) realizado com sucesso!")
                successful_firewalls.append((firewall_ip, firewall_name))
            else:
                print(f"Falha no backup do firewall {firewall_name} ({firewall_ip}).")
                failed_firewalls.append((firewall_ip, firewall_name))
        except Exception as e:
            print(f"Erro ao executar o backup do firewall {firewall_name} ({firewall_ip}): {e}")
            failed_firewalls.append((firewall_ip, firewall_name))

    send_email(successful_firewalls, failed_firewalls)


def send_email(successful_firewalls, failed_firewalls):
    """Envia e-mail com os resultados do backup."""
    try:
        server = smtplib.SMTP(HOST, PORT)
        server.starttls()
        server.login(email, senha)

        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = RECIPIENT

        if failed_firewalls:
            msg["Subject"] = "Relatório: Falhas no Backup dos Firewalls"
            message_type = "falhou"
            data = failed_firewalls
        else:
            msg["Subject"] = "Relatório: Backup dos Firewalls realizado com sucesso"
            message_type = "foi concluído com sucesso"
            data = successful_firewalls

        with open("logomarca.png", "rb") as image_file:
            img = MIMEImage(image_file.read())
            img.add_header("Content-ID", "<logomarca>")
            msg.attach(img)

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.9; color: #333; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .header img {{ max-width: 150px; height: auto; }}
                h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; text-align: left; padding: 8px; }}
                th {{ background-color: #f4f4f4; }}
                .footer {{ margin-top: 30px; text-align: center; font-size: 0.9em; color: #777; }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="cid:logomarca" alt="Logo da Empresa">
            </div>
            <h2>Relatório do Backup dos Firewalls</h2>
            <p>Prezado(a),</p>
            <p>O backup {message_type} para os seguintes dispositivos:</p>
            <p><strong>Total: {len(data)}</strong></p>
            <table>
                <thead>
                    <tr>
                        <th>Nome do Firewall</th>
                        <th>IP</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        for ip, name in data:
            status = "Sucesso" if not failed_firewalls else "Falha"
            color = "green" if not failed_firewalls else "red"
            html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{ip}</td>
                        <td style="color: {color};">{status}</td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
            <div class="footer">
                <p>Este é um e-mail automático. Por favor, não responda.</p>
                <p><strong>INFORMAÇÃO ADICIONAL DO RODAPE</strong></p>
                <p>Email: INFORMAÇÕES ADICIONAIS NO RODAPE
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        server.send_message(msg)
        print(f"E-mail enviado para {RECIPIENT} com o relatório do backup.")

        server.quit()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


if __name__ == "__main__":
    start_ssh_agent()
    firewall_mapping = read_firewall_ips()
    if firewall_mapping:
        run_backup(firewall_mapping)
    else:
        print("Nenhum IP de firewall encontrado no arquivo 'hosts'.")
