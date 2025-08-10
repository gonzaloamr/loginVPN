# 👑 Login VPN Kinghost

## 📖 Sobre
Aplicação desktop desenvolvida em Python para gerenciamento automático de conexões VPN da Kinghost. O sistema integra autenticação por usuário/senha com Google Authenticator (2FA) para estabelecer conexões seguras via OpenVPN.

---

## 💻 Tecnologias Usadas

- **[Python 🐍](https://www.python.org/)** - Linguagem principal
- **Tkinter** - Interface gráfica
- **OpenVPN** - Cliente VPN
- **Google Authenticator** - Autenticação de dois fatores (2FA)
- **Subprocess** - Gerenciamento de processos do sistema

---

## 📂 Funcionalidades

- **🔐 Login VPN:** Conecta automaticamente à VPN usando credenciais + código 2FA
- **🔓 Logout VPN:** Desconecta da VPN de forma segura
- **📊 Status da VPN:** Exibe em tempo real o status da conexão (Conectado/Desconectado)
- **🔑 Gerenciamento de Códigos 2FA:** Interface para configurar e armazenar códigos do Google Authenticator
- **🛡️ Segurança:** Limpa automaticamente arquivos temporários de credenciais

---

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux** (testado no Ubuntu/Debian)
- **Sudo** habilitado para o usuário

### Dependências do Sistema
```bash
sudo apt update
sudo apt install openvpn python3 python3-tk
```

### Arquivos de Configuração VPN Necessários
Você precisa ter os seguintes arquivos fornecidos pela Kinghost:

1. **Arquivo de configuração (.ovpn)**
   - Exemplo: `VPN_DEV_SIS_INTERNOS_usuario.ovpn`
   - Contém as configurações do servidor VPN

2. **Chave TLS (.key)**
   - Exemplo: `VPN_DEV_SIS_INTERNOS_usuario-tls.key`
   - Chave privada para autenticação TLS

3. **Certificado PKCS#12 (.p12)**
   - Exemplo: `VPN_DEV_SIS_INTERNOS_usuario.p12`
   - Certificado cliente em formato PKCS#12

---

## 🛠️ Instalação e Configuração

### 1. Clone ou baixe os arquivos do projeto
```bash
git clone <repository-url>
cd loginVPN
```

### 2. Posicione os arquivos VPN
Copie seus arquivos de VPN para o diretório do projeto:
```bash
# Coloque os arquivos no mesmo diretório do projeto
cp /caminho/para/seus/arquivos/VPN_DEV_SIS_INTERNOS_usuario.ovpn ./
cp /caminho/para/seus/arquivos/VPN_DEV_SIS_INTERNOS_usuario-tls.key ./
cp /caminho/para/seus/arquivos/VPN_DEV_SIS_INTERNOS_usuario.p12 ./
```

### 3. Configure o arquivo vpn_config.txt
Edite o arquivo `vpn_config.txt` e adicione o nome do seu arquivo .ovpn:
```bash
echo "VPN_DEV_SIS_INTERNOS_usuario.ovpn" > vpn_config.txt
```

### 4. Configure o Google Authenticator
- Acesse a aplicação
- Vá em "Menu" > "Meu Code"
- Digite seu código secreto do Google Authenticator
- Salve o código

---

## 🚀 Como Usar

### 1. Executar a aplicação
```bash
python3 loginVPNKing.py
```

### 2. Configurar o código 2FA (primeira vez)
1. Clique em "Menu" > "Meu Code"
2. Digite seu código secreto do Google Authenticator
3. Clique em "Salvar Code"
4. Volte para a tela principal

### 3. Conectar à VPN
1. Clique em "Menu" > "Login VPN"
2. Digite seu usuário da VPN
3. Digite sua senha da VPN
4. Clique em "Conectar VPN"
5. O sistema irá:
   - Gerar automaticamente o código 2FA
   - Concatenar senha + código 2FA
   - Estabelecer a conexão VPN

### 4. Verificar status
- Na tela principal você verá: "VPN Status: Conectado" ou "VPN Status: Desconectado"

### 5. Desconectar da VPN
1. Clique em "Menu" > "Logout VPN"
2. Confirme a desconexão
3. Digite sua senha sudo quando solicitado

---

## 📁 Estrutura do Projeto

```
loginVPN/
├── loginVPNKing.py          # Interface principal da aplicação
├── vpn_manager.py           # Gerenciador de conexões VPN
├── google_authenticator.py  # Gerador de códigos 2FA
├── code.py                  # Armazena o código do Google Authenticator
├── vpn_config.txt          # Caminho para o arquivo .ovpn
├── img/
│   └── kinghost-favicon.png # Ícone da aplicação
├── README.md               # Este arquivo
├── VPN_DEV_SIS_INTERNOS_usuario.ovpn  # Seu arquivo de configuração VPN
├── VPN_DEV_SIS_INTERNOS_usuario-tls.key  # Sua chave TLS
└── VPN_DEV_SIS_INTERNOS_usuario.p12      # Seu certificado P12
```

---

## 🔧 Solução de Problemas

### Erro: "Arquivo OVPN não encontrado"
- Verifique se o arquivo .ovpn está no diretório do projeto
- Confirme se o nome no `vpn_config.txt` está correto

### Erro: "Nenhum code salvo"
- Configure o código do Google Authenticator em "Menu" > "Meu Code"

### Erro de permissão sudo
- Certifique-se de que seu usuário tem privilégios sudo
- Digite a senha sudo corretamente quando solicitado

### VPN não conecta
- Verifique se todos os arquivos de certificado estão presentes (.ovpn, .key, .p12)
- Confirme se as credenciais estão corretas
- Verifique os logs em `vpn_manager.log`

---

## 🔒 Segurança

- **Limpeza automática:** Arquivos temporários de credenciais são removidos automaticamente
- **Códigos 2FA:** Gerados dinamicamente a cada conexão
- **Privilégios sudo:** Solicitados apenas quando necessário
- **Logs:** Registros detalhados para auditoria (podem ser desabilitados)

---

## 📝 Notas Importantes

- ⚠️ **Mantenha seus arquivos de certificado seguros e não os compartilhe**
- ⚠️ **O código do Google Authenticator fica armazenado localmente**
- ⚠️ **Certifique-se de ter permissões sudo antes de executar**
- ✅ **O sistema para automaticamente o Apache2 durante a conexão VPN**
- ✅ **Processos OpenVPN antigos são finalizados automaticamente**

---

## 🤝 Suporte

Em caso de problemas:
1. Verifique os logs em `vpn_manager.log`
2. Confirme se todos os arquivos necessários estão presentes
3. Teste a conectividade manual com OpenVPN
4. Entre em contato com o suporte da Kinghost se necessário
