import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random
from base64 import b64decode


def getHash(str):
    hashcode = hashlib.sha256()
    hashcode.update(bytes(str, encoding='utf-8'))
    return hashcode.hexdigest()


def generate_key():
    rsa = RSA.generate(1024)
    private_key = rsa.exportKey()
    publick_key = rsa.publickey().exportKey()
    return private_key.decode(), publick_key.decode()


def rsa_encrypt(public_key, message):
    public_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_v1_5.new(public_key)
    return cipher_rsa.encrypt(str.encode(message))


def rsa_decrypt(private_key, message):
    dsize = SHA.digest_size
    sentinel = Random.new().read(1024 + dsize)
    private_key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_v1_5.new(private_key)
    return cipher_rsa.decrypt(b64decode(message), sentinel)




