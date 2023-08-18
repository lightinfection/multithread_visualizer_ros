import time
import threading
import std_msgs.msg
import queue
import json
import signal
import inspect
import rclpy
from rclpy.node import Node


class ProfileResult:
    def __init__(self, name, start, end, thread_id):
        self.Name = name
        self.Start = start
        self.End = end
        self.ThreadID = thread_id

class InstrumentationTimer:
    def __init__(self):
        self.m_Name = inspect.stack()[1][0].f_code.co_name
        self.start = time.time()
    
    def stop(self):
        self.end = time.time()
        write_in = ProfileResult(name=self.m_Name, start=self.start, end=self.end, thread_id=threading.get_ident())
        Instrumentor.get().WriteProfile(write_in)
    
class Instrumentor:

    json_temp = []

    def BeginSession(self, filepath="result.json" ):
        self.file = open(filepath, "w")
        self.file.truncate(0)
        self.WriteHeader()

    def EndSession(self):
        self.WriteFooter()
        self.file.close()

    def WriteProfile(self, result: ProfileResult):
        Instrumentor.json_temp = [
            {
            "cat":"function", 
            "dur": result.End-result.Start, 
            "name":result.Name, 
            "ph":"X", "pid":0, 
            "tid": result.ThreadID, 
            "ts":result.Start
            },  *Instrumentor.json_temp
        ]
    
    def WriteHeader(self):
        m_OutputStream = "{\"otherData\": {},\"traceEvents\":"
        self.file.write(m_OutputStream)
        self.file.flush()

    def WriteFooter(self):
        m_OutputStream = json.dumps(Instrumentor.json_temp) + "}"
        self.file.write(m_OutputStream)
        self.file.flush()

    @staticmethod
    def get():
        instant = Instrumentor()
        return instant

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