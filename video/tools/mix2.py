#!/usr/bin/env python3
"""v2 mix: voice bus (clear, forward) + effects bus ducked by the voice (sidechain) + two-pass loudness normalisation.
Everything is generated here; no third-party audio."""
import json, subprocess, sys
lang=sys.argv[1]
cfg=json.load(open(f'cfg_{lang}.json')); total=cfg['total']; segs=cfg['segs']; sc=cfg['scenes']
inputs=[]; filt=[]; V=[]; F=[]; k=[0]
def inp(*a):
    inputs.extend(a); k[0]+=1; return k[0]-1
def lav(expr,dur):
    return inp('-f','lavfi','-t',f'{dur}','-i',expr)
for s in segs:
    i=inp('-i',s['wav']); ms=int(round(s['t0']*1000))
    filt.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=mono,adelay={ms}|{ms},apad=whole_dur={total}[v{i}]"); V.append(f'[v{i}]')
def fx(i,t,vol,name,extra=''):
    ms=int(round(max(0,t)*1000))
    filt.append(f"[{i}:a]aformat=channel_layouts=mono,{extra}volume={vol},adelay={ms}|{ms},apad=whole_dur={total}[{name}]"); F.append(f'[{name}]')
i=lav("aevalsrc='(sin(2*PI*52*t)+0.5*sin(2*PI*104*t))*exp(-5*t)':d=1.0:s=44100",1.0); fx(i,0.0,0.7,'hit')
i=lav("anoisesrc=d=0.5:c=brown:a=0.6:r=44100",0.5); fx(i,0.0,0.5,'nz','afade=t=out:st=0.05:d=0.45,')
for n,name in enumerate(['intro','crypto','ws','asia','oil','fed','out']):
    i=lav("anoisesrc=d=0.6:c=pink:a=0.5:r=44100",0.6)
    fx(i,sc[name][0]-0.1,0.22,f'wh{n}','highpass=f=500,lowpass=f=5000,afade=t=in:d=0.25,afade=t=out:st=0.3:d=0.3,')
i=lav("aevalsrc='(sin(2*PI*523.25*t)+sin(2*PI*659.25*t)+sin(2*PI*783.99*t))/3*exp(-2.6*t)':d=1.6:s=44100",1.6); fx(i,sc['fed'][0]+0.45,0.4,'chime')
i=lav(f"aevalsrc='0.05*(sin(2*PI*110*t)+0.7*sin(2*PI*164.81*t)+0.5*sin(2*PI*220*t))*(0.75+0.25*sin(2*PI*0.2*t))':d={total}:s=44100",total)
filt.append(f"[{i}:a]aformat=channel_layouts=mono,afade=t=in:d=1.5,afade=t=out:st={total-1.8}:d=1.8,volume=0.5[pad]"); F.append('[pad]')
g=''.join(V)+f"amix=inputs={len(V)}:normalize=0:duration=longest,asplit=2[vo][vsc]"
g2=''.join(F)+f"amix=inputs={len(F)}:normalize=0:duration=longest[fxm]"
g3="[fxm][vsc]sidechaincompress=threshold=0.015:ratio=12:attack=8:release=350:makeup=1[fxd]"
g4=f"[vo][fxd]amix=inputs=2:normalize=0:duration=longest,atrim=0:{total},aformat=sample_rates=44100:channel_layouts=stereo[pre]"
fc=';'.join(filt+[g,g2,g3,g4])
pre=f'pre_{lang}.wav'
subprocess.run(['ffmpeg','-y','-loglevel','error']+inputs+['-filter_complex',fc,'-map','[pre]',pre],check=True)
# two-pass loudnorm: measure, then apply a single linear gain (no pumping)
T="I=-14:LRA=7:TP=-1.5"
r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',pre,'-af',f'loudnorm={T}:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rindex('{'):r.rindex('}')+1])
af=(f"loudnorm={T}:measured_I={j['input_i']}:measured_LRA={j['input_lra']}:measured_TP={j['input_tp']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aformat=sample_rates=44100:channel_layouts=stereo")
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',pre,'-af',af,'-c:a','aac','-b:a','192k',f'audio_{lang}.m4a'],check=True)
d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'audio_{lang}.m4a']).decode())
print(lang,'audio',round(d,2),'s (video',total,'s) measured I',j['input_i'],'-> target -14')
