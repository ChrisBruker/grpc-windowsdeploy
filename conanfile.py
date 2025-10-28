from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy
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
        # Generate CMake dependencies
        deps = CMakeDeps(self)
    # Automatically map RelWithDebInfo to Release in generated CMake files
        deps.build_context_activated = ["Release", "RelWithDebInfo", "Debug"]
        deps.build_context_suffix = {"RelWithDebInfo": "Release"}
        deps.generate()

        # Generate CMake toolchain
        tc = CMakeToolchain(self)

        # Configure build types and MSVC-specific settings
        if is_msvc(self):
            # Set ZI flag for MSVC compiler for Debug only
            if self.settings.build_type == "Debug":
                tc.variables["CMAKE_CXX_FLAGS_DEBUG"] = "/MDd /ZI /Ob0 /Od /RTC1"
                tc.variables["CMAKE_C_FLAGS_DEBUG"] = "/MDd /ZI /Ob0 /Od /RTC1"
            # Remove debug info flags from Release and RelWithDebInfo
            if self.settings.build_type == "RelWithDebInfo":
                tc.variables["CMAKE_CXX_FLAGS_RELWITHDEBINFO"] = "/MD /O2 /Ob1 /DNDEBUG"
                tc.variables["CMAKE_C_FLAGS_RELWITHDEBINFO"] = "/MD /O2 /Ob1 /DNDEBUG"
            if self.settings.build_type == "Release":
                tc.variables["CMAKE_CXX_FLAGS_RELEASE"] = "/MD /O2 /GL /DNDEBUG"
                tc.variables["CMAKE_C_FLAGS_RELEASE"] = "/MD /O2 /GL /DNDEBUG"
                tc.variables["CMAKE_EXE_LINKER_FLAGS_RELEASE"] = "/OPT:REF /OPT:ICF"
                tc.variables["CMAKE_MODULE_LINKER_FLAGS_RELEASE"] = "/OPT:REF /OPT:ICF"
                tc.variables["CMAKE_SHARED_LINKER_FLAGS_RELEASE"] = "/OPT:REF /OPT:ICF"

        # Set output directories for Release and RelWithDebInfo to the same folder
        tc.variables["CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE"] = "${CMAKE_BINARY_DIR}/release"
        tc.variables["CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO"] = "${CMAKE_BINARY_DIR}/release"
        tc.variables["CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE"] = "${CMAKE_BINARY_DIR}/release"
        tc.variables["CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO"] = "${CMAKE_BINARY_DIR}/release"
        tc.variables["CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE"] = "${CMAKE_BINARY_DIR}/release"
        tc.variables["CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO"] = "${CMAKE_BINARY_DIR}/release"

        # Additional CMake configurations
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = "ON"
        tc.variables["CMAKE_EXPORT_COMPILE_COMMANDS"] = "ON"

        # gRPC specific configurations
        tc.variables["CMAKE_CXX_STANDARD"] = "17"
        tc.variables["CMAKE_CXX_STANDARD_REQUIRED"] = "ON"

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
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "m", "dl"])
        
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
