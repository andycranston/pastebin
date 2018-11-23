/*
 *  @(!--#) @(#) timestable.c, version 004, 18-october-2017
 *
 *  test someones 12 times table times table
 *
 */

/*
 *  includes
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <setjmp.h>
#include <sys/time.h>

/*
 *  defines
 */

#define NUM_QUESTIONS     12

/*
 *  globals
 */

char *progname;

sigjmp_buf   jb;
struct sigaction siga;

/*****************************************************************/

static void answertimeout(sig)
  int   sig;
{
  progname = progname;

/*
  siglongjmp(jb, 1);
*/
}

/*****************************************************************/

void askquestions(numquestions)
  int   numquestions;
{
  int   q;
  int   x;
  int   y;
  int   a;
  int   answer;
  int   correct;
  int   rc;
  int   n;
  struct itimerval timer;

  correct = 0;

  for ( q = 1; q <= numquestions ; q++ ) {
    rc = sigsetjmp(jb, 1);

    if (rc != 0) {
      printf("You took too long to answer - moving on to next question\n\n");

      continue;
    }

    printf("Question %d of %d\n\n", q, numquestions);

    x = (random() % 12) + 1;
    y = (random() % 12) + 1;
    a = x * y;

    printf("What is %d times %d ?\n\n", x, y);

    timer.it_value.tv_sec = 5;
    timer.it_value.tv_usec = 500000;
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 0;

    setitimer(ITIMER_REAL, &timer, NULL);

    errno = 0;

    n = scanf("%d", &answer);

    putchar('\n');

    printf("%d %d\n", n, errno);

    if (answer == a) {
      printf("CORRECT - Well done!\n\n");
      correct++;
    } else {
      printf("Sorry - that answer is incorrect - the correct answer is %d\n\n", a);
    }
  }

  printf("End of test - you answered %d out of %d questions correctly\n\n", correct, numquestions);

  return;
}

/*****************************************************************/

main(argc, argv)
  int   argc;
  char *argv[];
{
  int   numquestions;

  progname = argv[0];

  numquestions = NUM_QUESTIONS;

  if (argc >= 2) {
    numquestions = atoi(argv[1]);

    if (numquestions < 1) {
      fprintf(stderr, "%s: number of questions on command line must be 1 or more - using default value of %d\n", progname, NUM_QUESTIONS);
      numquestions = NUM_QUESTIONS;
    }
  }

  siga.sa_handler = answertimeout;
  sigemptyset(&siga.sa_mask);
  siga.sa_flags = 0;
  sigaction(SIGALRM, &siga, NULL);

  askquestions(numquestions);

  return(0);
}

/*** end of file *************************************************/
