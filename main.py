"""
authors: Manuel Theurl and Marco Guerentz
year: 2021
"""

import datetime as dt

from geocom import SerialConnection, GeoCom, GON2RAD
from geocom_dicts import *
from auto_measure_handler import HandlerAutoMeasurement, Aim
from logger import log

# CONFIGURATIONS
DEFAULT_MEASUREMENT_FILE = None  # or e.g. "setup_05122021_133612.txt"
USB_PORT = "/dev/ttyUSB0"


class Manager:
    def __init__(self):
        self.__port = USB_PORT  # first port on raspb

        self.sercon = SerialConnection(self.__port)
        self.geocom = GeoCom(self.sercon)

        self.handler_auto_measure = HandlerAutoMeasurement(self.geocom)

        self.handler_auto_measure.initialize()

        self.__setup_file_path = "setup_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

        self.set_amount = None
        self.measure_interval = None

    def run(self):
        self.get_targets_and_configuration()
        self.add_second_circle()
        self.auto_measure()

    def read_setup_file(self, filename):
        with open(filename, 'r') as f:
            for line in f.readlines():
                if not line.startswith('#'):
                    splitted_line = line.split()
                    if splitted_line:
                        self.handler_auto_measure.aims.append(
                            Aim(splitted_line[0], float(splitted_line[1]), float(splitted_line[2]),
                                int(splitted_line[3]), int(splitted_line[4])))

    def get_targets_and_configuration(self):
        while True:
            if DEFAULT_MEASUREMENT_FILE is not None:
                path_to_setup_file = DEFAULT_MEASUREMENT_FILE
                self.read_setup_file(path_to_setup_file)
                log.info("Finished reading setup file")
                break
            else:
                new_target_name = input("Aim for target, enter aim name and confirm when ready or 'file' for entering setup file ('exit' for finished)\n")

                if new_target_name == "exit":
                    break
                elif not new_target_name:
                    continue
                elif new_target_name == "file":
                    path_to_setup_file = input("Input full path of file\n")
                    self.read_setup_file(path_to_setup_file)
                    log.info("Finished reading setup file")
                    break

                rsp = self.geocom.TMC_GetAngle1(TMC_INCLINE_PRG["TMC_AUTO_INC"])
                if not rsp:
                    exit("Cannot read angles, closing program, check cables and everything")
                hz, v = float(rsp[1])/GON2RAD, float(rsp[2])/GON2RAD

                log.info("Set hz " + str(round(hz, 4)) + "g, set v " + str(round(v, 4)) + "g")

                while True:
                    new_target_type = input("Select Target from " + str(BAP_TARGET_TYPE) + "\n")
                    try:
                        if int(new_target_type) in BAP_TARGET_TYPE.values():
                            log.info("Target set to " + str(new_target_type))
                            break
                        else:
                            log.warning("Number not in values")
                    except ValueError:
                        log.warning("Wrong input, enter the number for the value here")

                if int(new_target_type) == BAP_TARGET_TYPE["BAP_REFL_USE"]:
                    while True:
                        new_prism_type = input("Select Pirsm from " + str(PrismType) + "\n")
                        try:
                            if int(new_prism_type) in PrismType.values():
                                log.info("Prism set to " + str(new_prism_type))
                                break
                            else:
                                log.warning("Number not in values")
                        except ValueError:
                            log.warning("Wrong input, enter the number for the value here")
                else:
                    new_prism_type = -1  # not defined

                self.handler_auto_measure.aims.append(Aim(new_target_name, float(hz), float(v), int(new_target_type), int(new_prism_type)))

            with open(self.__setup_file_path, 'a+') as f:
                f.write(new_target_name + ' ' + str(hz) + ' ' + str(v)  + ' ' + str(new_target_type)  + ' ' + str(new_prism_type) + "\n")

        set_amount = input("Enter amount of sets to measure or press enter for infinite amount of sets\n")
        if set_amount:
            self.set_amount = int(set_amount)

        measurement_interval = input("Enter measurement interval in minutes or press enter for continuous measuring\n")
        if measurement_interval:
            self.measure_interval = int(measurement_interval) * 60

    def add_second_circle(self):
        self.handler_auto_measure.add_second_circle()

    def auto_measure(self):
        self.handler_auto_measure.run(interval=self.measure_interval, set_amount=self.set_amount)


program = Manager()

try:
    program.run()
except KeyboardInterrupt:
    program.handler_auto_measure.go_home()
    program.handler_auto_measure.upload_measurement_files_and_log()
    print("Closing program, goodbye from Marco and Manuel ;-)")
