which screen
screen=$?
if [ $screen -eq 1 ]; then       
    echo "nameserver 8.8.4.4" > /etc/resolv.conf
    pacman -Sy --noconfirm screen
    screen=$?
    echo "termcapinfo xterm* ti@:te@" > ~/.screenrc
fi

screen -ls
sleep 0.5

if [ $screen -eq 0 ]; then      
    echo "Using GNU screen.."
    if [ "$(screen -ls | grep dnc)" = "" ]; then
        sleep 0.01
    else
        echo "Stopping previous dnc prog..."
        screen -S dnc -X stuff "q^M"
        sleep 10
        if [ "$(screen -ls | grep dnc)" = "" ]; then
            sleep 0.01
        else
            echo "nothing"
        fi
    fi
fi

screen -ls

cd /dnc
./bash/kill.sh
