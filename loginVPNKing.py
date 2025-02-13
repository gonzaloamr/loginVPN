import tkinter as tk
from tkinter import messagebox, ttk
import os
import subprocess
import platform
from vpn_manager import VPNManager
from vpn_manager import get_ovpn_config_path
import threading
from tkinter import simpledialog

def check_vpn_status():
    config_path = get_ovpn_config_path()
    if not config_path:
        return False
    try:
        output = subprocess.check_output(
            ["pgrep", "-f", f"openvpn --config {config_path}"],
            text=True
        )
        if output.strip():
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def update_initial_vpn_status():
    if check_vpn_status():
        vpn_status_label.config(text="VPN Status: Conectado")
    else:
        vpn_status_label.config(text="VPN Status: Desconectado")

def show_index():
    """Exibe a página index (Olá mundo) e esconde outras páginas."""
    frame_code.pack_forget()
    frame_loginvpn.pack_forget()
    frame_index.pack(fill='both', expand=True)

def show_code():
    """Exibe a página Meu Code e esconde outras páginas."""
    frame_index.pack_forget()
    frame_loginvpn.pack_forget()
    frame_code.pack(fill='both', expand=True)
    carregar_code()

def show_loginvpn():
    """Exibe a página de Login VPN e esconde outras páginas."""
    frame_index.pack_forget()
    frame_code.pack_forget()
    frame_loginvpn.pack(fill='both', expand=True)

def salvar_code():
    """Salva o código digitado no arquivo code.py"""
    code = code_entry.get()
    if code:
        try:
            dir_app = os.path.dirname(os.path.realpath(__file__))
            caminho_arquivo = os.path.join(dir_app, "code.py")
            
            with open(caminho_arquivo, "w") as f:
                f.write(f'code = "{code}"\n')
                
            messagebox.showinfo("Code", "Code salvo com sucesso!")
            carregar_code()  
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    else:
        messagebox.showwarning("Aviso", "Digite o código antes de salvar.")

def carregar_code():
    """Carrega e exibe o código salvo"""
    dir_app = os.path.dirname(os.path.realpath(__file__))
    caminho_arquivo = os.path.join(dir_app, "code.py")

    if os.path.exists(caminho_arquivo):
        try:
            code_namespace = {}
            with open(caminho_arquivo, "r") as f:
                exec(f.read(), code_namespace)

            code_atual = code_namespace.get("code", "Nenhum code salvo")
        except Exception:
            code_atual = "Erro ao carregar code"
    else:
        code_atual = "Nenhum code salvo"

    code_label_atual.config(text=f'Meu code atual é: "{code_atual}"')

def login_vpn():
    """Realiza o login na VPN, gera o código 2FA, concatena com a senha e grava as credenciais."""
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    if usuario and senha:
        try:
            dir_app = os.path.dirname(os.path.realpath(__file__))
            caminho_code = os.path.join(dir_app, "code.py")
            if os.path.exists(caminho_code):
                try:
                    code_namespace = {}
                    with open(caminho_code, "r") as f:
                        exec(f.read(), code_namespace)
                    secret = code_namespace.get("code")
                    if not secret:
                        messagebox.showwarning("Aviso", "Nenhum code salvo. Salve um code primeiro!")
                        return
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar code: {e}")
                    return
            else:
                messagebox.showwarning("Aviso", "Arquivo code.py não encontrado.")
                return

            from google_authenticator import GoogleAuthenticator
            ga = GoogleAuthenticator(secret)
            access_code = ga.get_code()

            #Concatena a senha digitada com o código gerado do google
            senha_completa = senha + access_code

            caminho_credenciais = os.path.join(dir_app, "credenciais.txt")
            with open(caminho_credenciais, "a") as cred_file:
                cred_file.write(f"{usuario}\n")
                cred_file.write(f"{senha_completa}\n")

            vpn = VPNManager()
            
            def executar_conexao():
                if vpn.connect(usuario, senha_completa, senha):
                    update_initial_vpn_status()
                    messagebox.showinfo("VPN", f"Conexão VPN estabelecida com sucesso!")
                    show_index()
                else:
                    messagebox.showerror("VPN", "Falha na conexão VPN")
            
            threading.Thread(target=executar_conexao, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha crítica: {str(e)}")
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos!")

def desconectar_vpn():
    """Desconecta a VPN matando os processos de OpenVPN e atualiza o status na página principal."""
    confirm = messagebox.askyesno("Sair da VPN", "Tem certeza que deseja desconectar a VPN?")
    if confirm:
        sudo_password = simpledialog.askstring("Sair da VPN", "Digite sua senha sudo para desconectar:", show="*", parent=root)
        if sudo_password:
            vpn = VPNManager()
            try:
                vpn.kill_openvpn_processes(sudo_password)
                update_initial_vpn_status()
                messagebox.showinfo("VPN", "Desconectado da VPN com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao desconectar VPN: {e}")
        else:
            messagebox.showwarning("Aviso", "Senha sudo não fornecida. Não foi possível desconectar a VPN.")

def acao_sair():
    """Encerra o aplicativo"""
    root.quit()

# Configuração da janela principal
root = tk.Tk(className="VPN KingHost")
root.title("Login VPN KingHost")
root.geometry("500x300")
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "img", "kinghost-favicon.png")

