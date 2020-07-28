#!/bin/bash

for SVG in scalable/mnotify-none-wireframe-{dark,light}{,-transparent}.svg  scalable/mnotify-some-wireframe.svg; do 

    echo "#------------_ $SVG" ; 
    for SIZE in 8 16 22 24 32 48 64 96 128 256; do 
        DIR=./${SIZE}x${SIZE}/apps
        [ -d $DIR ] || mkdir -p $DIR
        PNG="${SVG##*/}"
        PNG="${PNG%.svg}.png"
        CMD="inkscape -z -h $SIZE -w $SIZE -e $DIR/$PNG -f $SVG" 
        echo $CMD; 
        $CMD  2>/dev/null;  
    done;
done
