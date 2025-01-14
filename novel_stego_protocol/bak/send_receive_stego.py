import sys
import socket
import select
import os
from Crypto.Cipher import AES

KEY = b'Sixteen byte key'
key = 'Sixteen byte key'
cipher = AES.new(key, AES.MODE_EAX)
nonce = cipher.nonce
print(nonce)


def chat_client():
	# if(len(sys.argv) < 3) :
	#    print('Usage : python chat_client.py hostname port')
	#    sys.exit()

	# Default Parameters:
	default = input("Use default settings for IP and port settings? [y/N]: ")

	if default != 'y':
		# For sake of good UI
		host = str(input("Chat room IP: "))
		port = int(input("Chat room port: "))
	else:
		host = 'localhost'
		port = 9009

	KEY = b''
	#while not (len(KEY) == 16 or len(KEY) == 24 or len(KEY) == 32):
		#print('\tError: Key Length is Incorrect, enter key with length 16, 24, or 32.')
	#KEY = input("Encryption key: ")

	verbose = input('Do you want to turn on verbose mode? [y/N]: ')
	if verbose == 'y':
		verbose = True
	else:
		verbose = False

	os.system('clear')
	# port = int(sys.argv[2])
	print("+-+-+-+ Welcome to SteganoChat +-+-+-+\n"
		  + "*** If you want to hide something ****\n"
		  + "*** important from the government ****\n"
		  + "*** we're here to help you.       ****\n"
		  + "-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
		  + "*** Connecting to chat room...    ****\n"
		  + "-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)

	# connect to remote host
	try:
		s.connect((host, port))
	except:
		print('Unable to connect')
		sys.exit()

	print('&&&                                &&&\n'
		  + '*** Connected to remote chatroom. ****\n'
		  + '*** Start securely messaging now! ****\n'
		  + '-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
	sys.stdout.write('[Me] ');
	sys.stdout.flush()

	while 1:
		socket_list = [sys.stdin, s]

		# Get the list sockets which are readable
		ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])

		for sock in ready_to_read:
			if sock == s:
				# incoming message from remote server, s
				data = sock.recv(4096)
				if not data:
					print('\nDisconnected from chat server')
					sys.exit()
				else:
					# print data
					process_packet(data, KEY, verbose)
					sys.stdout.write('[Me] ');
					sys.stdout.flush()

			else:
				# user entered a message
				msg = sys.stdin.readline().replace('\n', '')

				send_packet(msg, s, KEY, verbose)

				sys.stdout.write('[Me] ');
				sys.stdout.flush()


def send_packet(msg, socket, key, verbose):
	ctxt, nonce = encrypt(msg, key)
	nonce_and_ctxt = nonce + bytes('|||') + ctxt

	# Do stego magic on the nonce_and_ctxt variable
	# stego_text = apply_stego(nonce_and_ctxt)
	stego_text = nonce_and_ctxt

	# If verbose mode turned on show all info.
	if verbose:
		print('\tSending Message: %s' % msg)
		print('\tCipherText: %s' % ctxt)
		print('\tNonce: %s' % nonce)
		print('\tData to be sent: %s' % nonce_and_ctxt)
		print('\tStego Transformed Text: %s' % stego_text)
		print('')

	socket.send(stego_text)
	return None


def process_packet(data, key, verbose):
	# I don't know why but the nonce|||ciphertext which one client sends gets pre-appended with IP and Port
	# In order to combat this here's some messy code
	# When applying stego, it might glitch out so try to print them out to make sure everything is ok
	#
	# print(data)
	intro_end_idx = data.index(']')
	intro, stego_data = data[:intro_end_idx + 2], data[intro_end_idx + 2:]
	# print(intro, stego_data)

	# Do some stego magic to revert the packet sent to us to original data
	# orig_data = revert_stego(stego_data)
	orig_data = stego_data

	try:
		split_intro_nonce_and_ctxt = orig_data.split(b'|||')
		if len(split_intro_nonce_and_ctxt) < 2:
			sys.stdout.write(orig_data)
			return None

		# Once again pls make sure it's doing correctly, to debug turn on verbose mode on both clients and commpare
		# the two debug outputs
		nonce, ctxt = split_intro_nonce_and_ctxt[0], split_intro_nonce_and_ctxt[1]
		# print(nonce)
		# print(ctxt)

	except:
		sys.stdout.write('Packet Error: Data received was not valid\n')
		return None

	if verbose:
		print('\nReceived Text:')
		print(stego_data)
		print('Stego-text transformed back to original data:')
		print(orig_data)
		print('CipherText: %s' % ctxt)
		print('Nonce: %s' % nonce)

	message = '\n' + intro + 'sent a message:' + decrypt(ctxt, key, nonce) + '\n'

	print(message)
	return None


def encrypt(message, key):
	"""
	Input:
		message: string
		key: bytes/bytearray/memoryview (Must be 16, 24, or 32 bytes long)
	Output:
		ciphertext: bytes
		tag:
	"""

	#if not (len(key) == 16 or len(key) == 24 or len(key) == 32):
	#	print('Key Length Incorrect (length: %s)' % len(key))
	#	print('Exiting Encryption Method...')
	#	return None

	data = message.encode()
	cipher = AES.new(key, AES.MODE_CTR)
	ct_bytes = cipher.encrypt(data)
	nonce = cipher.nonce

	return (ct_bytes, nonce)


def decrypt(ciphertext, key, nonce):
	try:
		cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
		plaintext_bytes = cipher.decrypt(ciphertext)
		plaintext = plaintext_bytes.decode('utf-8')
		return plaintext
	except Exception:
		print("Incorrect decryption")
		return None


if __name__ == "__main__":
	sys.exit(chat_client())
