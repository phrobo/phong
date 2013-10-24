/*
 * A simple setuid binary that runs /usr/bin/phong.py
 *
 * Copyright (C) 2013 Torrie Fischer <tdfischer@hackerbots.net>
 *
 * This file is part of phong.
 *
 * Phong is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Phong is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with phong.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <sys/types.h>
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
  newArgv[argc+1] = NULL;
  setreuid (geteuid (), getuid ());
  return execv (newArgv[0], newArgv);
}
