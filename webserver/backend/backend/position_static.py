from backend.controller.pupper.hardware_interface import Servo
import numpy as np
hardware_interface = Servo()

theta = 0.5235987755982988
gamma = 0.7853981633974483

def protect_clip(theta, gamma):
    theta_mod = np.pi/2 - theta
    theta_final = np.clip(theta_mod, np.radians(-45), np.radians(135))
    gamma_final = 0
    #gamma的第一层限制，小腿相对于大腿的旋转角度不可以小于0度，也不可以大于180度，由于机械结构限制调整为45度到135度
    gamma_mod = np.clip(gamma, np.radians(45), np.radians(135))
    gamma_mod = - gamma_mod + theta_final
    #第二层限制， 小腿相对于y轴的绝对角度与大腿的旋转角度存在限制关系
    if theta_final < np.radians(45):
        gamma_final = np.clip(gamma_mod, np.radians(-90), theta_final-np.radians(45))
    else:
        gamma_final = np.clip(gamma_mod, theta_final - np.radians(135), np.radians(0))
    return theta_final, gamma_final
thet, gam = protect_clip(theta, gamma)
print(thet * 57.3)
print(gam * 57.3)
hardware_interface.set_servo_position(thet, 1, 0)
hardware_interface.set_servo_position(gam, 2, 0)
hardware_interface.set_servo_position_done()
