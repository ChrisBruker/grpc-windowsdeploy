#include <grpcpp/grpcpp.h>
#include <iostream>

int main()
{
    std::cout << "gRPC libraries located via full_deploy bundle" << std::endl;
    std::cout << "gRPC version: " << grpc::Version() << std::endl;
    return 0;
}
