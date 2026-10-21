set -e
# D = this directory; ../h2rev/v.mp4 = voice source video, ../h2proto/build = clipB build dir (example layout)
D=${D:-$(cd "$(dirname "$0")" && pwd)}; cd $D
rm -rf frD; python3 render.py clipD.html frD --workers 2 --cues cuesD.json
rm -rf frM; mkdir -p frM; i=0
for f in $(ls frB/*.png | sort) $(ls frD/*.png | sort); do ln -s $D/$f frM/$(printf f_%05d.png $i); i=$((i+1)); done
ffmpeg -y -loglevel error -framerate 30 -i frM/f_%05d.png -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p vM.mp4
# voice: clipB part (6.5s) + 0.6s hold, then 0.5s lead + clipC voice 198.35-217.55 (19.2s) + 0.4s tail = 27.2s
ffmpeg -y -loglevel error -ss 122.7 -to 129.2 -i ../h2rev/v.mp4 -vn -ac 2 -ar 48000 -af "apad=pad_dur=1.1" va.wav
ffmpeg -y -loglevel error -ss 198.35 -to 217.55 -i ../h2rev/v.mp4 -vn -ac 2 -ar 48000 -af "afade=t=out:st=19.08:d=0.12,apad=pad_dur=0.4" vb.wav
ffmpeg -y -loglevel error -i va.wav -i vb.wav -filter_complex "[0][1]concat=n=2:v=0:a=1" -ar 48000 voiceM.wav
python3 - <<'P'
import json
b=json.load(open('../h2proto/build/cuesB.json'))['cues']; c=json.load(open('cuesD.json'))
cues=[dict(x,t=round(x['t']-28.3,3)) for x in b if 28.3<=x['t']<34.8]+[dict(x,t=round(x['t']+7.1,3)) for x in c['cues']]
json.dump({'duration':7.1+c['duration'],'cues':cues},open('cuesM.json','w')); print(7.1+c['duration'])
P
python3 audio.py cuesM.json voiceM.wav 0 27.2 mixM.wav 1
TP=-2.0
J=$(ffmpeg -hide_banner -i mixM.wav -af loudnorm=I=-16:TP=$TP:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
gi() { echo "$J" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -loglevel error -i mixM.wav -af loudnorm=I=-16:TP=$TP:LRA=11:measured_I=$(gi input_i):measured_TP=$(gi input_tp):measured_LRA=$(gi input_lra):measured_thresh=$(gi input_thresh):offset=$(gi target_offset):linear=true,aresample=48000 -ar 48000 normM.wav
ffmpeg -y -loglevel error -i vM.mp4 -i normM.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart mixdemo2.mp4
ffprobe -v error -show_entries format=duration mixdemo2.mp4
ffmpeg -hide_banner -i mixdemo2.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
