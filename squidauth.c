/*
 *  @(#--!) @(#) squidauth.c, version 003, 17-july-2017
 *
 *  provide squid authority program for simple password access
 *
 *  https://arashmilani.com/post?id=49
 *
 *  http://wiki.squid-cache.org/Features/Authentication
 *
 */

/*
 *  includes
 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

/*
 *  defines
 */

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define MAX_LINE_LENGTH 1024

#define PASSWORD "password"

/*****************************************************************************/

int alllower(s)
  char *s;
{
  int  flag;

  flag = TRUE;

  while (*s != '\0') {
    if (! islower(*s)) {
      flag = FALSE;
      break;
    }

    s++;
  }

  return(flag);
}

/*****************************************************************************/

main(argc, argv)
  int   argc;
  char *argv[];
{
  char  line[MAX_LINE_LENGTH + sizeof(char)];
  char *user;
  char *pass;
  int   ok;

  while ( fgets(line, MAX_LINE_LENGTH, stdin) != NULL )
  {
    ok = FALSE;

    if ( (user = strtok(line, " \t\r\n")) != NULL ) {
      if ( (pass = strtok(NULL, " \t\r\n")) != NULL ) {

#ifdef DEBUG
        printf("User=[%s] Pass=[%s]\n", user, pass);
#endif

        if (alllower(user)) {
          if (strcmp(pass, PASSWORD) == 0) {
            ok = TRUE;
          }
        }
      }
    }

    if (ok) {
      printf("OK\n");
    } else {
      printf("ERR\n");
    }

    fflush(stdout);
  }

  exit(0);
}
