#include <memory>
#include <string>
#include <thread>
#include <queue>
#include <iostream>
#include <condition_variable>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
// #include "test_cpp/Instrumentor.h"

class testnode : public rclcpp::Node
{

private:
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr talker;
    std::queue<std::string> buffer;
    std_msgs::msg::String output;
    std::string temp;
    bool is_put = false;
    std::mutex mutex;

public:
    testnode(): Node("trytrytry")
    {
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
                mutex.lock();
                temp = std::to_string(i);
                buffer.push(temp);
                RCLCPP_INFO(this->get_logger(), "inputing '%s'",temp.c_str());
                mutex.unlock();
                rclcpp::Clock().sleep_for(std::chrono::seconds(1));
            }
        }
        is_put = true;
    }
    
    void print()
    {
        while (rclcpp::ok() && (!is_put))
        {
            if(!buffer.empty())
            {
                mutex.lock();
                std::string getdata = buffer.front();
                output.data = getdata;
                RCLCPP_INFO(this->get_logger(), "outputing '%s'", getdata.c_str());
                talker->publish(output);
                buffer.pop();
                mutex.unlock();
            }
        }
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    testnode node2;
    rclcpp::shutdown();
    return 0;
}
