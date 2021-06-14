import os
import datetime as dt


LOG_FOLDER = "logs/"


class Logger:
    def __init__(self):
        if not os.path.isdir(LOG_FOLDER):
            os.mkdir(LOG_FOLDER)
        self.current_file_name = LOG_FOLDER + dt.datetime.now().strftime("%Y%m%d") + ".txt"

    def get_current_file_name(self):
        return self.current_file_name

    def set_new_file_name(self):
        self.current_file_name = LOG_FOLDER + dt.datetime.now().strftime("%Y%m%d") + ".txt"

    def info(self, string):
        string = str(dt.datetime.now().strftime('%Y%m%d_%H%M%S')) + " INFO: " + str(string) + "\n"
        print(string, end='')
        with open(self.current_file_name, 'a+') as f:
            f.write(string)

    def warning(self, string):
        string = str(dt.datetime.now().strftime('%Y%m%d_%H%M%S')) + " WARNING: " + str(string) + "\n"
        print(string, end='')
        with open(self.current_file_name, 'a+') as f:
            f.write(string)

    def error(self, string):
        string = str(dt.datetime.now().strftime('%Y%m%d_%H%M%S')) + " ERROR: " + str(string) + "\n"
        print(string, end='')
        with open(self.current_file_name, 'a+') as f:
            f.write(string)


log = Logger()
