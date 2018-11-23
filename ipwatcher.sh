#!/bin/sh
#
# @(!--#) @(#) ipwatcher.sh, version 001, 09-march-2017
#
# watch ip addresses appear and disappear on a range of IP addresses
#

#
# Main
#

progname=`basename $0`

if [ $# -lt 2 ]
then
  echo "$progname: usage: $progname startip endip" 1>&2
  exit 1
fi

startip=$1
endip=$2

lastfile=/var/tmp/$progname.$$.last.out
thisfile=/var/tmp/$progname.$$.this.out

cp /dev/null $lastfile

while true
do
  echo "=============================================="
  fping -g $startip $endip 2>/dev/null | grep "is alive" | sort | uniq > $thisfile

  diff $lastfile $thisfile

  sleep 5

  cp $thisfile $lastfile
done


