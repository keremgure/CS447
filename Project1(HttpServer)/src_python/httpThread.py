import threading
import socket
import sys


class httpThread(threading.Thread):
    def __init__(self, channel, details, path, LoggerObj, pill2kill):
        self.stop_event = pill2kill
        self.channel = channel
        self.details = details
        self.path = path
        self.LoggerObj = LoggerObj

        self.channel.settimeout(5)  # set a timeout
        threading.Thread.__init__(self)
        self.setName("httpThread")

    def run(self):
        if not self.stop_event.wait(0):
            # print("Connection from {} with port {}".format(self.details[0],self.details[1]))
            try:
                req = self.channel.recv(1024)
                # print(req, type(self.channel))
                msg, obj = self.reqParser(req)
                # self.channel.sendall(msg.encode(encoding="utf-8"))
                self.channel.sendall(msg)
                self.channel.close()
                # print("connectionn closed with {}:{}".format(self.details[0],self.details[1]))
                self.LoggerObj.log(obj, self.details[0], self.details[1])
            except socket.timeout:
                print("Connection timed out.")
        else:
            print("httpThread is stopping...")

    def reqParser(self, req):
        types = [("html", "text/html"), ("jpg", "image/jpg"), ("png", "image/png"), ("js", "text/javascript"),
                 ("mp4", "video/mp4"), ("css", "text/css")]  # or use magic.Magic(MIME=True).from_file(file)

        # print("Parsing Request! from {}".format(self.details[0]))

        statusCode = "404 Not Found"
        objMIME = "text/html"
        # msg = b'HTTP/0.9 200 OK\r\n
        # Content-Type: text/html\r\ncharset=ISO-8859-4\r\n
        # Content-length: %d\r\n\r\n%b' % (len(objBuffer),objBuffer)

        # print(req, "\n", req.decode())

        temp = req.split(b'\r\n')
        obj = str(temp[0][4:-9])[2:-1]
        objExt = ""
        objBuffer = ""
        if (obj != ""):
            try:
                objExt = obj.split(".")[1]
            except IndexError:
                # print("{} so assuming directory.".format(ie))
                obj = "{}/index.html".format(obj)

            obj = "{}{}".format(self.path, obj)  # Set the full path
            # print(objExt)
            try:
                objBuffer = open(obj, 'rb').read()
                statusCode = "200 OK"
                for pair in types:
                    if objExt == pair[0]:
                        objMIME = pair[1]
                        break
                # print(objMIME)
            except(PermissionError, FileNotFoundError):
                # print("requested file not found: {}".format(obj))
                # objBuffer = open("{}/404.html".format(self.path),"rb").read()
                self.channel.close()  # Close the connection as signalling of errors are not wanted.
                sys.exit(1)

        objLength = len(objBuffer)
        # objLength = objLength.to_bytes((objLength.bit_length() // 8) + 1,'little')
        msg = "HTTP/0.9 {}\r\nContent-Type: {}\r\ncharset=utf-8\r\nConnection: close\r\nContent-length: {}\r\n\r\n".format(statusCode, objMIME, objLength).encode(encoding="UTF-8")
        msg = b'%s%b' % (msg, objBuffer)
        return msg, obj
