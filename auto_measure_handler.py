import time
import copy
import datetime as dt
import os
import pysftp

from geocom import GeoCom
from geocom_dicts import *
from geocom import GON2RAD
from logger import log


MEASUREMENT_FOLDER = "measurements/"
COMPENSATOR_CHILL_TIME = 2


class Aim:
    def __init__(self, name, hz, v, target: BAP_TARGET_TYPE, prism: PrismType):
        self.name = name
        self.hz = hz
        self.v = v
        self.target = target
        self.prism = prism


class HandlerAutoMeasurement:
    def __init__(self, geocom: GeoCom):
        self.geocom = geocom
        self.aims = []
        self.last_start_time = None

        self.current_measurement_file_name = MEASUREMENT_FOLDER + dt.datetime.now().strftime("%Y%m%d") + ".txt"

        if not os.path.isdir(MEASUREMENT_FOLDER):
            os.mkdir(MEASUREMENT_FOLDER)
            with open(MEASUREMENT_FOLDER + "README.txt", 'w') as f:
                f.write("One Measurement file for each day is created. The format is given by\n"
                        "str_datetime str_aim_name str_hz_angle[g] str_hz_angle_raw[g] str_v_angle[g] str_v_angle_raw[g]"
                        " str_slope_dist[m] str_cross_incline[g] str_length_incline[g] str_internal_temperature[°C]\n")

    def add_second_circle(self):
        for aim in reversed(copy.deepcopy(self.aims)):
            new_aim = copy.deepcopy(aim)
            new_aim.hz += 200
            new_aim.v = 400 - new_aim.v
            self.aims.append(new_aim)

    def go_home(self):
        log.info("Going to home position")
        self.geocom.AUT_MakePositioning(0, 200, AUT_POSMODE["AUT_PRECISE"], AUT_ATRMODE["AUT_POSITION"])

    def initialize(self, retry_amount=3):
        current_try = 0
        while current_try <= retry_amount:
            current_try += 1

            if current_try == 2:
                log.info("Initializing failed, trying again in 10 seconds")
                time.sleep(10)
            elif current_try == 3:
                log.info("Initializing failed, trying again in 90 seconds")
                time.sleep(90)
            elif current_try > 3:
                log.info("Initializing failed, trying again in 10 min")
                time.sleep(10*60)

            if not self.geocom.TMC_SetInclineSwitch(ON_OFF_TYPE["ON"]):  # if off, no values for length and cross inclination
                continue

            if not self.geocom.TMC_SetAtmPpm(0):
                continue

            if not self.geocom.TMC_SetEdmMode(EDM_MODE["EDM_PRECISE_IR"]):  # for MS30   EDM_PRECISE_IR
                continue

            if not self.geocom.BAP_SetMeasPrg(BAP_USER_MEASPRG["BAP_SINGLE_REF_PRECISE"]):
                continue

            log.info("Successfully (re)initialized TS")
            break
        else:
            log.info("Initializing failed, stopping program")
            self.upload_measurement_files_and_log()
            exit()
            return False
        return True

    def upload_measurement_files_and_log(self):
        try:
            srv = pysftp.Connection(host="matlab.tugraz.at", username="atraxoo", password=None)  # enter password if no ssh key in authorized keys
            with srv.cd('/home/a/atraxoo/Desktop/Sensorik/measurements'):
                srv.put(self.current_measurement_file_name)
            with srv.cd('/home/a/atraxoo/Desktop/Sensorik/logs'):
                srv.put(log.get_current_file_name())
            srv.close()
            log.info("Uploaded file via SFTP")
        except:
            log.error("Failed updating file via SFTP")

    def run(self, interval=None, set_amount=None, distance_measurement_retry_amount=2):
        """
        :param interval: in seconds or None for continuous measuring
        :param set_amount: None for infinite amount of sets
        :param distance_measurement_retry_amount:
        """
        while set_amount is None or set_amount > 0:
            self.last_start_time = time.time()

            self.current_measurement_file_name = MEASUREMENT_FOLDER + dt.datetime.now().strftime("%Y%m%d") + ".txt"
            log.set_new_file_name()

            log.info("Starting new set")

            for aim in self.aims:
                log.info("Measuring " + aim.name)

                if not self.geocom.AUS_SetUserAtrState(ON_OFF_TYPE["ON"]):  # important that this is here and first to execute
                    self.initialize()  # stops program if not initializing again
                    continue

                if not self.geocom.BAP_SetTargetType(aim.target):
                    self.initialize()  # stops program if not initializing again
                    continue

                if aim.target == BAP_TARGET_TYPE["BAP_REFL_USE"]:
                    if not self.geocom.BAP_SetPrismType(aim.prism):
                        self.initialize()  # stops program if not initializing again
                        continue

                if aim.target == BAP_TARGET_TYPE["BAP_REFL_USE"]:
                    if not self.geocom.AUT_MakePositioning(aim.hz, aim.v, AUT_POSMODE["AUT_PRECISE"],
                                                    AUT_ATRMODE["AUT_TARGET"]):
                        self.initialize()  # stops program if not initializing again
                        continue
                else:
                    if not self.geocom.AUT_MakePositioning(aim.hz, aim.v, AUT_POSMODE["AUT_PRECISE"],
                                                    AUT_ATRMODE["AUT_POSITION"]):
                        self.initialize()  # stops program if not initializing again
                        continue

                if aim.target == BAP_TARGET_TYPE["BAP_REFL_USE"]:
                    if not self.geocom.AUT_FineAdjust(2, 2):
                        self.initialize()  # stops program if not initializing again
                        continue

                distance_measurement_retry_i = 0

                full_measure_rsp = False
                while distance_measurement_retry_i < distance_measurement_retry_amount:
                    if not self.geocom.TMC_DoMeasure(TMC_MEASURE_PRG["TMC_DEF_DIST"], TMC_INCLINE_PRG["TMC_AUTO_INC"]):
                        self.initialize()  # stops program if not initializing again
                        continue

                    time.sleep(COMPENSATOR_CHILL_TIME)  # let compensator chill a bit

                    timeout = 15000  # ms
                    # RC, Hz[double], V[double], AccAngle[double], C[double], L[double], AccIncl[double], SlopeDist[double], DistTime[double]
                    full_measure_rsp = self.geocom.TMC_GetFullMeas(timeout, TMC_INCLINE_PRG["TMC_AUTO_INC"])

                    if not full_measure_rsp:
                        break  # failed communication breaking out

                    distance_rsp_code = int(full_measure_rsp[0])

                    if distance_rsp_code == 0:
                        break  # successful distance measurement
                    log.error("Distance measurement Failed")
                    distance_measurement_retry_i += 1
                    if distance_measurement_retry_i < distance_measurement_retry_amount:
                        log.info("Retrying")

                if not full_measure_rsp:
                    self.initialize()  # stops program if not initializing again
                    continue

                rc_full_measure, hz_angle, v_angle, cross_incline, length_incline, slope_dist = int(
                    full_measure_rsp[0]), float(full_measure_rsp[1]), float(full_measure_rsp[2]), float(
                    full_measure_rsp[4]), float(full_measure_rsp[5]), float(full_measure_rsp[7])

                # %R1P,0,0:RC,Hz[double],V[double],AngleAccuracy[double],AngleTime[long],CrossIncline[double],LengthIncline[double], AccuracyIncline[double],InclineTime[long],FaceDef[long]
                angle1_rsp = self.geocom.TMC_GetAngle1(TMC_INCLINE_PRG["TMC_AUTO_INC"])

                if not angle1_rsp:
                    self.initialize()  # stops program if not initializing again
                    continue

                rc_getAngle1, hz_angle_raw, v_angle_raw = int(angle1_rsp[0]), float(angle1_rsp[1]), float(
                            angle1_rsp[2])

                temperature_rsp = self.geocom.CSV_GetIntTemp()

                if not temperature_rsp:
                    self.initialize()  # stops program if not initializing again
                    continue

                rc_temperature, internal_temperature = int(temperature_rsp[0]), float(temperature_rsp[1])

                rt = 5  # round to
                str_datetime = str(dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
                str_aim_name = aim.name
                str_hz_angle = str(round(hz_angle/GON2RAD, rt))
                str_hz_angle_raw = str(round(hz_angle_raw/GON2RAD, rt))
                str_v_angle = str(round(v_angle/GON2RAD, rt))
                str_v_angle_raw = str(round(v_angle_raw/GON2RAD, rt))
                str_slope_dist = str(round(slope_dist, rt))
                str_cross_incline = str(round(cross_incline/GON2RAD, rt))
                str_length_incline = str(round(length_incline/GON2RAD, rt))
                str_internal_temperature = str(round(internal_temperature, rt))

                if rc_full_measure != 0:
                    str_slope_dist = "NaN"
                    log.error("Distance measurement failed (" + str(rc_full_measure) + ")")
                if rc_getAngle1 != 0:
                    str_hz_angle, str_hz_angle_raw, str_v_angle, str_v_angle_raw = "Nan", "Nan", "Nan", "Nan"
                    log.error("Angle response failed (" + str(rc_getAngle1) + ")")
                if rc_temperature != 0:
                    str_internal_temperature = "Nan"
                    log.error("Internal temperature measurement failed ( " + str(rc_temperature) + ")")

                with open(self.current_measurement_file_name, 'a+') as f:
                    f.write(str_datetime + ' ' + str_aim_name  + ' ' + str_hz_angle + ' ' + str_hz_angle_raw + ' '
                            + str_v_angle + ' ' + str_v_angle_raw + ' ' + str_slope_dist + ' '
                            + str_cross_incline + ' ' + str_length_incline + ' ' + str_internal_temperature + "\n")

                time.sleep(1)

            self.upload_measurement_files_and_log()

            if interval is not None:
                # get in home position
                self.go_home()

                try:
                    log.info("Sleeping for " + str(int(interval - (time.time() - self.last_start_time))) + "s")
                    time.sleep(interval - (time.time() - self.last_start_time))
                except ValueError:
                    log.warning("Interval too short")
            if set_amount is not None:
                set_amount -= 1
        else:
            log.info("Finished all sets")
