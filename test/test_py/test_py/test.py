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
        timer = InstrumentationTimer()
        self.pub = self.create_publisher(std_msgs.msg.String, "testpub", 10)
        # self.timer = self.create_timer(1, self._print)
        self.count = 0
        self.buf = queue.Queue(10)
        self.lock = threading.Condition()
        self.temp = None
        t1 = threading.Thread(target=self._put)
        t2 = threading.Thread(target=self._print)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        timer.stop()

    def _put(self):
        while self.count<=20 and rclpy.ok():
            t1 = time.time()
            timer = InstrumentationTimer()
            self.lock.acquire()
            if self.buf.full():
                timer.stop()
                print("full already")
                return
            self.buf.put_nowait(self.count)
            self.count += 1
            print("[ ",threading.get_ident()," ] after putting ", self.buf.qsize())
            self.lock.notify()
            self.lock.release()
            timer.stop()
            print("t1 running time, ", time.time()-t1)
            time.sleep(1)

    def _print(self):
        while self.count<=20 and rclpy.ok():
            t2 = time.time()
            self.lock.acquire()
            timer = InstrumentationTimer()
            r = std_msgs.msg.String()
            while True:
                if(not self.buf.empty()):
                    x = self.buf.get_nowait()
                    print("[ ",threading.get_ident()," ]", x)
                    r.data = "now count is " + str(x)
                    self.pub.publish(r)
                    break
                self.lock.wait()
            self.lock.release()
            timer.stop()
            print("t2 running time, ", time.time()-t2)

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
    rclpy.init()
    publisher = node1()
    rclpy.shutdown()
    vis.EndSession()
    
if __name__ == "__main__":
    main()