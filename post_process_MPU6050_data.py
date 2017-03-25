from interruptingcow import timeout
import argparse
import cPickle as pickle
import datetime
import matplotlib.pyplot as plt
import numpy as np
import serial
import subprocess
import time

POLL_TIME = 5

class SerialReader(object):
    def __init__(self, baud_rate, port=None, dump_data=False, debug=False,
                 stabilizing_time=5):
        self.baud_rate = baud_rate
        self.raw_data = []

        if port:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=0.5)
        else:
            self.ser = None
            self.find_serial_device()

        self.dump_data = dump_data
        self.debug = debug

        if self.debug:
            self.stabilizing_time = 0.1

        # Relevant data arrays
        self.x_1 = []
        self.x_2 = []

        self.y_1 = []
        self.y_2 = []

        self.z_1 = []
        self.z_2 = []

    def find_serial_device(self):
        serial_devices = subprocess.Popen("ls /dev/serial/by-id", shell=True,
                        stdout=subprocess.PIPE).stdout.read().strip().split('\n')

        assert len(serial_devices) == 1
        serial_device = "/dev/serial/by-id/" + serial_devices[0]
        self.ser = serial.Serial(serial_device, self.baud_rate, timeout=0.5)

    def init_data_stream(self):
        max_attempts = 20
        while True:
            data = self.ser.readline()
            if 'Send any' in data:
                print "Sending start signal"
                self.ser.write('s')
                break
            if max_attempts < 0:
                print "Unable to do this. WTF is going on"
                import pdb ; pdb.set_trace()
                break
            max_attempts -= 1

    def wait_for_stable_signal(self):
        print "Waiting for signal to stabilizing.."
        print "Sleeping for %ds." %(self.stabilizing_time)
        time.sleep(self.stabilizing_time)
        print "Starting to collect data for %d seconds" %(POLL_TIME)
        time.sleep(0.1)

    @timeout(POLL_TIME)
    def collect_data(self):
        while True:
            try:
                data = self.ser.readline()
                self.raw_data.append(data)
            except KeyboardInterrupt:
                print "Keyboard Interrupt Pressed, exiting"
                break
            # means we are polling quicker than the buffer is being
            # written, so just pass. sleeping here is somewhat dangerous
            # so we are better off spinning.
            except serial.serialutil.SerialException:
                if self.debug:
                    import pdb ; pdb.set_trace()
                pass
            # watchdog raises an interrupt exception
            except RuntimeError:
                if self.debug:
                    print "Done polling.. Processing time now"
                break

        if self.dump_data:
            self.dump()

    def dump(self):
        pickle.dump(self.raw_data, open("raw_data.txt", "wb"))
        print "Done Dumping. Data has been saved as raw_data.txt in cwd."

    def process_data(self):
        if self.debug:
            print "Processing data set.."

        for line in self.raw_data:
            try:
                a1, a2 = line.strip().split('|')
            except Exception as e:
                continue

            # HACK: Better way to do this for sure, but too late rn.
            # Just go with it
            try:
                a1 = a1.strip().split()
                a2 = a2.strip().split()

                # ensure we don't have malformed data
                assert(len(a1) == 3)
                assert(len(a2) == 3)

                self.x_1.append(a1[0])
                self.y_1.append(a1[1])
                self.z_1.append(a1[2])

                self.x_2.append(a2[0])
                self.y_2.append(a2[1])
                self.z_2.append(a2[2])

            # Swallow the above exception of malformed data and continue
            # one data point of inconsistency in practice is fine
            # for future, we should prob have a strike basis counter that
            # limits the number of consecutive failures
            except Exception as e:
                pass

        print "Graphing results.."
        plt.subplot(311)
        plt.plot(self.x_1)
        plt.plot(self.x_2)

        plt.subplot(312)
        plt.plot(self.y_1)
        plt.plot(self.y_2)

        plt.subplot(313)
        plt.plot(self.z_1)
        plt.plot(self.z_2)

        plt.show()
        import pdb ; pdb.set_trace()

    def run(self):
        #self.init_data_stream()
        self.wait_for_stable_signal()
        self.collect_data()
        self.process_data()

def main():
    # TODO:
    #       1) Add argparse for poll time and debug and other options

    global POLL_TIME
    POLL_TIME = 0.5
    debug = True

    ser = SerialReader(115200, debug=debug)
    ser.run()


if __name__ == "__main__":
    main()
