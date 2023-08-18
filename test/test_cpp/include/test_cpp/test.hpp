#pragma once
#ifndef TEST_CPP__TEST_HPP_
#define TEST_CPP__TEST_HPP_

#include <memory>
#include <string>
#include <thread>
#include <queue>
#include <iostream>
#include <condition_variable>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class testnode : public rclcpp::Node
{
private:
    std::queue<std::string> buffer;
    std::mutex mutex;
    std::condition_variable cv;
    
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr talker;
    std_msgs::msg::String output;
    std::string input;

public:
    testnode(/* args */);
    ~testnode();
    void put(int count);
    void print();
};

#endif
