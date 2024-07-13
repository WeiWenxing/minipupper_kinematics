from backend.controller.pupper.hardware_interface import Servo
import subprocess
import socket
import time


HOST = '0.0.0.0'
PORT = 8001
hardware_interface = Servo()

class JupyterServer:

    def __init__(self):
        self.process_running = False
        self.current_process = None

    def handle_command(self, command):
        if command.startswith("1D"):
            try:
                parts = command.split(' ', 1)
                contents = parts[1].split('|')
                with open('./1D_execute.py', 'r') as f:
                    lines = f.readlines()
                    new_line1 ='theta = np.radians(' + contents[0] + ')\n'
                    new_line2 ='gamma = np.radians(' + contents[1] + ')\n'
                    lines[4] = new_line1
                    lines[5] = new_line2
                with open('./1D_execute.py', 'w') as f:
                    f.writelines(lines)
            except Exception as e:
                return f"Failed: {e}"
            try:
                self.current_process = subprocess.Popen(['python', './1D_execute.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return f"Process Started"
            except Exception as e:
                return f"Failed to run: {e}"            
        elif command.startswith('ANI'):
            parts = command.split(' ', 1)
            contents = parts[1].split('|')
            with open('./1D_animate.py', 'r') as f:
                lines = f.readlines()
                replace1 = 'theta = ' + contents[0] + '\n'
                replace2 = 'gamma = ' + contents[1] + '\n'
                lines[8] = replace1
                lines[9] = replace2
            with open('./1D_animate.py', 'w') as f:
                f.writelines(lines)
            self.current_process = subprocess.Popen(['python', './1D_animate.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.process_running = True
            return f"Process Started"
        elif command.startswith("PushUp"):
            try:
                parts = command.split(' ', 1)
                contents = parts[1].split('|')
                with open('./2D_execute.py', 'r+') as f:
                    lines = []
                    for i in range(5):
                        line = f.readline()
                        lines.append(line)
                    f.seek(len(''.join(lines)))
                    f.truncate()
                    f.write('theta = ' + contents[0] + '\n')
                    f.write('gamma = ' + contents[1] + '\n')
                    f.write('delta = ' + contents[2] + '\n')

                    append_line = []
                    append_line.append('ik = IK_Control([theta, gamma], delta)')
                    append_line.append('ik.InProgress = True')
                    append_line.append('ik.runLoop(hardware_interface)')
                    for line in append_line:
                        f.write(line + '\n')
                            
                try:
                    self.current_process = subprocess.Popen(['python', './2D_execute.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    self.process_running = True
                    return f"Process started"
                except Exception as e:
                    return f"Failed to start process: {e}"
            except Exception as e:
                return f"Failed to run: {e}"
        elif command.startswith('Walk') and not self.process_running:
            try:
                parts = command.split(' ', 1)
                contents = parts[1].split('|')
                with open('./3D_execute.py', 'r') as f:
                    lines = f.readlines()
                    new_lines = []
                    new_lines.append('frequency = ' + contents[0] + '\n')
                    new_lines.append('gc.step_length = ' + contents[1] + '\n')
                    new_lines.append('gc.step_height = ' + contents[2] + '\n')
                    new_lines.append('gc.number_of_points = ' + contents[3] + '\n')
                    new_lines.append("params['vel_x'] = " + contents[4] + '\n')
                    new_lines.append("params['vel_y'] = " + contents[5] + '\n')
                    lines[13:19] = new_lines
                with open('./3D_execute.py', 'w') as f:
                    f.writelines(lines)
            except Exception as e:
                return f"failed: {e}"
                        
            try:
                self.current_process = subprocess.Popen(['python', './3D_execute.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                self.process_running = True
                return f"Process Started"
            except Exception as e:
                return f"Failed to run: {e}"
        elif command == 'Stop':
            if self.process_running:
                self.current_process.terminate()
                self.current_process = None
                self.process_running = False
    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f"server listening on {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            time.sleep(0.1)
                            break
                        command = data.decode().strip()
                        print('received command: {command}')
                        if self.process_running and command != 'STOP':
                            if self.current_process.poll() is None:
                                response = "Current Process is still running, please wait."
                                conn.sendall(response.encode())
                                break
                            else:
                                self.process_running = False
                                self.current_process = None
                        print(f"Received command: {command}")
                        response = self.handle_command(command)
                        conn.sendall(response.encode())
                        if command == "STOP":
                            break
                    print(f"Connection with {addr} closed")

if __name__ == "__main__":
    server = JupyterServer()
    server.server()