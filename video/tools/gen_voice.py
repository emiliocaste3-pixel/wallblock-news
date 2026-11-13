#!/usr/bin/env python3
"""v2 voice: SVOX Pico per segment -> trim silences -> clarity chain -> pad to the scene slot. Writes audio/<lang>_<seg>.wav,
durations.json (slot lengths) and speech.json (actual speech lengths, used for caption timing)."""
import subprocess, json, sys, wave, os
sys.path.insert(0,'.')
from segments import SEG, MIN, SPEED
CODE={'es':'es-ES','en':'en-US'}
# clarity chain: remove rumble, tame level jumps, add a little presence for consonants, then limit
CHAIN=("highpass=f=75,"
       "acompressor=threshold=0.06:ratio=3.5:attack=4:release=70:makeup=2.5,"
       "equalizer=f=3000:t=q:w=1.1:g=3,equalizer=f=6500:t=q:w=1.2:g=1.5,"
       "alimiter=limit=0.89:level=disabled")
TRIM=("silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.04,"
      "areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.06,areverse")
def dur(f):
    w=wave.open(f); return w.getnframes()/w.getframerate()
os.makedirs('audio',exist_ok=True); os.makedirs('pico2',exist_ok=True)
langs=sys.argv[1:] or ['es','en']
try: D=json.load(open('durations.json'))
except Exception: D={}
try: P=json.load(open('speech.json'))
except Exception: P={}
for l in langs:
    D[l]={}; P[l]={}
    for name,say,cap in SEG[l]:
        raw=f'pico2/{l}_{name}.raw.wav'; mid=f'pico2/{l}_{name}.wav'; out=f'audio/{l}_{name}.wav'
        subprocess.run(['pico2wave','-l',CODE[l],'-w',raw,f"<speed level='{SPEED[l]}'>{say}</speed>"],check=True)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',raw,'-af',TRIM+','+CHAIN,'-ar','44100','-ac','1',mid],check=True)
        sp=dur(mid); slot=max(sp+0.12,MIN[name])
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',mid,'-af',f'apad=whole_dur={slot:.3f}','-ar','44100','-ac','1',out],check=True)
        D[l][name]=round(slot,3); P[l][name]=round(sp,3)
        print(f'{l} {name:7} speech {sp:5.2f}s  slot {slot:5.2f}s')
    print(l,'speech total',round(sum(P[l].values()),1),'slots total',round(sum(D[l].values()),1))
json.dump(D,open('durations.json','w'),indent=1); json.dump(P,open('speech.json','w'),indent=1)
