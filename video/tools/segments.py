# v2: shorter, calmer narration read at a natural pace. "say" is what the voice reads (numbers spelled out,
# foreign names respelled for the Spanish voice); "cap" is the on-screen caption. MIN = minimum scene length (s)
# so every on-screen animation (cards, bars, notes) has time to appear.
SEG={
'es':[
 ('hook1',"¡Bitcóin se hunde por debajo de sesenta y nueve mil dólares! Más de mil cuatrocientos millones liquidados.","¡Bitcoin se hunde por debajo de 69.000 $! Más de 1.400 M$ liquidados"),
 ('hook2',"¿Contagia a Uol Strit? Quédate: al final, la cifra de diciembre.","¿Contagia a Wall Street? Quédate: al final, la cifra de diciembre"),
 ('intro',"Soy Uali. Apertura de Uol Blok Niús.","Soy Wallie. Apertura de WallBlock News"),
 ('crypto',"Casi todo, posiciones largas. Y los E T F de bitcóin, cinco sesiones de salidas.","Casi todo, posiciones largas. Y los ETF de bitcoin, 5 sesiones de salidas"),
 ('ws',"Uol Strit abre sin rumbo: el Nasdak cae y el Dau sube.","Wall Street abre sin rumbo: el Nasdaq cae y el Dow sube"),
 ('asia',"Asia cierra mixta: sube Japón; caen Corea y Jong Kong.","Asia cierra mixta: sube Japón; caen Corea y Hong Kong"),
 ('oil',"El Brent, cerca de noventa y seis dólares, tras subir un tres por ciento el jueves.","El Brent, cerca de 96 $, tras subir un 3 % el jueves"),
 ('fed',"¿Y diciembre? Casi descontada una subida de la Fed: ochenta y siete por ciento, cuarto de punto.","¿Y diciembre? Casi descontada una subida de la Fed: 87 %, cuarto de punto"),
 ('outro',"Sigue Uol Blok Niús. Información, no asesoramiento financiero.","Sigue WallBlock News · Información, no asesoramiento financiero"),
],
'en':[
 ('hook1',"Bitcoin is crashing below sixty-nine thousand dollars! Over one point four billion liquidated.","Bitcoin is crashing below $69,000! Over $1.4B liquidated"),
 ('hook2',"Will Wall Street catch it? Stay to the end for December's big number.","Will Wall Street catch it? Stay to the end for December's big number"),
 ('intro',"I'm Wallie. This is the WallBlock News market open.","I'm Wallie. This is the WallBlock News market open"),
 ('crypto',"Almost all longs wiped out. And bitcoin ETFs: five straight sessions of outflows.","Almost all longs wiped out. And bitcoin ETFs: 5 straight sessions of outflows"),
 ('ws',"Wall Street opens directionless: Nasdaq down, Dow up.","Wall Street opens directionless: Nasdaq down, Dow up"),
 ('asia',"Asia closes mixed: Japan up; Korea and Hong Kong down.","Asia closes mixed: Japan up; Korea and Hong Kong down"),
 ('oil',"Brent hovers near ninety-six dollars after jumping three percent on Thursday.","Brent near $96 after jumping 3% on Thursday"),
 ('fed',"And December? A Fed hike is nearly priced in: eighty-seven percent, a quarter point.","And December? A Fed hike is nearly priced in: 87%, a quarter point"),
 ('outro',"Follow WallBlock News. Information, not financial advice.","Follow WallBlock News · Information, not financial advice"),
]}
MIN={'hook1':0,'hook2':0,'intro':3.2,'crypto':5.0,'ws':6.4,'asia':4.2,'oil':4.4,'fed':5.8,'outro':4.6}
SPEED={'es':100,'en':100}   # Pico <speed level>; 100 = natural
