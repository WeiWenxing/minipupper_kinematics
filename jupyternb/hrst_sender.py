import socket
import time
import numpy as np

class SocketSender:
	def __init__(self, HOST):
		self.HOST = HOST
		self.PORT = 8001
		self.text = []

	def send_pushup_command(self, command, theta = -3*np.pi/4, gamma = np.pi/2, delta = 0.02):
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			# 连接到服务器
			client_socket.connect((self.HOST, self.PORT))
			print(f"Connected to server {self.HOST}:{self.PORT}")

			modified_command = ''
			if command == 'PushUp':
				self.text = [str(theta), str(gamma), str(delta)]
				content = '|'.join(self.text)
				modified_command = f"PushUp {content}"

				# 发送命令
				client_socket.sendall(modified_command.encode())
				print(f"Sent command: {modified_command}")
			else:
				client_socket.sendall(command.encode()) 

		except socket.error as e:
			print(f"Socket error: {e}")
		finally:
			# 关闭连接
			client_socket.close()
			print("Connection closed")