from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


sk ="2321321df"
iv= "421321edf"
msg = "hi im bob"
cipher = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
encryptor = cipher.encryptor()
ct = encryptor.update(msg.encode()) + encryptor.finalize()
print(ct)
