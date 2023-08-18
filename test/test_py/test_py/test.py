import time
import threading
import std_msgs.msg
import queue
import signal
import rclpy
from rclpy.node import Node
from .benchmark import *

class node1(Node):
    def __init__(self):
        super().__init__("trytry")
        self.pub = self.create_publisher(std_msgs.msg.String, "testpub", 10)
        # self.timer = self.create_timer(1, self._print)
        self.count = 0
        self.buf = queue.Queue(10)
        self.lock = threading.Condition()
        self.temp = None

    def _put(self):
        timer = InstrumentationTimer()
        while self.count<=5 and rclpy.ok():
            t1 = time.time()
            time.sleep(1)
            self.lock.acquire()
            if self.buf.full():
                return
            self.buf.put_nowait(self.count)
            self.count += 1
            print("[ ",threading.get_ident()," ] after putting ", self.buf.qsize())
            self.lock.notify()
            self.lock.release()
            print("t1 running time, ", time.time()-t1)
        timer.stop()

    def _print(self):
        timer = InstrumentationTimer()
        while self.count<=5 and rclpy.ok():
            r = std_msgs.msg.String()
            t2 = time.time()
            # if(not self.buf.empty()):
            self.lock.acquire()
            self.lock.wait()
            x = self.buf.get_nowait()
            print("[ ",threading.get_ident()," ]", x)
            self.lock.release()
            r.data = "now count is " + str(x)
            self.pub.publish(r)
            print("t2 running time, ", time.time()-t2)
        timer.stop()

def ctrlc_handler(signum, frame):
    global shut_down
    shut_down = 1
    time.sleep(0.25)
    print("Exiting")
    exit(1)   

def main():
    global shut_down
    shut_down = 0
    signal.signal(signal.SIGINT, ctrlc_handler)

    vis = Instrumentor()
    vis.BeginSession()
    timer = InstrumentationTimer()
    rclpy.init()
    publisher = node1()
    t1 = threading.Thread(target=publisher._put)
    t1.start()
    publisher._print()
    # rclpy.spin(publisher)
    t1.join()
    # print(publisher.temp.Start, publisher.temp.End, publisher.temp.ThreadID)
    # print(result2.Start, result2.End, result2.ThreadID)
    rclpy.shutdown()
    timer.stop()
    vis.EndSession()
    
if __name__ == "__main__":
    main()