cmake_minimum_required(VERSION 3.20)
project(grpc_consumer LANGUAGES CXX)

# Require C++17 and avoid compiler-specific extensions.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Expect the caller to define where the full_deploy bundle lives
set(FULL_DEPLOY_ROOT "" CACHE PATH "Absolute path to the Conan full_deploy output (top-level folder containing cmake/, lib/, bin/, include/)")
if(NOT FULL_DEPLOY_ROOT)
    message(FATAL_ERROR "Please configure FULL_DEPLOY_ROOT to the directory created by conan_full_deploy_all.bat")
endif()

# Tell CMake where to find the generated package configuration files
list(APPEND CMAKE_PREFIX_PATH "${FULL_DEPLOY_ROOT}/cmake")

find_package(gRPC CONFIG REQUIRED)
find_package(protobuf CONFIG REQUIRED)

add_executable(grpc_hello
    src/main.cpp
)

target_link_libraries(grpc_hello
    PRIVATE
    gRPC::grpc++
    protobuf::protobuf
)

target_include_directories(grpc_hello
    PRIVATE
        "${FULL_DEPLOY_ROOT}/include"
)

# Provide a hint about where to copy dependent DLLs from when configuring/installing
set_target_properties(grpc_hello PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/bin/debug"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_BINARY_DIR}/bin/relwithdebinfo"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/bin/release"
)
