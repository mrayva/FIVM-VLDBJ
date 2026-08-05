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
option(FIVM_ENABLE_ZERIALIZE "Fetch and enable zerialize adaptors/tests" ON)

# -----------------------------------------------------------------------------
# Dependencies via vcpkg
# -----------------------------------------------------------------------------
find_package(flatbuffers CONFIG REQUIRED)
find_package(msgpack-cxx CONFIG QUIET)  # Optional, for msgpack-c

# -----------------------------------------------------------------------------
# Fetch zerialize (header-only)
# -----------------------------------------------------------------------------
if(FIVM_ENABLE_ZERIALIZE)
    include(FetchContent)
    # Pinned to a commit (not a floating branch) for reproducible builds.
    # zerialize has no tagged releases, so a commit SHA is the closest thing
    # to a version; bump this deliberately, don't track a branch HEAD.
    FetchContent_Declare(
        zerialize
        GIT_REPOSITORY https://github.com/mrayva/zerialize.git
        GIT_TAG        32d9d9447c9ce725ba0ea9d1a5d25005066a0cd8
        GIT_SHALLOW    FALSE
    )
    FetchContent_MakeAvailable(zerialize)
endif()

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
        flatbuffers::flatbuffers
)

if(FIVM_ENABLE_ZERIALIZE)
    target_link_libraries(fivm_runtime
        INTERFACE
            $<BUILD_INTERFACE:zerialize>
    )
endif()

target_compile_features(fivm_runtime INTERFACE cxx_std_20)

# Disable FlexBuffers locale-dependent code
target_compile_definitions(fivm_runtime INTERFACE FLATBUFFERS_LOCALE_INDEPENDENT=0)

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
if(FIVM_BUILD_TESTS)
    enable_testing()
    find_package(GTest CONFIG REQUIRED)
    find_library(CXXABI_LIBRARY c++abi)

    add_executable(csv_reader_test
        test/csv_reader_test.cpp
    )
    target_link_libraries(csv_reader_test
        PRIVATE
            fivm::runtime
            GTest::gtest
            GTest::gtest_main
    )
    if(CXXABI_LIBRARY)
        target_link_libraries(csv_reader_test PRIVATE ${CXXABI_LIBRARY})
    endif()
    set_target_properties(csv_reader_test PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests
    )
    add_test(NAME csv_reader_test COMMAND csv_reader_test)

    find_package(Threads REQUIRED)
    add_executable(string_test
        test/string_test.cpp
    )
    target_link_libraries(string_test
        PRIVATE
            fivm::runtime
            GTest::gtest
            GTest::gtest_main
            Threads::Threads
    )
    if(CXXABI_LIBRARY)
        target_link_libraries(string_test PRIVATE ${CXXABI_LIBRARY})
    endif()
    set_target_properties(string_test PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests
    )
    add_test(NAME string_test COMMAND string_test)

    if(FIVM_ENABLE_ZERIALIZE)
    add_executable(zerialize_test
        test/zerialize_test.cpp
    )
    target_link_libraries(zerialize_test
        PRIVATE
            fivm::runtime
            zerialize
            GTest::gtest
            GTest::gtest_main
    )
    if(CXXABI_LIBRARY)
        target_link_libraries(zerialize_test PRIVATE ${CXXABI_LIBRARY})
    endif()
    set_target_properties(zerialize_test PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/tests
    )
    add_test(NAME zerialize_test COMMAND zerialize_test)
    endif()
endif()

# -----------------------------------------------------------------------------
# Installation (simplified - no export of zerialize dependency)
# -----------------------------------------------------------------------------
include(GNUInstallDirs)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)
