import threading
import queue
import datetime


class Logger(threading.Thread):
    def __init__(self, period, pill2kill):
        self.logQueue = queue.Queue()
        self.period = period
        self.stop_event = pill2kill
        threading.Thread.__init__(self)
        self.name = "Logger"
        self.logFile = open("log", "a+")

    def run(self):
        # print("in run funcs")
        while not self.logQueue.empty():
            logItem = self.logQueue.get()
            self.logFile.write("{}\n".format(logItem))
            print(logItem)
        if not self.stop_event.wait(0):
            logRun = threading.Timer(self.period, self.run)
            logRun.name = "logPrint"
            logRun.start()
        else:
            self.logFile.close()
            print("Logger is stopped...")

    def log(self, event, client_ip, client_port):
        logItem = Log(event, client_ip, client_port).run()
        self.logQueue.put(logItem)


class Log:
    def __init__(self, event, client_ip, client_port):
        self.event = event
        self.date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.client_ip = client_ip
        self.client_port = client_port
        # print("log initialized")

    def run(self):
        # print("running!")
        return "{} GET {} {}:{}".format(self.date, self.event, self.client_ip, self.client_port)
