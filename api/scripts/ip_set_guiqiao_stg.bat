netsh interface ipv4 set address "��������" static %1 255.255.255.0 %2
netsh interface ipv4 add dnsserver name="��������" address="10.12.101.251"
netsh interface ipv4 add dnsserver name="��������" address="10.12.101.252"
netdom renamecomputer %computername% /newname:%3 /userd:administrator /passwordd:WEB@ymatou.com.2015 /force /reboot:1
