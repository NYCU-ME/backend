cd ./config/named/keys
dnssec-keygen -f KSK -a ECDSAP256SHA256 -b 4096 -n ZONE nycu.me.
dnssec-keygen -a ECDSAP256SHA256 -b 1024 -n ZONE nycu.me.
