cmake_minimum_required(VERSION 3.25)

project(fivm_runtime
    VERSION 1.1.0
    DESCRIPTION "FIVM Runtime - Factorized Incremental View Maintenance"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(FIVM_BUILD_TESTS "Build tests" ON)
option(FIVM_BUILD_EXAMPLES "Build examples" OFF)

# -----------------------------------------------------------------------------
# Dependencies via vcpkg
# -----------------------------------------------------------------------------
find_package(flatbuffers CONFIG REQUIRED)
find_package(msgpack-cxx CONFIG QUIET)  # Optional, for msgpack-c

# -----------------------------------------------------------------------------
# Fetch zerialize (header-only)
# -----------------------------------------------------------------------------
include(FetchContent)
FetchContent_Declare(
    zerialize
    GIT_REPOSITORY https://github.com/colinator/zerialize.git
    GIT_TAG        main
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(zerialize)

# -----------------------------------------------------------------------------
# FIVM Runtime Library (header-only)
# -----------------------------------------------------------------------------
add_library(fivm_runtime INTERFACE)
add_library(fivm::runtime ALIAS fivm_runtime)

target_include_directories(fivm_runtime
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Link to zerialize for build, but don't export it (zerialize doesn't export)
target_link_libraries(fivm_runtime
    INTERFACE
        $<BUILD_INTERFACE:zerialize>
        flatbuffers::flatbuffers
)

target_compile_features(fivm_runtime INTERFACE cxx_std_20)

# Disable FlexBuffers locale-dependent code
target_compile_definitions(fivm_runtime INTERFACE FLATBUFFERS_LOCALE_INDEPENDENT=0)

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
if(FIVM_BUILD_TESTS)
    enable_testing()
    find_package(GTest CONFIG REQUIRED)

    add_executable(zerialize_test
        test/zerialize_test.cpp
    )
    target_link_libraries(zerialize_test
        PRIVATE
            fivm::runtime
            zerialize
            GTest::gtest_main
    )
    set_target_properties(zerialize_test PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests
    )
    add_test(NAME zerialize_test COMMAND zerialize_test)
endif()

# -----------------------------------------------------------------------------
# Installation (simplified - no export of zerialize dependency)
# -----------------------------------------------------------------------------
include(GNUInstallDirs)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)
