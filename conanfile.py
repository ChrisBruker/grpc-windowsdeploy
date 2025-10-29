from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, save
from conan.tools.microsoft import is_msvc
import os


class GrpcProjectConan(ConanFile):
    name = "grpc-project"
    version = "1.0"
    
    # Package metadata
    description = "gRPC project with comprehensive build configuration"
    topics = ("grpc", "rpc", "networking")
    
    # Configuration options
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "grpc/*:cpp_plugin": True,
        "grpc/*:codegen": True,
        "grpc/*:python_plugin": True,
        "grpc/*:csharp_plugin": False,
        "grpc/*:node_plugin": False,
        "grpc/*:objective_c_plugin": False,
        "grpc/*:php_plugin": False,
        "grpc/*:ruby_plugin": False,
    }
    
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "proto/*"
    
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
    
    def configure(self):
        # Ensure C++17 is used for consistency across all dependencies
        self.settings.compiler.cppstd = "17"
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def requirements(self):
        # gRPC and its dependencies
        self.requires("grpc/1.72.0")
        
       

    
    def build_requirements(self):
        # Build tools
        self.tool_requires("cmake/[>=3.15]")
        if is_msvc(self):
            # Ensure we have the right tools for MSVC builds
            pass
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        # Inject custom MSVC toolchain for all builds
        tc.user_toolchain = [os.path.join(self.source_folder, "msvc_conan_toolchain.cmake")]
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        # Copy license files
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        # Run CMake install
        cmake = CMake(self)
        cmake.install()
        
        # Copy additional files if needed
        copy(self, "*.proto", src=os.path.join(self.source_folder, "proto"), 
             dst=os.path.join(self.package_folder, "proto"), keep_path=True)
    
    def package_info(self):
        # Define package information for consumers
        self.cpp_info.libs = ["grpc_project"]  # Adjust based on your actual library names
        
        # Set include directories
        self.cpp_info.includedirs = ["include"]
        
        # Set library directories
        self.cpp_info.libdirs = ["lib"]
        
        # Set binary directories
        self.cpp_info.bindirs = ["bin"]
        
        # Platform-specific configurations
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "wsock32"])
        
        # Compiler-specific flags
        if is_msvc(self):
            # Ensure proper linkage and runtime
            if self.settings.build_type == "Debug":
                self.cpp_info.cppflags.append("/MDd")
            else:
                self.cpp_info.cppflags.append("/MD")
    
    def deploy(self):
        # Deploy binaries and dependencies to a deployment folder
        self.copy("*.exe", dst="bin", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.proto", dst="proto", keep_path=True)
        
        # Copy configuration files  
        self.copy("*.conf", dst="config", keep_path=False)
        self.copy("*.json", dst="config", keep_path=False)
        self.copy("*.yaml", dst="config", keep_path=False)
        self.copy("*.yml", dst="config", keep_path=False)

        # Copy CMake generator files into deploy folder for downstream CMake projects
        generators_src = getattr(self, "generators_folder", None)
        if generators_src and os.path.isdir(generators_src):
            cmake_dst = os.path.join(self.deploy_folder, "cmake") if hasattr(self, "deploy_folder") else "cmake"
            copy(self, "*", src=generators_src, dst=cmake_dst, keep_path=True)
