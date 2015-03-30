cmake_minimum_required(VERSION 2.8.4)
project(testC)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -lwiringPi")

set(SOURCE_FILES
    testc/extSPI.cpp
    testc/extSPI.h
    testc/main.cpp
    testc/main.h
    testc/PI_GPIO.c)

add_executable(testC ${SOURCE_FILES})