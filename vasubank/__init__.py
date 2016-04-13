from Crypto.PublicKey import RSA
from Crypto import Random
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
f = open('bank_public_key.pem','w')
f.write(key.publickey().exportKey('PEM'))
f.close()
f=open('/home/akash/vasu/bis2/VASU/bank_public_key.pem','r')
clg_public_key = RSA.importKey(f.read())
f.close()
