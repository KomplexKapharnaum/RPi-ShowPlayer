#!/usr/bin/env bash

KXKM_GIT_SERVER="kxkm.ddns.net"
TMP_DIR="/tmp/.tmp_kpi_scenraio_install"
ARCH="unknown"
SCRIPTPATH="$( cd "$(dirname $0)" ; pwd -P )"
INSTALLPATH="$SCRIPTPATH/libs/"

NO_COLOUR="\033[0m"
ERROR_COLOUR="\033[1;31m"
SUCESS_COLOUR="\033[1;35m"


function fatal_error {
    # $1  : status code
    # $2* : error message
    # $3* : success message
    if [ $1 -ne 0 ]; then
        if [ $# -gt 1 ]; then
            echo -e $ERROR_COLOUR"ERROR : $2 => ABORT$NO_COLOUR"
        fi
        exit $1
    elif [ $# -gt 2 ]; then
            echo -e $SUCESS_COLOUR"SUCESS : $3"$NO_COLOUR
    fi
    return $1
}

#function fatal_error {
#    # $1  : status code
#    # $2* : error message
#    # $3* : success message
#    error $*
#    if [ $? -ne 0 ]; then exit $1; fi
#}

function create_tmp_dir {
    if [ ! -d $TMP_DIR ]; then
        mkdir -p $TMP_DIR
        fatal_error $? "Impossible to create TMP_DIR at $TMP_DIR"
    fi
}

function create_install_dir {
    if [ ! -d $INSTALLPATH ]; then
        mkdir -p $INSTALLPATH
        fatal_error $? "Impossible to create INSTALLPATH at $INSTALLPATH"
    fi
}
function get_arch {
    if [ $ARCH == "unknown" ]; then
        ARCH=$(uname -m)
    fi
    echo $ARCH
}

function install_lib {
    # $1  : libname (must be unique)
    # $2  : git repo
    # $3  : branch
    # $4  : install script : (noscript, scriptname)

    create_tmp_dir
    create_install_dir

    # Clone repo
    cd $TMP_DIR
    if [ -d $1 ]; then rm -rf $1; fi
    git clone $2 $1
    fatal_error $? "Impossible to clone git repo"
    cd $1

    # Change branch
    git checkout $3
    fatal_error $? "Impossible to change branch"

    # Install script
    if [ $4 != "noscript" ]; then
        [ -x "./$4" ]
        fatal_error $? "Installation script is not executable or present"
        # Run script
        cmd_to_run="./$4 $(get_arch)"
        eval $cmd_to_run
        fatal_error $? "Installation script failled"
    fi

    # Copy files
    cp -a ./* "$INSTALLPATH"
    fatal_error $? "Impossible to copy data from lib to install dir $INSTALLPATH" "[OK] $1"

    # Cleanup
    #    cd ../
    #    rm -rf $1
}

LIB_RTPLIB=("rtplib" "ssh://git@$KXKM_GIT_SERVER/kpi_lib_rtplib.git" "master" "install.sh")

install_lib ${LIB_RTPLIB[0]} ${LIB_RTPLIB[1]} ${LIB_RTPLIB[2]} ${LIB_RTPLIB[3]}