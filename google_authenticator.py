import hmac
import hashlib
import time
import struct
import base64
import os

class GoogleAuthenticator:
    def __init__(self, secret):
        self._code_length = 6
        self.secret = secret

    def create_secret(self, secret_length=16):
        return base64.b32encode(os.urandom(secret_length)).decode('utf-8').strip('=')

    def get_code(self, time_slice=None):
        if time_slice is None:
            time_slice = int(time.time() / 30)

        secret_key = base64.b32decode(self.secret.upper() + '=' * ((8 - len(self.secret) % 8) % 8))
        time_bytes = struct.pack('>Q', time_slice)
        
        hm = hmac.new(secret_key, time_bytes, hashlib.sha1).digest()
        offset = hm[-1] & 0x0F
        code = (struct.unpack('>I', hm[offset:offset+4])[0] & 0x7FFFFFFF) % (10 ** self._code_length)
        return str(code).zfill(self._code_length)