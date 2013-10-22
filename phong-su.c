/*
 * A simple setuid binary that runs /usr/bin/phong.py
 */
#include <unistd.h>

#ifndef PHONG_PATH
#define PHONG_PATH "/usr/bin/phong.py"
#endif

int main(int argc, char** argv)
{
  return execv (PHONG_PATH, argv);
}
