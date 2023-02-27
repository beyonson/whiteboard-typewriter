#include <iostream>
#include <GLFW/glfw3.h>

int main() {
    if (glfwInit()) {
        std::cout << "Error: could not initialize glfw" << std::endl;
        return -1;
    }

    return 0;
}