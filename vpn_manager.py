import subprocess
import os
import shutil
from pathlib import Path
import threading

class VPNManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.credential_file = self.script_dir / "credentials.txt"
        self.pass_file = self.script_dir / "pass_auth.txt"
        self.config_file = self.script_dir / "VPN_DEV_SIS_INTERNOS_gonzalo_munoz.ovpn"
        
    def _cleanup_files(self):
        """Remove arquivos temporários"""
        for file in [self.credential_file, self.pass_file]:
            if file.exists():
                file.unlink()

    def connect(self, username, password):
        """Executa a conexão VPN"""
        try:
            # 1. Parar serviços e limpar arquivos antigos
            subprocess.run(['sudo', 'service', 'apache2', 'stop'], check=True)
            self._cleanup_files()

            # 2. Gerar arquivos temporários (mockado por enquanto)
            with open(self.credential_file, 'w') as f:
                f.write(f"{username}\n{password}123456")  # Mock do OAuth

            with open(self.pass_file, 'w') as f:
                f.write(f"{password}123456")

            # 3. Executar OpenVPN
            cmd = [
                'sudo', 'openvpn',
                '--config', str(self.config_file),
                '--daemon'
            ]
            
            subprocess.run(cmd, check=True)
            
            # 4. Limpeza final
            self._cleanup_files()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Erro na execução: {str(e)}")
            self._cleanup_files()
            return False
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            self._cleanup_files()
            return False