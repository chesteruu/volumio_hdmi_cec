import logging
from receiver_control import ReceiverController
import time
import threading


class TvController:
    TVCONTROLLER_OFF = -1
    TVCONTROLLER_ON = 0
    TVCONTROLLER_START = 1
    TVCONTROLLER_STARTING = 2

    def __init__(self, tv_device, rec_controller: ReceiverController):
        self.tv_device = tv_device
        self.state = TvController.TVCONTROLLER_OFF
        self.rec_controller = rec_controller

    def __turn_on(self):
        logging.info("TvController __turn_on")
        self.tv_device.power_on()

    def __turn_off(self):
        logging.info("TvController __turn_off")
        self.tv_device.stand_by()

    def __check_receiver(self):
        i = 1
        retry_times = 0

        while self.rec_controller.state != ReceiverController.RECEIVER_ON:
            time.sleep(1)
            logging.info(f"Waiting audio to be [ON]...{i}s")

            i += 1
            if i == 41:
                logging.info("Failed start audio, tv should start rec automatically.")
                i = 1
                if self.rec_controller.devices[5].is_on():
                    while self.rec_controller.state != ReceiverController.RECEIVER_ON:
                        time.sleep(1)
                        i += 1
                        if i >= 5:
                            i = 1

                    if self.rec_controller.state == ReceiverController.RECEIVER_ON:
                        break

                self.rec_controller.push_state(ReceiverController.RECEIVER_START)
                retry_times += 1
                if retry_times == 2:
                    logging.info("Give up...")
                    return

        self.rec_controller.go_to_home()
        self.rec_controller.go_to_optical()

    def __turn_on_rec(self):
        logging.info("TvController __turn_on_rec")

        check_rec_thread = threading.Thread(target=self.__check_receiver)
        check_rec_thread.start()

    def push_state(self, state):
        logging.info(f"TvController push_state, current state: {self.state} new state: {state}")
        if self.state == state:
            return

        if state == TvController.TVCONTROLLER_ON:
            if self.state == TvController.TVCONTROLLER_OFF:
                self.__turn_on_rec()
            self.state = state
            return

        if state == TvController.TVCONTROLLER_OFF:
            self.state = state
            return

        if state == TvController.TVCONTROLLER_START:
            if self.state == self.TVCONTROLLER_OFF:
                self.__turn_on()
                self.state = TvController.TVCONTROLLER_STARTING
            return
