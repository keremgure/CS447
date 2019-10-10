import socket
import httpThread
# import importlib # For reloading httpThread
import threading
import logger
import argparse
import textwrap
import sys


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(BACKLOG)
        s.settimeout(5.0)

        global threads
        threads = []

        global pill2kill
        pill2kill = threading.Event()

        global LoggerObj
        LoggerObj = logger.Logger(loggerPeriod, pill2kill)
        threads.append(LoggerObj)
        LoggerObj.start()
        get_exit = threading.Thread(target=getExit, name='stdinReader')
        # threads.append(get_exit)
        get_exit.start()

        while not pill2kill.wait(0):
            try:
                # print("Active Threads: {}".format(threading.active_count()))
                conn, addr = s.accept()
                # importlib.reload(httpThread)  # TODO For Debugging purposes delete later.
                thread = httpThread.httpThread(conn, addr, PATH, LoggerObj, pill2kill)
                threads.append(thread)
                thread.start()
                # print("Active Threads: {}".format(threading.active_count()))

            except socket.timeout:
                pass
        return


def argsDefiner():
    global parser
    parser = argparse.ArgumentParser(prog='CS447 Simple HTTP Server',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''\
         additional information:
             Please specify the full path as STRING!
             (use "__")
             for the arguments or put the files
             in the same directory with the script.

         example:
             main.py "C:\\some_path\\another_path" 8080 --period 5"
         '''))

    # requiredNamed = parser.add_argument_group('required named arguments')
    parser.add_argument('path', help='Specify the path will be served to the server.')
    parser.add_argument('port', type=int,
                        help='Specify the port will be used for serving the server.')

    parser.add_argument('--period', type=int, required=False,
                        help='''Specify the period in seconds for the logger to print out the events.(default=5secs)''')


def argsParser():
    if len(sys.argv) < 2:
        parser.print_help(sys.stderr)
        sys.exit(1)

    global PORT
    global PATH
    global loggerPeriod
    args = parser.parse_args()
    loggerPeriod = LOGGER_DEFAULT if args.period is None else int(args.period)
    PATH = str(args.path)
    PORT = int(args.port)


def getExit():
    while True:
        for line in sys.stdin:
            if str(line).lower() == "exit\n":
                print("Exiting...")
                pill2kill.set()
                for thread in threads:
                    # print(thread.getName)
                    if thread.is_alive():
                        # print("Stopping....{},{}".format(thread.getName(), thread.ident))
                        thread.join()
                print("httpThreads are stopped...")
                return
            # print("Received: {} ".format(line))


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 0
    BACKLOG = 10
    LOGGER_DEFAULT = 5

    argsDefiner()
    argsParser()

    main()
