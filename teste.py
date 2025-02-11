import sys
from google_authenticator import GoogleAuthenticator

if len(sys.argv) != 2:
    print("Uso: python3 teste.py <secret>")
    sys.exit(1)

secret = sys.argv[1]
ga = GoogleAuthenticator(secret)

# Gerar código atual
code = ga.get_code()
print("Código atual:", code)