icone = tk.PhotoImage(file=image_path)
root.iconphoto(True, icone)

# Configuração do menu, frames, etc.
menubar = tk.Menu(root)
menu_acoes = tk.Menu(menubar, tearoff=0)
menu_acoes.add_command(label="Login VPN", command=show_loginvpn)
menu_acoes.add_command(label="Logout VPN", command=desconectar_vpn)
menu_acoes.add_command(label="Meu Code", command=show_code)
menu_acoes.add_separator()
menu_acoes.add_command(label="Sair", command=acao_sair)
menubar.add_cascade(label="Menu", menu=menu_acoes)
root.config(menu=menubar)

# Frames para as páginas
frame_index = tk.Frame(root)
frame_code = tk.Frame(root)
frame_loginvpn = tk.Frame(root)

# Página Index
label_ola = tk.Label(frame_index, font=("Arial", 24))
label_ola.pack(expand=True)
img = tk.PhotoImage(file=image_path)
image_label = tk.Label(frame_index, image=img)
image_label.image = img
image_label.place(relx=0.5, rely=0.5, anchor="center")

# Label de status da VPN
vpn_status_label = tk.Label(frame_index, text="VPN Status: Desconectado", font=("Arial", 12))
vpn_status_label.pack(pady=(10, 0))

# Página Meu Code
code_label_atual = tk.Label(frame_code, text="Meu code atual é: ", font=("Arial", 12))
code_label_atual.pack(pady=(20, 5))

code_label = tk.Label(frame_code, text="Digite o novo Code:", font=("Arial", 12))
code_label.pack(pady=(10, 5))

code_entry = tk.Entry(frame_code, show="*", font=("Arial", 12))
code_entry.pack(pady=5)

botao_salvar = tk.Button(frame_code, text="Salvar Code", command=salvar_code, font=("Arial", 12))
botao_salvar.pack(pady=10)

botao_voltar = tk.Button(frame_code, text="Voltar", command=show_index, font=("Arial", 12))
botao_voltar.pack(pady=10)

# Página Login VPN
label_login = tk.Label(frame_loginvpn, text="Login VPN", font=("Arial", 24))
label_login.pack(pady=20)

label_usuario = tk.Label(frame_loginvpn, text="Usuário:", font=("Arial", 12))
label_usuario.pack()
entry_usuario = tk.Entry(frame_loginvpn, font=("Arial", 12))
entry_usuario.pack(pady=5)

label_senha = tk.Label(frame_loginvpn, text="Senha:", font=("Arial", 12))
label_senha.pack()
entry_senha = tk.Entry(frame_loginvpn, show="*", font=("Arial", 12))
entry_senha.pack(pady=5)

botao_login = tk.Button(frame_loginvpn, text="Conectar VPN", command=login_vpn, font=("Arial", 12))
botao_login.pack(pady=10)

botao_voltar_login = tk.Button(frame_loginvpn, text="Voltar", command=show_index, font=("Arial", 12))
botao_voltar_login.pack(pady=10)

# Inicia com a página index
frame_index.pack(fill='both', expand=True)

root.after(100, update_initial_vpn_status)

root.mainloop()