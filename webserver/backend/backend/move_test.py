from backend.controller.wobble import Wobble
from backend.controller.walk import Walk
from backend.controller.pupper.hardware_interface import Servo
from minipupper import CONF

CONF.minipupper.environment = 'minipupper'

hardware_interface = Servo()
wobble_controller = Wobble(hardware_interface)
walk_controller = Walk(hardware_interface)

wobble_controller.params['pitch'] = 10.0
wobble_controller.run = True

print(wobble_controller.params)
print(wobble_controller.run)
print(wobble_controller.hasChanged)

wobble_controller._run()