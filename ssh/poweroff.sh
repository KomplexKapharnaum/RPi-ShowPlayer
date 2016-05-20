which screen
screen=$?
if [ $screen -eq 1 ]; then       
    echo "nameserver 8.8.4.4" > /etc/resolv.conf
    pacman -Sy --noconfirm screen
    screen=$?
    echo "termcapinfo xterm* ti@:te@" > ~/.screenrc
fi

if [ $screen -eq 0 ]; then      
    echo "Using GNU screen.."
    if [ "$(screen -ls | grep dnc)" = "" ]; then
        sleep 0.01
    else
        echo "Stopping previous dnc prog..."
        screen -S dnc -X stuff "q^M"
        sleep 13
        if [ "$(screen -ls | grep dnc)" = "" ]; then
            sleep 0.01
        else
            echo "Stopping previous dnc screen session..."
            screen -X -S dnc quit
            sleep 0.1
        fi
    fi
    
fi

screen -ls

sleep 1
poweroff
