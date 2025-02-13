import subprocess
from tkinter import messagebox, ttk
import logging
import os
from pathlib import Path

logging.disable(logging.CRITICAL)  # Se não quiser ver os logs comente essa linha
script_dir = Path(__file__).parent.resolve()
log_file = script_dir / "vpn_manager.log"

# Configuração básica do logging.
logging.basicConfig(
    filename=str(log_file),  # Usa o caminho absoluto do log
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_ovpn_config_path():
    """Lê o caminho do arquivo OVPN do arquivo de configuração vpn_config.txt"""
    dir_app = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(dir_app, "vpn_config.txt")
    
    try:
        with open(config_file, 'r') as f:
            ovpn_filename = f.readline().strip()
            if not ovpn_filename:
                messagebox.showerror("Erro", "Arquivo vpn_config.txt está vazio!")
                return None
            
            ovpn_path = os.path.join(dir_app, ovpn_filename)
            if not os.path.exists(ovpn_path):
                messagebox.showerror("Erro", f"Arquivo OVPN não encontrado: {ovpn_path}")
                return None
            
            return ovpn_path
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo vpn_config.txt não encontrado!")
        return None

def run_sudo_command(cmd, sudo_password, cwd=None):
    """
    Executa um comando sudo com a opção -S, passando a senha via stdin.
    Retorna uma tupla: (código_de_retorno, stdout, stderr)
    """
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd  # Define o diretório de trabalho
    )
    out, err = proc.communicate(sudo_password + "\n")
    return proc.returncode, out, err

class VPNManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.credential_file = self.script_dir / "credenciais.txt"
        self.pass_file = self.script_dir / "pass_auth.txt"
        self.config_file = get_ovpn_config_path()
        
    def _cleanup_files(self):
        # Remove o arquivo pass_auth.txt, se existir
        if self.pass_file.exists():
            self.pass_file.unlink()
        # Remove o arquivo credenciais.txt, se existir
        if self.credential_file.exists():
            self.credential_file.unlink()

    def connect(self, username, password, sudo_password):
        try:
            logging.info("Tentando parar o serviço apache2.")
            ret, out, err = run_sudo_command(
                ['sudo', '-S', 'service', 'apache2', 'stop'], 
                sudo_password,
                cwd=str(self.script_dir)
            )
            if ret != 0:
                logging.error("Erro ao parar o apache2: %s", err)
                return False

            # Limpa processos antigos de OpenVPN, se houver
            self.kill_openvpn_processes(sudo_password)
            self._cleanup_files()  # Limpa arquivos antigos (credenciais e pass_auth)

            logging.info("Gerando arquivo de credenciais (%s).", self.credential_file)
            with open(self.credential_file, 'w') as f:
                f.write(f"{username}\n{password}")

            with open(self.pass_file, 'w') as f:
                f.write(password)

            logging.info("Iniciando OpenVPN com o arquivo de configuração: %s", self.config_file)
            cmd = [
                'sudo', '-S', 'openvpn',
                '--config', str(self.config_file),
                '--daemon'  # Executa em background
            ]
            ret, out, err = run_sudo_command(cmd, sudo_password, cwd=str(self.script_dir))
            if ret != 0:
                logging.error("Erro na execução do OpenVPN. Código de retorno: %s", ret)
                logging.error("OpenVPN stdout: %s", out)
                logging.error("OpenVPN stderr: %s", err)
                self._cleanup_files()
                return False

            logging.info("OpenVPN executado com sucesso.")
            logging.debug("OpenVPN stdout: %s", out)
            logging.debug("OpenVPN stderr: %s", err)

            self._cleanup_files()
            return True

        except Exception as e:
            logging.exception("Erro inesperado durante a conexão VPN: %s", str(e))
            self._cleanup_files()
            return False

    def kill_openvpn_processes(self, sudo_password):
        """
        Procura e mata processos de OpenVPN em execução.
        """
        # Comando que lista os PIDs dos processos openvpn (o uso de '[o]penvpn' evita que o próprio grep apareça na lista)
        cmd = "ps aux | grep '[o]penvpn' | awk '{print $2}'"
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(self.script_dir)
        )
        out, err = proc.communicate()
        if out:
            pids = out.strip().splitlines()
            for pid in pids:
                # Mata cada processo encontrado
                ret, out_kill, err_kill = run_sudo_command(
                    ['sudo', '-S', 'kill', '-9', pid],
                    sudo_password,
                    cwd=str(self.script_dir)
                )
                logging.info("Processo openvpn com PID %s finalizado (retorno %s)", pid, ret)
        else:
            logging.info("Nenhum processo openvpn encontrado para matar.")