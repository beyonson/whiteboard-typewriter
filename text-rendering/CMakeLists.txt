cmake_minimum_required(VERSION 3.25)
project(text-rendering)

## Call sub directories
add_subdirectory(external)

include_directories(include)

## Create and link executables
set(SOURCES src/text-rendering.cpp src/glad.c include/shader.h include/glad/glad.h include/KHR/khrplatform.h)
add_executable(${PROJECT_NAME}
	${SOURCES}
)
target_link_libraries(${PROJECT_NAME}
	glfw
	freetype
)
