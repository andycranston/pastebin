/*
 * @(!--#) @(#) snmptrapRECV.c, version 001, 17-may-2017
 *
 * simple SNMP trap receiver
 *
 * listen for SNMP trap messages and when receieved display on
 * stdout with each field broken down
 *
 */

/**************************************************************************/

/*
 *  system includes
 */
 
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

/**************************************************************************/

/*
 *  defines
 */

#ifndef TRUE
#define TRUE 1
#endif
 
#ifndef FALSE
#define FALSE 0
#endif

#define MAX_PACKET_LENGTH 8192

/**************************************************************************/

/*
 *  global variables
 */

char *progname;

int   debug;

/**************************************************************************/

char *basename(pathname)
  char   *pathname;
{
  char   *s;
  char   *lastslash;

  lastslash = pathname;

  s = pathname;

  while (*s != '\0') {
    if (*s == '/') {
      lastslash = s;
    }

    s++;
  }

  if (lastslash != pathname) {
    lastslash += 1;
  }

  return(lastslash);
}

/**************************************************************************/

void displaypacketbuffer(buf, lenbuf, displayasciiflag)
  unsigned char   *buf;
  int              lenbuf;
  int              displayasciiflag;
{
  int              i;
  char             c;

  for ( i = 0 ; i < lenbuf ; i++ ) {
    if ((i % 16) != 0) {
      putchar(' ');
    }

    printf("%02X", buf[i]);

    if (((i+1) % 16) == 0) {
      putchar('\n');
    }
  }

  printf("\n");

  if (displayasciiflag) {
    printf("%-3d:", lenbuf);

    for ( i = 0 ; i < lenbuf ; i++ ) {
      c = (char)buf[i];

      printf("  ");

      if ((c >= 32) && (c <=126)) {
        putchar(c);
      } else {
        putchar('_');
      }
    }

    printf("\n");
  }

  return;
}

/**************************************************************************/

void outputoid(intbytes, lenintbytes)
  unsigned char   *intbytes;
  int              lenintbytes;
{
  int              highnibble;
  int              lownibble;
  int              i;
  int              value;
  unsigned char    byte;

  if (lenintbytes == 0) {
    return;
  }

  highnibble = intbytes[0] / 40;
  lownibble  = intbytes[0] % 40;

  printf("%d.%d", highnibble, lownibble);

  value = 0;

  i = 1;

  while (i < lenintbytes) {
    value = value * 128;

    byte = intbytes[i];

    value += (byte & 0x7F);

    if (byte < 128) {
      printf(".%d", value);

      value = 0;
    }

    i++;
  }

  putchar('\n');

  return;
}

/**************************************************************************/

unsigned int getint(intbytes, lenintbytes)
  unsigned char   *intbytes;
  int              lenintbytes;
{
  int              i;
  unsigned int     rval;

  i = 0;

  rval = 0;

  while (i < lenintbytes) {
    rval = rval << 8;

    rval = rval + (unsigned int)intbytes[i];

    i++;
  }

  return (rval);
}
    
/**************************************************************************/

void decodetrap(inpacket, packetsize)
  unsigned char   *inpacket;
  int              packetsize;
{
  int              i;
  int              j;
  int              tlvtype;
  int              tlvlength;
  int              tlvsize;
  char             c;

  i = 0;

  while (i < packetsize) {
    tlvtype = inpacket[i];

    i++;

    if (inpacket[i] <= 127) {
      tlvlength = 1;

      tlvsize = inpacket[i];

      i++;
    } else {
      tlvlength = inpacket[i] - 128;

      i++;

      tlvsize = 0;

      for (j = 0 ; j < tlvlength ; j++) {
        tlvsize = tlvsize << 8;

        tlvsize = tlvsize + inpacket[i];

        i++;
      }
    }

/*
    printf("Code: 0x%02X   Length: %u\n", tlvtype, tlvsize);
*/

    switch (tlvtype) {
      case 0x30:   /* sequence */
        printf("Sequence compound type 0x%02X: following through\n", tlvtype);
        break;

      case 0xA4:   /* PDU trap */
        printf("PDU TRAP compound type 0x%02X: following through\n", tlvtype);
        break;

      case 0x02:   /* integer */
        printf("Integer: %u\n", getint(inpacket + i, tlvsize));
        i += tlvsize;
        break;

      case 0x43:   /* uptime ticks */
        printf("Uptime ticks: %u\n", getint(inpacket + i, tlvsize));
        i += tlvsize;
        break;

      case 0x40:   /* source IP of trap */
        printf("IPv4: %d.%d.%d.%d\n", (unsigned int)inpacket[i], (unsigned int)inpacket[i+1], (unsigned int)inpacket[i+2], (unsigned int)inpacket[i+3]);
        i += tlvsize;
        break;

      case 0x04:   /* ASCII string */
        printf("String: ");

        for (j = 0 ; j < tlvsize ; j++) {
          c = inpacket[i+j];

          if ((c >= 32) && (c <= 126)) {
            putchar(c);
          } else {
            putchar('_');
          }
        }
        
        putchar('\n');

        i += tlvsize;
        break;

      case 0x06:   /* OID */
        printf("OID: ");
        outputoid(inpacket + i, tlvsize);
   
        i += tlvsize;
        break;

      default:
        printf("WARNING: Unknown type 0x%02X - following through but results cannot be trusted\n", tlvtype);
        break;
    }
  }

  return;
}

