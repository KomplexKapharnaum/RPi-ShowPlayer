
for ip in $(nmap -p 22 2.0.2.1/24 |grep 2.0.2 | grep -v done |cut -d"(" -f 2 | cut -d")" -f 1 ); do 
	if [[ "$@" == "$ip" ]]
	then
	    >&2 echo "Skipping $ip"
	else
	    echo "$ip"
	fi
done

