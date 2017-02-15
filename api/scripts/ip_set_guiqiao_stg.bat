netsh interface ipv4 set address "本地连接" static %1 255.255.255.0 %2
netsh interface ipv4 add dnsserver name="本地连接" address="10.12.101.251"
netsh interface ipv4 add dnsserver name="本地连接" address="10.12.101.252"
netdom renamecomputer %computername% /newname:%3 /userd:administrator /passwordd:WEB@ymatou.com.2015 /force /reboot:1
