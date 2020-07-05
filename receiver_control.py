import threading
import cec
import logging
import time


class ReceiverController:
    RECEIVER_OFF = -1
    RECEIVER_GRACE_OFF = 0
    RECEIVER_STARTING = 1
    RECEIVER_ON = 2
    RECEIVER_START = 3

    def __init__(self, devices):
        logging.info("ReceiverController init.")
        self.state = ReceiverController.RECEIVER_OFF
        self.grace_off_timer = threading.Timer(20, self.__grace_off)
        self.check_timer = threading.Timer(30, self.__check_state)
        self.devices = devices

    def __turn_on(self):
        logging.info("ReceiverController __turn_on.")
        cec.transmit(cec.CECDEVICE_AUDIOSYSTEM,
                     cec.CEC_OPCODE_USER_CONTROL_PRESSED, b'\x40')
        if not self.check_timer.is_alive():
            self.check_timer = threading.Timer(45, self.__check_state)
            self.check_timer.start()


    def __turn_off(self):
        logging.info("ReceiverController __turn_off.")
        if self.state == ReceiverController.RECEIVER_GRACE_OFF:
            cec.transmit(cec.CECDEVICE_AUDIOSYSTEM,
                         cec.CEC_OPCODE_USER_CONTROL_PRESSED, b'\x40')

        self.devices[5].is_on()

    def __check_state(self):
        logging.info(f"ReceiverController __check_state. state: {self.state}")
        if self.state != ReceiverController.RECEIVER_STARTING:
            return

        cec.transmit(cec.CECDEVICE_AUDIOSYSTEM,
                     cec.CEC_OPCODE_USER_CONTROL_PRESSED, b'\x40')
        self.check_timer = threading.Timer(45, self.__check_state)
        self.check_timer.start()

    def __grace_off(self):
        logging.info(f"ReceiverController __grace_off. state: {self.state}")
        if not self.state == ReceiverController.RECEIVER_GRACE_OFF:
            return

        self.__turn_off()

    def go_to_home(self):
        logging.info(f"ReceiverController go_to_home. state: {self.state}")
        if self.state != ReceiverController.RECEIVER_ON:
            return

        cec.transmit(cec.CEC_DEVICE_TYPE_AUDIO_SYSTEM, cec.CEC_OPCODE_USER_CONTROL_PRESSED, b'\x44')
        time.sleep(4)

    def go_to_hdmi_1(self):
        logging.info(f"ReceiverController go_to_home. state: {self.state}")
        if self.state != ReceiverController.RECEIVER_ON:
            return

        for i in range(0, 4):
            logging.info(f'Change input button hit [{i}] times')
            cec.transmit(cec.CEC_DEVICE_TYPE_AUDIO_SYSTEM, cec.CEC_OPCODE_USER_CONTROL_PRESSED, b'\x34')
            time.sleep(2.8)

    def go_to_optical(self):
        logging.info(f"ReceiverController go_to_optical. state: {self.state}")

        if self.state != ReceiverController.RECEIVER_ON:
            return

        for i in range(0, 8):
            logging.info(f'Change input button hit [{i}] times')
            cec.transmit(cec.CEC_DEVICE_TYPE_AUDIO_SYSTEM, cec.CEC_OPCODE_USER_CONTROL_PRESSED, b'\x34')
            time.sleep(2.8)

    def push_state(self, state):
        logging.info(f"ReceiverController push_state. current state: {self.state} new state: {state}")
        if self.state == state:
            return

        if state == ReceiverController.RECEIVER_ON:
            if self.state == ReceiverController.RECEIVER_STARTING:
                self.check_timer.cancel()

            if self.state == ReceiverController.RECEIVER_GRACE_OFF:
                return

            self.state = ReceiverController.RECEIVER_ON
        elif state == ReceiverController.RECEIVER_OFF:
            if self.state == ReceiverController.RECEIVER_STARTING:
                self.__turn_on()
                return

            self.state = ReceiverController.RECEIVER_OFF
            self.check_timer.cancel()
            self.grace_off_timer.cancel()
        elif state == ReceiverController.RECEIVER_GRACE_OFF:
            if self.state == ReceiverController.RECEIVER_STARTING:
                self.state = ReceiverController.RECEIVER_OFF
                self.__turn_off()
                return

            if self.state == ReceiverController.RECEIVER_OFF or self.state == ReceiverController.RECEIVER_GRACE_OFF:
                return

            if not self.grace_off_timer.is_alive():
                self.grace_off_timer = threading.Timer(30, self.__grace_off)

            self.grace_off_timer.start()
            self.state = ReceiverController.RECEIVER_GRACE_OFF
        elif state == ReceiverController.RECEIVER_START:
            if self.state == ReceiverController.RECEIVER_ON or self.state == ReceiverController.RECEIVER_STARTING:
                return

            if self.state == ReceiverController.RECEIVER_GRACE_OFF:
                self.grace_off_timer.cancel()
                self.state = ReceiverController.RECEIVER_ON
                return

            self.check_timer.cancel()
            self.__turn_on()
            self.state = ReceiverController.RECEIVER_STARTING



