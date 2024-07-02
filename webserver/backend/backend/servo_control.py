from backend.controller.pupper.hardware_interface import Servo
import time
import numpy as np
from minipupper import CONF

hardware_interface = Servo()

class IK_Control:

    def __init__(self, angle = [-3*np.pi/4, np.pi/2], delta = 0.02):
        self.theta = angle[0]
        self.gamma = angle[1]
        self.delta = delta
        self.InProgress = False

# for Minipupper write function for forward kinematic using only np
    def transformationMatrix(self, angle, l):
        c = np.cos(angle)
        s = np.sin(angle)
        return np.array([[c, -s, l*c], [s, c, l*s], [0, 0, 1]])
    def mpForwardKin(self, angles):
        lu = 0.05022511821787979 # from urdf
        ll = 0.065 # measured, includes the rubber foot
        T1 = self.transformationMatrix(angles[0], lu)
        T2 = self.transformationMatrix(angles[1], ll)
        T3 = T1.dot(T2)
        P1 = T1.dot(np.array([0,0,1]))[0:2]
        P2 = T3.dot(np.array([0,0,1]))[0:2]
        return np.array([[0, P1[0], P2[0]], [0, P1[1], P2[1]]])

    def mpInverseKin(self, point):
        lu = 0.05022511821787979 # from urdf
        ll = 0.065 # measured, includes the rubber foot
        gam = np.arccos((point[0]**2+point[1]**2-lu**2-ll**2)/(2*lu*ll))
        B = np.array(point)
        A11 = lu + ll * np.cos(gam)
        A12 = -ll * np.sin(gam)
        A21 = ll * np.sin(gam)
        A22 = lu + ll * np.cos(gam)

        A = np.array([[A11, A12], [A21, A22]])
        X = np.linalg.inv(A).dot(B)
        thet = np.arctan(X[1]/X[0])
        # correction for 2nd and 3rd quadrant
        # we assume -np.pi/4 <= thet <= -3*np.pi/4 
        if thet > -np.pi/4:
            thet = thet - np.pi
        return [thet, gam]

    def set_points(self):
        midpoint = self.mpForwardKin([self.theta, self.gamma])[:,2]
        N = 20 # number of points
        line = np.linspace(midpoint[1]-self.delta, midpoint[1]+self.delta, num=N)

        # create points there to position the foot. We construct a loop and make sure the end points are only hit once
        points = np.full((2, 2*N-2), midpoint[0])
        points[1][0:N] = line
        points[1][N:] = np.flip(line)[1:N-1]

        leg_servo_positions = []
        for j in range(2*N-2):
            leg_servo_positions.append(self.mpInverseKin(points[:,j]))
        angle_position = np.zeros((2*N-2, 2))
        for i in range(len(leg_servo_positions)):        
            leg_servo_positions[i][1] = leg_servo_positions[i][1] + leg_servo_positions[i][0]
            leg_servo_positions[i][0] = np.pi + leg_servo_positions[i][0]
            for j in range(2):
                angle_position[i][j] += leg_servo_positions[i][j] * 57.32
        return leg_servo_positions
    def runLoop(self, hardware_interface):
        loop_trajectory = self.set_points()
        while True:
            if self.InProgress == True:
                for k in range(len(loop_trajectory)):
                    hardware_interface.set_servo_position(loop_trajectory[k][0], 1, 0)  # range:  0-90
                    hardware_interface.set_servo_position(loop_trajectory[k][1], 2, 0) # range: -90-0
                    hardware_interface.set_servo_position_done()
                    time.sleep(0.07)
            else:
                hardware_interface.set_servo_position(np.pi/4, 1, 0)  # range:  0-90
                hardware_interface.set_servo_position(-np.pi/4, 2, 0) # range: -90-0
                hardware_interface.set_servo_position_done()



if __name__ == "__main__":
    ik_control = IK_Control()
    leg_servo_positions = ik_control.set_points()
    while True:
        for k in range(len(leg_servo_positions)):
            hardware_interface.set_servo_position(leg_servo_positions[k][0], 1, 0)  # range:  0-90
            hardware_interface.set_servo_position(leg_servo_positions[k][1], 2, 0) # range: -90-0
            hardware_interface.set_servo_position_done()
            time.sleep(0.05)
