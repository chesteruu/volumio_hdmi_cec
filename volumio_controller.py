from socketIO_client import SocketIO
import time
import logging
import os
from hdmi_system_controller import CecController

logging.Formatter.converter = time.gmtime
logging.basicConfig(filename='/var/log/hdmi-cec.log', format='%(asctime)s %(message)s',
                    filemode='w', level=os.environ.get("AF_LOGLEVEL", "INFO"))


class VolumioController:
    PLAYER_PLAY = 'play'
    PLAYER_STOP = 'stop'

    def __init__(self, hdmi_controller: CecController):
        self.controller = hdmi_controller
        self.controller.set_player_call_back(self.push_player_state)
        self.socketIO = SocketIO('volumio.local', 3000)
        self.socketIO.connect()
        self.socketIO.on('pushState', self.__on_push_state)

    def start(self):
        self.socketIO.wait()

    def push_player_state(self, state):
        self.socketIO.emit(state)

    def __on_push_state(self, status_info: dict, **args):
        logging.info(f"Volumio state change to {status_info['status']}")
        if status_info['status'] == 'play':
            self.controller.turn_on_receiver()
            is_first_time = False
            i = 1
            while not controller.is_audio_on():
                time.sleep(1)
                logging.info(f"Waiting audio to be [ON]...{i}s")
                is_first_time = True
                i += 1
                if i == 41:
                    logging.info("Failed start audio")
                    return

            if is_first_time:
                self.controller.init_audio_to_hdmi_1()

            return

        if status_info['status'] == 'pause' or status_info['status'] == 'stop':
            if not self.controller.is_tv_on():
                self.controller.turn_off_receiver()
            return


controller = CecController()
controller.get_current_power_state()
volumio = VolumioController(controller)
volumio.start()