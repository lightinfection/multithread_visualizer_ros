#include "test_cpp/test.hpp"
#include "test_cpp/Instrumentor.h"

testnode::testnode (/* args */)
: rclcpp::Node("trycpp")
{   
    std::thread()


    
}

void testnode::put(int count)
{
    std::unique_lock<std::mutex> lock(mutex);
    for (int i = 0; i < count; i++)
    {
        input = std::to_string(count);
        buffer.push(input);
        cv.notify_one();
    }
}

void testnode::print()
{
    output.data = buffer.front();
    buffer.pop();
    talker->publish(output);
}

testnode::~testnode ()
{
}


int main()
{
    return 0;
}
