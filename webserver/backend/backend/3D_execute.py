from backend.controller.pupper.hardware_interface import Servo
from backend.controller.gaits3D import GaitController3D
from minipupper import CONF
import numpy as np
import time

hardware_interface = Servo()
CONF.minipupper.environment == 'minipupper'
gc = GaitController3D()

params = {}
gait_plan = []

frequency = 1./10
gc.step_length = 0.04
gc.step_height = 0.02
gc.number_of_points = 20
params['vel_x'] = 0.5
params['vel_y'] = 0.5

def _setGaitPlan(gc, params):
    angle = np.arctan2(params['vel_y'], params['vel_x'])
    speed = max(abs(params['vel_x']), abs(params['vel_y']))
    gait_plan = gc._gait_plan(angle, 'walk', speed)
    if CONF.minipupper.environment == 'minipupper':
        for k in range(len(gait_plan[0])):
            for i in range(len(gc.legs)):
                gait_plan[i][k][2] = gait_plan[i][k][1] + gait_plan[i][k][2]
    return gait_plan

def _run(gc, gait_plan, hardware_interface, frequency = 1./120, i = 0):
        for k in range(len(gait_plan[0])):
            for j in range(len(gc.joints)):
                hardware_interface.set_servo_position(gait_plan[i][k][j], j, i)
            hardware_interface.set_servo_position_done()
            time.sleep(frequency)

gait_plan = _setGaitPlan(gc, params)

while True:
    _run(gc, gait_plan, hardware_interface, frequency)
    print(gait_plan[0].shape)


