cmake_minimum_required(VERSION 2.8)
project( client )
find_package( OpenCV REQUIRED )
add_executable( client client.cpp )
target_link_libraries( client ${OpenCV_LIBS} )