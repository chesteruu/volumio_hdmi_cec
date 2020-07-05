from receiver_control import ReceiverController
from tv_controller import TvController
import cec
import logging


def log_cb(event, level, time, message):
    logging.info("CEC Log message: {}".format(message))


class CecController:
    def __init__(self):
        cec.init()
        self.devices = cec.list_devices()
        self.rec_controller = ReceiverController(self.devices)
        self.tv_controller = TvController(self.devices[0], self.rec_controller)
        self.player_callback = None
        cec.add_callback(self.__event_callback, cec.EVENT_COMMAND)
        cec.add_callback(log_cb, cec.EVENT_LOG)

    def __event_callback(self, event, event_data):
        logging.info("{0} Received with data {1}".format(event, event_data))
        source = event_data["initiator"]
        opcode = event_data["opcode"]
        para = event_data["parameters"]
        if source == cec.CECDEVICE_AUDIOSYSTEM:
            if opcode == cec.CEC_OPCODE_REPORT_POWER_STATUS:
                if para == b'\x01':
                    self.rec_controller.push_state(ReceiverController.RECEIVER_OFF)
                    if self.player_callback is not None:
                        self.player_callback('stop')
                elif para == b'\x00':
                    self.rec_controller.push_state(ReceiverController.RECEIVER_ON)
                return
            if opcode == cec.CEC_OPCODE_SET_SYSTEM_AUDIO_MODE:
                if para == b'\x01':
                    self.rec_controller.push_state(ReceiverController.RECEIVER_ON)
                elif para == b'\x00':
                    self.rec_controller.push_state(ReceiverController.RECEIVER_OFF)
                    if self.player_callback is not None:
                        self.player_callback('stop')
                return
        if source == cec.CECDEVICE_TV:
            if opcode == cec.CEC_OPCODE_REPORT_POWER_STATUS:
                if para == b'\x01':
                    self.tv_controller.push_state(TvController.TVCONTROLLER_OFF)
                elif para == b'\x00':
                    self.tv_controller.push_state(TvController.TVCONTROLLER_ON)
                    if self.player_callback is not None:
                        self.player_callback('stop')
                return
            if opcode == cec.CEC_OPCODE_SET_MENU_LANGUAGE:
                self.tv_controller.push_state(TvController.TVCONTROLLER_ON)
                if self.player_callback is not None:
                    self.player_callback('stop')
                return
            if opcode == cec.CEC_OPCODE_ACTIVE_SOURCE:
                self.tv_controller.push_state(TvController.TVCONTROLLER_ON)
                if self.player_callback is not None:
                    self.player_callback('stop')
                return
            if opcode == cec.CEC_OPCODE_STANDBY:
                self.tv_controller.push_state(TvController.TVCONTROLLER_OFF)
                return

    def turn_on_receiver(self):
        self.rec_controller.push_state(ReceiverController.RECEIVER_START)

    def turn_off_receiver(self):
        self.rec_controller.push_state(ReceiverController.RECEIVER_GRACE_OFF)

    def get_current_power_state(self):
        self.devices[5].is_on()
        cec.transmit(cec.CECDEVICE_TV, cec.CEC_OPCODE_GIVE_DEVICE_POWER_STATUS, '')

    def is_audio_on(self):
        return self.rec_controller.state == ReceiverController.RECEIVER_ON

    def is_tv_on(self):
        return self.tv_controller.state == TvController.TVCONTROLLER_ON \
               or self.tv_controller.state == TvController.TVCONTROLLER_STARTING

    def init_audio_to_hdmi_1(self):
        self.rec_controller.go_to_home()
        self.rec_controller.go_to_hdmi_1()

    def init_audio_to_optical(self):
        self.rec_controller.go_to_home()
        self.rec_controller.go_to_optical()

    def set_player_call_back(self, call_back):
        self.player_callback = call_back
