import json,sys
sys.path.insert(0,'.')
from segments import SEG
dur=json.load(open('durations.json')); spk=json.load(open('speech.json'))
LEAD,GAP,TAIL=0.5,0.2,1.5
STR={
'es':dict(date='VIE 13 NOV 2026 · APERTURA',pill='ALERTA CRIPTO',btc1='BITCOIN',btc2='SE HUNDE',price='< 69.000 $',chip1='Mínimos desde agosto',chip2='liquidados',q='¿Contagia a Wall Street?',
 teaser='AL FINAL: LA CIFRA DE DICIEMBRE',introTitle='APERTURA<br>DE WALL STREET',introSub='Viernes 13 de noviembre',
 cTitle='CRIPTO',cLiq='LIQUIDACIONES · 24 H',cLong='Largas · ≈ 89 %',cShort='Cortas · ≈ 11 %',cEtf='ETF DE BITCOIN',cEtfx='Salidas 5 sesiones seguidas',
 wTitle='WALL STREET ABRE',idx=[dict(n='S&P 500',v='−0,1 %',up=False),dict(n='NASDAQ',v='−0,4 %',up=False),dict(n='DOW JONES',v='+0,3 %',up=True)],
 ppiT='PRECIOS AL PRODUCTOR · OCT.',ppiV='0,3 % vs 0,4 %',ppiS='más suave de lo previsto',wNote='9:38 ET (15:38 h europea): datos tras la apertura',
 aTitle='ASIA · CIERRE',asia=[dict(n='JAPÓN · NIKKEI',v='+0,5 %',p=0.5,up=True),dict(n='COREA · KOSPI',v='−1 %',p=-1,up=False),dict(n='HONG KONG · HANG SENG',v='−1,5 %',p=-1.5,up=False)],
 oTitle='PETRÓLEO',oName='BRENT',oVal='≈ 96 $',oChg='▲ +3,3 % el jueves',oChip='IRÁN',
 fTitle='FED · 9 DE DICIEMBRE',fSub='Probabilidad de subida de tipos',fL1='CUARTO DE PUNTO',f87='87 % · 0,25',f13='13 %',fL2='El 13 % apuesta por medio punto · Fuente: CME FedWatch',
 outT1='SIGUE<br>WALLBLOCK NEWS',outT2='Información, no asesoramiento financiero',foot='Datos: 13 nov · 15:40 h europea. Fuentes: CoinGlass, CME FedWatch, CNBC, InvestingLive.'),
'en':dict(date='FRI NOV 13, 2026 · MARKET OPEN',pill='CRYPTO ALERT',btc1='BITCOIN',btc2='CRASHES',price='< $69,000',chip1='Lowest since August',chip2='liquidated',q='Will Wall Street catch it?',
 teaser="AT THE END: DECEMBER'S NUMBER",introTitle='WALL STREET<br>MARKET OPEN',introSub='Friday, November 13',
 cTitle='CRYPTO',cLiq='LIQUIDATIONS · 24 H',cLong='Longs · ≈ 89%',cShort='Shorts · ≈ 11%',cEtf='BITCOIN ETFs',cEtfx='5 straight sessions of outflows',
 wTitle='WALL STREET OPENS',idx=[dict(n='S&P 500',v='−0.1%',up=False),dict(n='NASDAQ',v='−0.4%',up=False),dict(n='DOW JONES',v='+0.3%',up=True)],
 ppiT='PRODUCER PRICES · OCT.',ppiV='0.3% vs 0.4%',ppiS='softer than expected',wNote='9:38 ET (15:38 European time): data after the open',
 aTitle='ASIA · CLOSE',asia=[dict(n='JAPAN · NIKKEI',v='+0.5%',p=0.5,up=True),dict(n='S. KOREA · KOSPI',v='−1%',p=-1,up=False),dict(n='HONG KONG · HANG SENG',v='−1.5%',p=-1.5,up=False)],
 oTitle='OIL',oName='BRENT',oVal='≈ $96',oChg='▲ +3.3% on Thursday',oChip='IRAN',
 fTitle='FED · DECEMBER 9',fSub='Odds of a rate hike',fL1='A QUARTER POINT',f87='87% · 0.25',f13='13%',fL2='13% bet on a half point · Source: CME FedWatch',
 outT1='FOLLOW<br>WALLBLOCK NEWS',outT2='Information, not financial advice',foot='Data: Nov 13 · 15:40 European time. Sources: CoinGlass, CME FedWatch, CNBC, InvestingLive.')}
def build(lang):
    t=LEAD; segs=[]
    for name,say,cap in SEG[lang]:
        d=dur[lang][name]; cap=cap.replace(' %','\u00a0%').replace(' $','\u00a0$').replace('S&P 500','S&P\u00a0500').replace('M$','M$'); segs.append(dict(name=name,t0=round(t,3),t1=round(t+d,3),sp=spk[lang][name],cap=cap,wav=f'audio/{lang}_{name}.wav')); t+=d+GAP
    by={s['name']:s for s in segs}; total=round(segs[-1]['t1']+TAIL,3)
    sc={'hook':[0,round(by['hook2']['t1']+0.1,3)],'intro':[round(by['intro']['t0']-0.15,3),round(by['intro']['t1']+0.05,3)],'crypto':[round(by['crypto']['t0']-0.15,3),round(by['crypto']['t1']+0.05,3)],
        'ws':[round(by['ws']['t0']-0.15,3),round(by['ws']['t1']+0.05,3)],'asia':[round(by['asia']['t0']-0.15,3),round(by['asia']['t1']+0.05,3)],'oil':[round(by['oil']['t0']-0.15,3),round(by['oil']['t1']+0.05,3)],
        'fed':[round(by['fed']['t0']-0.15,3),round(by['fed']['t1']+0.05,3)],'out':[round(by['outro']['t0']-0.15,3),total]}
    return dict(lang=lang,T=STR[lang],segs=segs,scenes=sc,total=total,hook2start=by['hook2']['t0'],teaser=[round(by['hook2']['t0']-0.1,3),round(by['fed']['t0']+0.9,3)])
for l in ('es','en'):
    c=build(l); json.dump(c,open(f'cfg_{l}.json','w'),ensure_ascii=False,indent=1)
    print(l,'total %.1fs'%c['total'],{k:(round(v[0],1),round(v[1],1)) for k,v in c['scenes'].items()},'teaser',c['teaser'])
