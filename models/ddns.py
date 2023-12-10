import subprocess
import _thread
from queue import Queue
import time
import logging

class DDNS:

    def __launch(self): 
        pr = subprocess.Popen( # pylint: disable=all
            ['nsupdate', '-k', self.key_file],
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        if self.name_server:
            pr.stdin.write(f"server {self.name_server}\n".encode())
        #if self.zone:
        #    pr.stdin.write(f"zone {self.zone}\n".encode())

        return pr

    def __write(self):
        diff = 0
        while True:
            try:
                while self.queue.qsize():
                    cmd = self.queue.get()
                    if self.nsupdate.poll() is not None:
                        self.nsupdate = self.__launch()
                        logging.warning("Subprocess nsupdate is dead, relaunched.")

                    self.nsupdate.stdin.write((cmd + "\n").encode())
                    diff = 1
                    logging.debug("executing command: %s", cmd)

                if diff and self.nsupdate.poll() is None:
                    diff = 0
                    self.nsupdate.stdin.write(b"send\n")

            except Exception as e:
                logging.warning("Error in __write: %s", str(e))

            time.sleep(5)

    def __init__(self, logger, key_file, name_server, zone):
        self.logger  = logger
        self.key_file = key_file
        self.name_server = name_server
        self.zone    = zone

        self.nsupdate = self.__launch()
        self.queue = Queue()

        _thread.start_new_thread(self.__write, tuple())

    def add_record(self, domain, rectype, value, ttl = 5):
        if domain != "" and rectype != "" and value != "":
            if rectype == "TXT":
                value = value.replace('"', '\"')
                value = f'"{value}"'
            if rectype == "MX":
                value = f"10 {value}"
            self.queue.put(f"update add {domain} {ttl} {rectype} {value}")

    def del_record(self, domain, rectype, value):
        if domain != "":
            if rectype == "TXT":
                value = value.replace('"', '\"')
                value = f'"{value}"'
            if rectype == "MX":
                value = f"10 {value}"
            self.queue.put(f"update delete {domain} {rectype} {value}")
            print(f"update delete {domain} {rectype} {value}")
