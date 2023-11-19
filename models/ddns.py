import subprocess
import _thread
from queue import Queue
import time
import logging

verbose = 1

class DDNS:

    def __launch(self):
        pr = subprocess.Popen(
            ['nsupdate', '-k', self.keyFile],
            bufsize = 0,
            stdin   = subprocess.PIPE,
            stdout  = subprocess.PIPE)
        
        if self.nServer: 
            pr.stdin.write(f"server {self.nServer}\n".encode())

        if self.zone: 
            pr.stdin.write(f"zone {self.zone}\n".encode())
    
        return pr
    
    def __write(self):
        diff = 0
        while True:
            try:
                while self.queue.qsize():
                    cmd = self.queue.get()
                    self.nsupdate.stdin.write((cmd + "\n").encode())
                    diff = 1
                    logging.debug("executing command: {cmd}".format(cmd=cmd));

                    if self.nsupdate.poll():
                        self.queue.put(cmd)
                        self.nsupdate = self.__launch()
                        logging.warning("Subprocess nsupdate is dead.")
                
                if diff and self.nsupdate.poll() == None:
                    diff = 0
                    self.nsupdate.stdin.write(b"send\n")
            
            except Exception as e:
                logging.warning(e)
                raise Exception(e)

            time.sleep(5)

    def __init__(self, logger, keyFile, nServer, zone):
        self.logger  = logger
        self.keyFile = keyFile
        self.nServer = nServer
        self.zone    = zone

        self.nsupdate = self.__launch()
        self.queue = Queue()

        _thread.start_new_thread(self.__write, tuple())

    def addRecord(self, domain, rectype, value, ttl = 5):
        if domain != "" and rectype != "" and value != "":
            if rectype == "TXT":
                value = '"%s"' % value.replace('"', '\"')
            self.queue.put("update add %s %d %s %s" % (domain, ttl, rectype, value))

    def delRecord(self, domain, rectype, value):
        if domain != "":
            if rectype == "TXT":
                value = '"%s"' % value.replace('"', '\"')
            self.queue.put("update delete %s %s %s" % (domain, rectype, value))

