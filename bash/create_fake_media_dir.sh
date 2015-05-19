#!/bin/bash

cd "$2"
mkdir "$2/video"
mkdir "$2/audio"
cd "$1"
for f in $(find $1); do
    #echo $f
    #echo $1
    f=${f#$1}
    echo "$2/$f"
    touch "$2/$f"
done