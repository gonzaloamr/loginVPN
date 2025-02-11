import subprocess
import logging
from pathlib import Path

# Configuração básica do logging.
# As mensagens serão gravadas no arquivo vpn_manager.log,
# com nível DEBUG e um formato que inclui data/hora, nível e mensagem.
logging.basicConfig(
    filename='vpn_manager.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class VPNManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        # O arquivo de credenciais usado pelo OpenVPN (não será apagado)
        self.credential_file = self.script_dir / "credenciais.txt"
        # Arquivo temporário que poderá ser limpo
        self.pass_file = self.script_dir / "pass_auth.txt"
        self.config_file = self.script_dir / "VPN_DEV_SIS_INTERNOS_gonzalo_munoz.ovpn"
        
    def _cleanup_files(self):
        """Remove arquivos temporários (mantém credenciais.txt)"""
        if self.pass_file.exists():
            self.pass_file.unlink()

    def connect(self, username, password):
        """Executa a conexão VPN e grava as mensagens de log para depuração."""
        try:
            logging.info("Tentando parar o serviço apache2.")
            subprocess.run(['sudo', 'service', 'apache2', 'stop'], check=True)
            self._cleanup_files()

            logging.info("Gerando arquivo de credenciais (%s).", self.credential_file)
            # Cria o arquivo de credenciais com usuário na primeira linha e senha (concatenada com o código 2FA) na segunda
            with open(self.credential_file, 'w') as f:
                f.write(f"{username}\n{password}")

            # Se necessário, também cria o arquivo pass_auth.txt
            with open(self.pass_file, 'w') as f:
                f.write(password)

            logging.info("Iniciando OpenVPN com o arquivo de configuração: %s", self.config_file)
            cmd = [
                'sudo', '-S', 'openvpn',
                '--config', str(self.config_file),
                '--daemon'
            ]

            # Supondo que você tenha a senha do usuário armazenada na variável `sudo_password`
            result = subprocess.run(
                cmd,
                input=sudo_password + "\n",  # a senha será lida pelo sudo
                check=True,
                capture_output=True,
                text=True,
                cwd=str(self.script_dir)
)
            
            logging.info("OpenVPN executado com sucesso.")
            logging.debug("OpenVPN stdout: %s", result.stdout)
            logging.debug("OpenVPN stderr: %s", result.stderr)

            self._cleanup_files()
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error("Erro na execução do OpenVPN. Código de retorno: %s", e.returncode)
            logging.error("OpenVPN stdout: %s", e.stdout)
            logging.error("OpenVPN stderr: %s", e.stderr)
            self._cleanup_files()
            return False
        except Exception as e:
            logging.exception("Erro inesperado durante a conexão VPN: %s", str(e))
            self._cleanup_files()
            return False