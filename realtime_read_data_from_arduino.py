"""
    Adopted from Mahesh Venkitchalam
    ldr.py : https://gist.githubusercontent.com/electronut/d5e5f68c610821e311b0/raw/bd14f52512880de6dd9171b109127b303af1d300/ldr.py

    Realtime library for graphing data from MPU6050
"""
from collections import deque
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
import serial
import time
from post_process_MPU6050_data import SerialReader

class RTSerialReader(SerialReader):
    MAXLEN = 1000

    def setup_data_arrays(self):
        self.x_1 = deque([0.0] * self.MAXLEN)
        self.x_2 = deque([0.0] * self.MAXLEN)

        self.y_1 = deque([0.0] * self.MAXLEN)
        self.y_2 = deque([0.0] * self.MAXLEN)

        self.z_1 = deque([0.0] * self.MAXLEN)
        self.z_2 = deque([0.0] * self.MAXLEN)

    def add_to_buffer(self, buf, val):
        if len(buf) < self.MAXLEN:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    def add(self, data_1, data_2):
        assert(len(data_1) == 3)
        assert(len(data_2) == 3)
        self.add_to_buffer(self.x_1, data_1[0])
        self.add_to_buffer(self.y_1, data_1[1])
        self.add_to_buffer(self.z_1, data_1[2])

        self.add_to_buffer(self.x_2, data_2[0])
        self.add_to_buffer(self.y_2, data_2[1])
        self.add_to_buffer(self.z_2, data_2[2])

    def update(self, frame_num,
               ax_0, ax_1,
               ay_0, ay_1,
               az_0, az_1):
        try:
            raw_data = self.ser.readline().strip()
            #print raw_data
            data_1, data_2 = raw_data.split('|')
            data_1 = [float(x) for x in data_1.strip().split()]
            data_2 = [float(x) for x in data_2.split()]


            if data_1[0] and data_2[0]:
                self.add(data_1, data_2)
                ax_0.set_data(range(self.MAXLEN), self.x_1)
                ax_1.set_data(range(self.MAXLEN), self.x_2)
                ay_0.set_data(range(self.MAXLEN), self.y_1)
                ay_1.set_data(range(self.MAXLEN), self.y_2)
                az_0.set_data(range(self.MAXLEN), self.z_1)
                az_1.set_data(range(self.MAXLEN), self.z_2)

            return [ax_0, ax_1, ay_0, ay_1, az_0, az_1]
        except KeyboardInterrupt:
            #print 'exiting'
            return a0
        except Exception as e:
            #print e
            return [ax_0, ax_1, ay_0, ay_1, az_0, az_1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--poll_time', '-p', type=int,
                        help='amount of time to poll',
                        default=5)
    parser.add_argument('--baud_rate', '-b',
                        help='baud rate',
                        default=115200)
    parser.add_argument('--debug', '-d',
                        help='debug mode or no',
                        action='store_true', default=False)
    parser.add_argument('--stabilizing_time', '-s',
                        help='amount of time for signal to stabilize',
                        default=10)
    args = parser.parse_args()

    # HACK:: Anshuman 03/22 Global variables are shitty, but decorators do not have
    # access to self/cls variables so.. for now global
    global POLL_TIME
    POLL_TIME = args.poll_time
    debug = args.debug
    baud_rate = args.baud_rate
    stabilizing_time = args.stabilizing_time

    rt_ser = RTSerialReader(args.baud_rate, debug=debug,
                       stabilizing_time=stabilizing_time)

    fig = plt.figure(num=0, figsize=(12,8))
    fig.suptitle("RealTime Acceleration on 3 axis", fontsize=12)

    ax0 = plt.subplot2grid((3,3), (0, 0), colspan=3, rowspan=1)
    ax1 = plt.subplot2grid((3,3), (1, 0), colspan=3, rowspan=1)
    ax2 = plt.subplot2grid((3,3), (2, 0), colspan=3, rowspan=1)

    # set titles
    ax0.set_title('Acceleration in X-axis', fontsize=9)
    ax1.set_title('Acceleration in Y-axis', fontsize=9)
    ax2.set_title('Acceleration in Z-axis', fontsize=9)

    # turn on grids
    ax0.grid(True)
    ax1.grid(True)
    ax2.grid(True)

    # set limits
    ax0.set_xlim(0, rt_ser.MAXLEN)
    ax0.set_ylim(-1000, 1000)
    ax1.set_xlim(0, rt_ser.MAXLEN)
    ax1.set_ylim(-1000, 1000)
    ax2.set_xlim(0, rt_ser.MAXLEN)
    ax2.set_ylim(-1000, 1000)

    # set labels
    ax0.set_xlabel("t")
    ax0.set_ylabel("ax")
    ax1.set_xlabel("t")
    ax1.set_ylabel("ay")
    ax2.set_xlabel("t")
    ax2.set_ylabel("az")

    # map axes to data vals
    ax_0, = ax0.plot([], [], 'b-', label='Input')
    ax_1, = ax0.plot([], [], 'g-', label='Output')

    ay_0, = ax1.plot([], [], 'b-', label='Input')
    ay_1, = ax1.plot([], [], 'g-', label='Output')

    az_0, = ax2.plot([], [], 'b-', label='Input')
    az_1, = ax2.plot([], [], 'g-', label='Output')

    # set legends
    ax0.legend([ax_0, ax_1], [ax_0.get_label(), ax_1.get_label()])
    ax1.legend([ay_0, ay_1], [ay_0.get_label(), ay_1.get_label()])
    ax2.legend([az_0, az_1], [az_0.get_label(), az_1.get_label()])

    anim = animation.FuncAnimation(fig, rt_ser.update,
                                   fargs=(ax_0, ax_1,
                                          ay_0, ay_1,
                                          az_0, az_1),
                                   interval = 50,
                                   blit=True)
    plt.show()

if __name__ == "__main__":
    main()

