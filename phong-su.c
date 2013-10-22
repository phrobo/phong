/*
 * A simple setuid binary that runs /usr/bin/phong.py
 */
#include <unistd.h>

#ifndef PHONG_PATH
#define PHONG_PATH "/usr/bin/phong.py"
#endif

int main(int argc, char** argv)
{
  int i;
  char **newArgv;

  newArgv = calloc (sizeof (char*), argc+1);
  newArgv[0] = strdup (PHONG_PATH);
  newArgv[1] = strdup ("sudo");
  for (i = 1; i < argc; i++) {
    newArgv[i+1] = strdup(argv[i]);
  }
  return execv (PHONG_PATH, newArgv);
}
