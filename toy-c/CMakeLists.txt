project(toy_c)

add_executable(toy_c main.cpp)

add_subdirectory(my_component)

target_link_libraries(toy_c my_component)

