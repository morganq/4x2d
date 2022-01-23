#!/bin/bash
animtoconvert=$1
nframe=$2  # every nth frame
fps=$3  # 100 / fps actually

# example: ./fc.sh somevid.mp4 2 3

# Split in frames
convert $animtoconvert +map +adjoin temp_%04d.gif

# select the frames for the new animation
j=0
for i in $(ls temp_*gif); do 
    if [ $(( $j%${nframe} )) -eq 0 ]; then 
        cp $i sel_`printf %04d $j`.gif; 
    fi; 
    j=$(echo "$j+1" | bc); 
done

# Create the new animation & clean up everything
convert -layers OptimizeTransparency -delay $fps $( ls sel_*) new_animation.gif
rm temp_* sel_*
