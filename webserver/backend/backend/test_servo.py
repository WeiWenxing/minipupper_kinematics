from backend.controller.pupper.hardware_interface import Servo
import time
import numpy as np
from backend.controller.gaits3D import GaitController3D
from minipupper import CONF

hardware_interface = Servo()

hardware_interface.set_servo_position(np.pi/4, 2, 0)  # range:  0-90