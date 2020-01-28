#!/bin/sh -ex

src=$1
dest="result.gif"
font=$2
header=$3
footer=$4

width=$(identify -format %w "${src}")
caption_height=$((width/8))
strokewidth=$((width/500))

ffmpeg -i "${src}" \
 -vf "fps=10,scale=320:-1:flags=lanczos" \
 -c:v pam \
 -f image2pipe - | \
 convert -delay 10 \
 - -loop 0 \
 -layers optimize \
 output.gif

convert "output.gif" \
 -pointsize 120 \
 -gravity center \
 -font "${font}" \
 -stroke black \
 -fill white \
 -strokewidth 3 \
 -draw "text 0,90 ${header}" \
 "${dest}"

rm output.gif