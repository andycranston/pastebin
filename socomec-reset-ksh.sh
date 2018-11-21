#
# reset socomec diris 720 BCMS kWh counters
#

socomecip=10.1.3.100
snmpwrite=private

i=1101

while [ $i -le 1244 ]
do
  echo snmpset -v 1 -c $snmpwrite $socomecip 1.3.6.1.4.1.24436.1.3.2.8.1.$i.0 i 0
       snmpset -v 1 -c $snmpwrite $socomecip 1.3.6.1.4.1.24436.1.3.2.8.1.$i.0 i 0

  i=`expr $i + 1`
done