/**************************************************************************/

void snmptrapreceiver(mastersocket)
  int   mastersocket;
{
  struct sockaddr_in   fromendpointaddress;
  unsigned char       *inpacket[MAX_PACKET_LENGTH + sizeof(unsigned char)];
  int                  n;
  int                  slavesocket;
  int                  addresslength;
  pid_t                forkedpid;
  pid_t                childpid;
  
  while (TRUE) {
    n = recvfrom(mastersocket, inpacket, MAX_PACKET_LENGTH, 0, (struct sockaddr *)&fromendpointaddress, &addresslength);

    if (n < 0) {
      fprintf(stderr, "%s: recvfrom call failed: %s\n", progname, strerror(errno));
      exit(1);
    }

    if (debug) {
      printf("IPv4 (reversed): 0x%08x   Length (hex): 0x%04X   Length (dec): %u\n", fromendpointaddress.sin_addr, n, n);
    }

    if (debug) {
      displaypacketbuffer(inpacket, n, FALSE);
    }

    if (debug) {
      decodetrap(inpacket, n);
    }
  }

  /* control never gets here */
}

/**************************************************************************/

/*
 *  Main
 */

main(argc, argv)
  int   argc;
  char *argv[];
{
  char                 *servicename;
  char                 *protocolname;
  int                   i;
  struct servent       *serviceentry;
  struct protoent      *protocolentry;
  struct sockaddr_in    endpointaddress;
  int                   s;

  progname = basename(argv[0]);

  debug = 1;

  if (debug) {
    printf("The name of this program is \"%s\"\n", progname);
  }

  if (argc > 1) {
    if (((argc - 1) % 2) != 0) {
      fprintf(stderr, "%s: there must be an even number of command line arguments\n", progname);
      exit(1);
    }
  }
  
  servicename = "snmp-trap";
  protocolname = "udp";

  for ( i = 1; i < argc ; i = i + 2 ) {
    if (strcmp(argv[i], "-p") == 0) {
      servicename = argv[i+1];
    } else {
      fprintf(stderr, "%s: unrecognised command line argument \"%s\"\n", progname, argv[i]);
      exit(1);
    }
  }

  if ( (strcmp(protocolname, "udp") != 0) && (strcmp(protocolname, "tcp") != 0) ) {
    fprintf(stderr, "%s: protocol name type must be either udp or tcp\n", progname);
    exit(1);
  }

  /* bzero((char *)&endpointaddress, sizeof(endpointaddress)); */
  memset((char *)&endpointaddress, 0, sizeof(endpointaddress));

  endpointaddress.sin_family = AF_INET;
  endpointaddress.sin_addr.s_addr = INADDR_ANY;

  serviceentry = getservbyname(servicename, protocolname);

  if (serviceentry != NULL) {
    endpointaddress.sin_port = htons(ntohs((u_short)serviceentry->s_port));
  } else {
    endpointaddress.sin_port = htons((u_short)atoi(servicename));
  }

  if (endpointaddress.sin_port == 0) {
    fprintf(stderr, "%s: cannot lookup service name \"%s\"\n", progname, servicename);
    exit(1);
  }

  if (debug) {
    printf("Service port number is %u\n", ntohs((u_short)endpointaddress.sin_port));
  }

  protocolentry = getprotobyname(protocolname);

  if (protocolentry == 0) {
    fprintf(stderr, "%s: cannot lookup protocol name \"%s\"\n", progname, protocolname);
    exit(1);
  }

  if (debug) {
    printf("Protocol number is %u\n", protocolentry->p_proto);
  }

  if (strcmp(protocolname, "udp") == 0) {
    s = socket(PF_INET, SOCK_DGRAM, protocolentry->p_proto);
  } else {
    s = socket(PF_INET, SOCK_STREAM, protocolentry->p_proto);
  }

  if (s < 0) {
    fprintf(stderr, "%s: unable to allocate socket: %s\n", progname, strerror(errno));
    exit(1);
  }

  if (debug) {
    printf("Socket number is %u\n", s);
  }

  if (bind(s, (struct sockaddr *)&endpointaddress, sizeof(endpointaddress)) < 0) {
    fprintf(stderr, "%s: unable to bind socket (are you root?): %s\n", progname, strerror(errno));
    exit(1);
  }

  if (debug) {
    printf("Socket bind call ok\n");
  }

  if (debug) {
    printf("Socket listen call ok\n");
  }

  snmptrapreceiver(s);

  exit(0);
}
