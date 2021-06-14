import serial
import time
import math as m

from geocom_dicts import *
from logger import log


GON2RAD = m.pi/200


class SerialConnection:
    def __init__(self, port, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1):

        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

        self.ser = None
        self.establish_serial_connection()

    def establish_serial_connection(self):
        # blocking until serial connection is established
        while True:
            if self.ser is not None:
                if self.ser.is_open:
                    self.ser.close()

            log.info("Trying to open serial connection on port " + self.port)

            try:
                self.ser = serial.Serial(self.port, baudrate=self.baudrate, parity=self.parity, stopbits=self.stopbits,
                                         timeout=self.timeout)
                log.info("Successfully opened serial connection on port " + self.port)
                break
            except (serial.serialutil.SerialException, ):
                time.sleep(2)

    def reset_serial_connection(self):
        log.error("Resetting serial connection")
        try:
            self.ser.readall()
        except:
            pass
        try:
            self.establish_serial_connection()
            return True
        except:
            log.error("Could not reopen port after resetting serial connection")
        return False

    def send(self, string):
        try:
            self.ser.write(string.encode("UTF-8"))
            return True
        except serial.serialutil.SerialException:
            log.error("USB unplugged!")
            self.establish_serial_connection()
            return False

    def receive(self, rsp_amount, timeout=10):
        result_string = []

        start_time = time.time()
        while start_time + timeout > time.time():
            try:
                char = self.ser.read(1).decode("UTF-8")
            except (UnicodeDecodeError, ):
                char = False
            except (serial.serialutil.SerialException, ):
                log.error("USB unplugged!")
                self.establish_serial_connection()
                return False

            if char:
                result_string.append(char)

                if char == '\n':
                    break
        else:
            log.error("Geocom Timeout, no response")
            return False

        try:
            return_list = ''.join(result_string)[:-2].split(':')[1].split(',')

            if len(return_list) == rsp_amount:
                return return_list
            else:
                log.error("Geocom response length missmatch " + str(len(return_list)) + "!=" + str(rsp_amount))
                return False
        except:  # TODO errors .. IndexError
            log.error("Geocom response index error")
            return False


class GeoCom:
    def __init__(self, sercon):
        self.sercon = sercon

    def save_send_and_receive(self, string, rsp_amount, retry_amount=3, timeout=10):
        while retry_amount:
            if self.sercon.send(string):
                recv = self.sercon.receive(rsp_amount, timeout=timeout)
                if recv:
                    return recv
                else:
                    if not self.sercon.reset_serial_connection():
                        return False
                    log.error("Retrying command")
            retry_amount -= 1

        log.error("Geocom did not receive response")
        return False

    def BAP_SetPrismType(self, prismtype):
        return self.save_send_and_receive("%R1Q,17008:" + str(prismtype) + "\r\n", 1, timeout=1)

    def BAP_SetTargetType(self, targettype):
        return self.save_send_and_receive("%R1Q,17021:" + str(targettype) + "\r\n", 1, timeout=1)

    def TMC_SetInclineSwitch(self, on_off_type):
        return self.save_send_and_receive("%R1Q,2006:" + str(on_off_type) + "\r\n", 1, timeout=1)

    def TMC_SetAtmPpm(self, dppma):
        # %R1Q,2148:
        return self.save_send_and_receive("%R1Q,2148:" + str(dppma) + "\r\n", 1, timeout=1)

    def AUS_SetUserAtrState(self, on_off_type):
        return self.save_send_and_receive("%R1Q,18005:" + str(on_off_type) + "\r\n", 1, timeout=1)

    def AUT_MakePositioning(self, hz, v, posmode, atrmode, bDummy=BOOLE[False]):
        return self.save_send_and_receive("%R1Q,9027:" + str(hz*GON2RAD) + ',' + str(v*GON2RAD) + ',' + str(posmode) + ',' + str(atrmode) + ',' + str(bDummy) + "\r\n", 1, timeout=15)

    def AUT_FineAdjust(self, dSrchHz, dSrchV, bDummy=BOOLE[False]):
        return self.save_send_and_receive("%R1Q,9037:" + str(dSrchHz*GON2RAD) + ',' + str(dSrchV*GON2RAD) + ',' + str(bDummy) + "\r\n", 1, timeout=15)

    def TMC_DoMeasure(self, command, mode):
        return self.save_send_and_receive("%R1Q,2008:" + str(command) + ',' + str(mode) + "\r\n", 1, timeout=15)

    def TMC_GetFullMeas(self, waittime, mode):
        # waittime in ms
        return self.save_send_and_receive("%R1Q,2167:" + str(waittime) + ',' + str(mode) + "\r\n", 9, timeout=15)

    def TMC_GetAngle1(self, mode):
        return self.save_send_and_receive("%R1Q,2003:" + str(mode) + "\r\n", 10, timeout=15)

    def TMC_GetAngle5(self, mode):
        return self.save_send_and_receive("%R1Q,2107:" + str(mode) + "\r\n", 5, timeout=15)

    def BAP_SetMeasPrg(self, emeasprg):
        return self.save_send_and_receive("%R1Q,17019:" + str(emeasprg) + "\r\n", 1, timeout=15)

    def TMC_SetEdmMode(self, mode):
        return self.save_send_and_receive("%R1Q,2020:" + str(mode) + "\r\n", 1, timeout=15)

    def CSV_GetIntTemp(self):
        return self.save_send_and_receive("%R1Q,5011:\r\n", 2, timeout=4)
