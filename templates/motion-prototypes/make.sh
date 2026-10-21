#!/bin/bash
# make.sh <A|B>  -> renders frames, audio, loudnorm (two-pass), mux to ../clipX.mp4, plus 0.5s sheet
set -e
# Paths: B = this directory (clip*.html, render.py, audio.py, sheet.py, cues*.json);
# V = a reference video whose audio track supplies the voice (example: the Harness² v3 cut).
B=${B:-$(cd "$(dirname "$0")" && pwd)}
O=${O:-$B/..}; V=${V:-<work>/voice_source.mp4}
X=$1; SUF=${2:-}; TP=${3:--1.5}
if [ "$X" = A ]; then S=23.0; E=37.95; else S=94.4; E=128.7; fi
cd $B
rm -rf $O/frames$X; python3 render.py clip$X$SUF.html $O/frames$X --workers 2 --cues cues$X.json
ffmpeg -y -loglevel error -framerate 30 -i $O/frames$X/f_%05d.png -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p $O/v$X.mp4
python3 audio.py cues$X.json $V $S $E mix$X.wav 1
J=$(ffmpeg -hide_banner -i mix$X.wav -af loudnorm=I=-16:TP=$TP:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
gi() { echo "$J" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -loglevel error -i mix$X.wav -af loudnorm=I=-16:TP=$TP:LRA=11:measured_I=$(gi input_i):measured_TP=$(gi input_tp):measured_LRA=$(gi input_lra):measured_thresh=$(gi input_thresh):offset=$(gi target_offset):linear=true,aresample=48000 -ar 48000 norm$X.wav
ffmpeg -y -loglevel error -i $O/v$X.mp4 -i norm$X.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $O/clip$X$SUF.mp4
ffmpeg -hide_banner -i $O/clip$X$SUF.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
# contact sheet every 0.5s
rm -rf $O/sh$X; mkdir -p $O/sh$X
n=$(ls $O/frames$X | wc -l); for ((i=0;i<n;i+=15)); do cp $O/frames$X/$(printf f_%05d.png $i) $O/sh$X/; done
python3 sheet.py $O/sheet$X$SUF.png 8 400 --fps=30 $(ls $O/sh$X/*.png | sort)
