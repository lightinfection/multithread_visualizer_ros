#include <memory>
#include <string>
#include <thread>
#include <queue>
#include <iostream>
#include <condition_variable>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "test_cpp/Instrumentor.h"

#define PROFILE 1
#if PROFILE
#define PROFILE_SCOPE(name)  InstrumentationTimer timer__LINE__(name)
#define PROFILE_FUNCTION() PROFILE_SCOPE(__FUNCTION__)
#else
#define PROFILE_SCOPE(name)
#endif

class testnode : public rclcpp::Node
{

private:
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr talker;
    std::queue<std::string> buffer;
    std::string temp;
    bool is_put = false;
    std::mutex mutex;
    std::condition_variable cv;

public:
    testnode(): Node("trytrytry")
    {
        PROFILE_FUNCTION(); // add timer for benchmark
        talker = this->create_publisher<std_msgs::msg::String>("test_thread_cpp", 10);   
        std::thread t1(std::bind(&testnode::put, this));
        std::thread t2(std::bind(&testnode::print, this));
        t1.join();
        t2.join();
    }
    
    void put()
    {
        if (!is_put)
        {
            for (int i = 0; i <= 10; i++)
            {   
                rclcpp::Clock().sleep_for(std::chrono::seconds(1)); // make sure print() thread blocked first
                PROFILE_FUNCTION(); // add timer for benchmark
                std::unique_lock<std::mutex> lock(mutex);
                temp = std::to_string(i);
                buffer.push(temp);
                cv.notify_one();
                lock.unlock();
                RCLCPP_INFO(this->get_logger(), "inputing '%s'",temp.c_str());
            }
        }
        is_put = true;
    }
    
    void print()
    {
        while (rclcpp::ok() && (!is_put))
        {
            PROFILE_FUNCTION(); // add timer for benchmark
            std_msgs::msg::String output;
            std::unique_lock<std::mutex> lock(mutex);
            while (!is_put)
            {
                if(!buffer.empty())
                {
                    std::string getdata = buffer.front();
                    output.data = getdata;
                    talker->publish(output);
                    buffer.pop();
                    RCLCPP_INFO(this->get_logger(), "outputing '%s'", getdata.c_str());
                    break;
                }
                cv.wait(lock);
            }
        }
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    Instrumentor::Get().BeginSession("testcpp");
    testnode node2;
    Instrumentor::Get().EndSession();
    rclcpp::shutdown();
    return 0;
}
