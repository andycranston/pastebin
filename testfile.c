#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BLOCK 819200

char *progname;

main(argc, argv)
  int   argc;
  char *argv[];
{
  int   size;
  int   i;

  progname = argv[0];

  if (argc < 2) {
    fprintf(stderr, "%s: must specify size of test file to generate\n", progname);
    exit(2);
  }
  
  size = atoi(argv[1]);

  if (size < 80) {
    fprintf(stderr, "%s: specified size is too small\n", progname);
    exit(2);
  }

  for ( i = 0 ; i < size ; i++ ) {
    putchar(0);
  }

  exit(0);
}
