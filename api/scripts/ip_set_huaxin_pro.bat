netsh interface ipv4 set address "��������" static %1 255.255.255.0 %2
netsh interface ipv4 add dnsserver name="��������" address="10.10.15.110"
netsh interface ipv4 add dnsserver name="��������" address="10.10.15.111"
netdom renamecomputer %computername% /newname:%3 /userd:administrator /passwordd:WEB@ymatou.com.2015 /force /reboot:1
