DEST_IP=`cat`
cmd=$1
SEDLINE=""
N=0
shift
while test ${#} -gt 0
do
	let N=$N+1
  	SEDLINE=$SEDLINE" -e s/@$N/\"$1\"/"
  	shift
done
echo ""
echo $SEDLINE
if [ $SEDLINE = "" ]; then
	SEDLINE=" -e s/xxx/xxx/ "
fi
for ip in $DEST_IP; do 
	echo "Do on $ip .."
	ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@$ip bash -c "'
$(sed $SEDLINE $cmd)
'" &
done
	
	# -e "s/@1/$2/" -e "s/@2/$3/" -e "s/@3/$4/"
