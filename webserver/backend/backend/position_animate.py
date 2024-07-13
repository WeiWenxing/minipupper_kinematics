from backend.controller.pupper.hardware_interface import Servo
from position_static import protect_clip
import numpy as np
import time

hardware_interface = Servo()

theta_defaut = np.radians(45)
gamma_defaut = np.radians(-45)
theta = 0.6981317007977318
gamma = 1.0471975511965976

thet, gam = protect_clip(theta, gamma)
ani_num = 20
angles_theta = np.linspace(theta_defaut, thet, ani_num)
angles_gamma = np.linspace(gamma_defaut, gam, ani_num)

hardware_interface.set_servo_position(theta_defaut, 1, 0)  # range:  0-90
hardware_interface.set_servo_position(gamma_defaut, 2, 0)  # range:  -90-0
time.sleep(0.5)
for i in range(ani_num):
    hardware_interface.set_servo_position(angles_theta[i], 1, 0)  # range:  0-90
    hardware_interface.set_servo_position(angles_gamma[i], 2, 0)  # range:  -90-0
    hardware_interface.set_servo_position_done()
    time.sleep(0.072)