import math,wave,struct,random
from pathlib import Path
out=Path(__file__).resolve().parent/'Audio';out.mkdir(exist_ok=True)
rate=22050
random.seed(4)
for name,duration in [('Breath',2.5),('Heart',.25),('Chime',1.6),('Swat',.18)]:
 samples=[];smooth=0
 for n in range(int(rate*duration)):
  t=n/rate;u=t/duration
  if name=='Breath':
   smooth=smooth*.92+random.uniform(-1,1)*.08
   v=smooth*math.sin(math.pi*u)*.8+math.sin(t*2*math.pi*330)*.018*math.sin(math.pi*u)
  elif name=='Heart':
   v=math.sin(2*math.pi*(58*t-15*t*t))*math.exp(-t*26)*.65
   if t>.1:v+=math.sin(2*math.pi*68*(t-.1))*math.exp(-(t-.1)*40)*.35
  elif name=='Chime':
   v=sum(math.sin(2*math.pi*f*t)*math.exp(-t*(2+i*.4)) for i,f in enumerate([523.25,659.25,783.99]))*.16*min(t*80,1)
  else:v=math.sin(2*math.pi*(650*t-1200*t*t))*math.exp(-t*28)*.35
  samples.append(struct.pack('<h',int(max(-1,min(1,v))*28000)))
 with wave.open(str(out/(name+'.wav')),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(b''.join(samples))
print('AUDIO_CREATED')
