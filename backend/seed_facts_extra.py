"""Extra curated Italian facts — extends the base seed to reach ~108 facts.

Each fact includes optional `sources`: list of {title, url} for verified deep dives.
"""
from typing import List, Dict
from seed_facts import _image_for


def _fact(category: str, title: str, short: str, deep: str, sources=None) -> Dict:
    return {
        "category": category,
        "title": title,
        "short_fact": short,
        "deep_dive": deep,
        "image_url": _image_for(category),
        "source": "seed",
        "sources": sources or [],
    }


EXTRA_FACTS: List[Dict] = [
    # ========== SCIENZA (+4) ==========
    _fact("Scienza", "Il vetro è in realtà un liquido ultraviscoso",
          "Il vetro non è un solido: è un liquido amorfo che scorre lentissimamente. Le vetrate medievali sono più spesse in basso.",
          "Tecnicamente il vetro è un 'solido amorfo': ha la rigidità di un solido ma la struttura molecolare disordinata di un liquido. A temperatura ambiente scorre a velocità infinitesimali — occorrerebbero miliardi di anni per vedere effetti macroscopici. Il 'flusso' delle vetrate delle cattedrali medievali è in realtà dovuto alla tecnica di produzione dell'epoca (vetro soffiato non uniforme), non al tempo. Ma vetri ultra-raffreddati mostrano effettivamente proprietà reologiche intermedie.",
          [{"title": "American Scientific Glass Association", "url": "https://www.asgsonline.org/"}]),
    _fact("Scienza", "I gatti hanno 32 muscoli per ogni orecchio",
          "Gli orecchi dei gatti possono ruotare di 180° grazie a 32 muscoli dedicati. Gli umani ne hanno 6, quasi tutti atrofizzati.",
          "Questa capacità acustica superiore permette ai gatti di localizzare prede con precisione millimetrica anche al buio. Possono sentire frequenze fino a 64.000 Hz (gli umani arrivano a 20.000). I 'movimenti d'orecchio' sono anche un linguaggio emotivo: appiattite = paura/aggressività, dritte = attenzione, rilassate = tranquillità. Gli etologi le chiamano 'antenne satellitari viventi'.",
          [{"title": "Cornell Feline Health Center", "url": "https://www.vet.cornell.edu/"}]),
    _fact("Scienza", "Esiste un materiale più nero del nero",
          "Il Vantablack assorbe il 99,965% della luce visibile: guardarlo è come guardare un buco nel mondo.",
          "Sviluppato nel 2014 da Surrey NanoSystems, è composto da nanotubi di carbonio verticali che 'intrappolano' i fotoni. Un oggetto 3D ricoperto di Vantablack appare come una silhouette piatta. L'artista Anish Kapoor ne ha acquisito l'esclusiva per usi artistici, scatenando polemiche. Nel 2019 il MIT ha creato un nero ancora più scuro (99,995%) da scarti di fluoro di calcio. Applicazioni: telescopi spaziali, ottica di precisione, esperimenti quantistici."),
    _fact("Scienza", "I fulmini producono antimateria",
          "Durante i temporali, la Terra emette lampi di raggi gamma che contengono positroni: la controparte di antimateria degli elettroni.",
          "Scoperto dal Fermi Space Telescope nel 2009, il fenomeno è chiamato TGF (Terrestrial Gamma-ray Flash). Ogni giorno la Terra produce migliaia di questi lampi, ciascuno contenente abbastanza antimateria da contraddire il senso comune. Gli elettroni accelerati dai campi elettrici del temporale creano coppie elettrone-positrone che si annichilano istantaneamente emettendo raggi gamma. Gli aerei che attraversano temporali sono occasionalmente esposti a queste dosi di radiazione."),

    # ========== STORIA (+5) ==========
    _fact("Storia", "I romani usavano l'urina come dentifricio",
          "L'urina umana (ricca di ammoniaca) era venduta come sbiancante per i denti. La più pregiata arrivava dal Portogallo.",
          "L'imperatore Vespasiano tassò il commercio dell'urina (raccolta nei 'vespasiani' pubblici, oggi eufemismo per orinatoi). Quando il figlio Tito si lamentò dell'origine, Vespasiano gli mise sotto il naso una moneta dicendo: 'Pecunia non olet' (il denaro non puzza), frase divenuta proverbiale. L'urina veniva usata anche dai tintori per fissare i colori e dai conciatori per ammorbidire la pelle. Contiene ammoniaca che effettivamente sbianca lo smalto, ma ne corrode la struttura."),
    _fact("Storia", "Napoleone non era basso",
          "Era alto 1,69m, media francese dell'epoca. Il mito nacque da un errore di conversione tra pollici francesi e inglesi.",
          "I pollici francesi erano più lunghi di quelli inglesi. Napoleone, misurato in 'pieds' francesi (5 pieds 2 pouces = 168cm), fu convertito erroneamente nei giornali inglesi come 5'2\" (157cm). La propaganda britannica di Gillray e Cruikshank sfruttò il malinteso creando il 'piccolo caporale' caricaturale. Il suo soprannome 'le petit caporal' era affettuoso, non descrittivo. Oggi la 'Sindrome di Napoleone' (piccoli aggressivi) è un mito psicologico scientificamente infondato.",
          [{"title": "Smithsonian Magazine", "url": "https://www.smithsonianmag.com/"}]),
    _fact("Storia", "Nel 1814 Londra fu sommersa da birra",
          "Scoppiò una cisterna di birra al Meux's Brewery: 1,5 milioni di litri invasero le strade, uccidendo 8 persone.",
          "Il 'London Beer Flood' del 17 ottobre 1814 distrusse due case nel quartiere povero di St. Giles. L'onda di birra bionda alta oltre 4 metri sommerse donne che stavano facendo il funerale di un bambino. Il proprietario fu assolto: 'atto di Dio'. Un aneddoto (probabilmente falso) vuole che alcuni sopravvissuti morirono poi di alcolismo cercando di bere la birra dalle cantine allagate. Oggi una targa a Tottenham Court Road ricorda il disastro."),
    _fact("Storia", "Il miele dei Faraoni era ancora commestibile",
          "Archeologi hanno trovato vasi di miele sigillati nella tomba di Tutankhamon ancora perfettamente commestibili dopo 3300 anni.",
          "Il miele è stato rinvenuto in perfette condizioni in molte tombe egizie. Gli Egizi lo consideravano sacro: era offerta agli dei, medicina (usato per curare ferite con ottimi risultati, le sue proprietà antibatteriche sono oggi scientificamente confermate), e simbolo di immortalità. Veniva depositato nelle tombe come alimento per l'aldilà. L'Organizzazione Mondiale della Sanità riconosce ufficialmente il miele come antimicrobico per ferite superficiali.",
          [{"title": "National Honey Board", "url": "https://honey.com/"}]),
    _fact("Storia", "Einstein rifiutò la presidenza di Israele",
          "Nel 1952 David Ben-Gurion offrì a Einstein la presidenza dello Stato d'Israele. Lui rifiutò per mancanza di esperienza politica.",
          "Einstein, ebreo tedesco e sionista convinto ma pacifista critico, rispose: 'Sono profondamente commosso ma non adatto. Ho poca esperienza nel rapportarmi con le persone e svolgere funzioni ufficiali'. Aveva 73 anni e si sentiva troppo vecchio. Weizmann, primo presidente, era stato suo amico. Einstein donò tutti i suoi diritti d'autore e lettere all'Hebrew University di Gerusalemme, che oggi ne custodisce oltre 80.000 documenti."),

    # ========== TECNOLOGIA (+4) ==========
    _fact("Tecnologia", "Il primo computer bug era letteralmente un insetto",
          "Nel 1947 Grace Hopper trovò una falena intrappolata nel Harvard Mark II. La incollò nel logbook: 'First actual case of bug being found'.",
          "Il termine 'bug' per difetti esisteva già (Edison lo usava nel 1878), ma l'incidente del 9 settembre 1947 lo rese leggendario nell'informatica. Il logbook è oggi esposto al Smithsonian. Grace Hopper inventò anche il primo compilatore e il concetto di linguaggio ad alto livello (COBOL). Ammiraglia della US Navy, è considerata madre dell'informatica moderna. Il termine 'debugging' (togliere insetti) è ancora in uso oggi.",
          [{"title": "Smithsonian NMAH", "url": "https://americanhistory.si.edu/collections/nmah_334663"}]),
    _fact("Tecnologia", "Esiste un bottone per far impazzire i cellulari",
          "I numeri con troppi caratteri speciali possono crashare qualsiasi smartphone. Nel 2018 un messaggio in telugu bloccava gli iPhone.",
          "Le 'crash bombs' sfruttano vulnerabilità di rendering dei caratteri Unicode. Il 'Telugu Bug' di iOS 11 (2018) faceva crashare qualsiasi app che mostrasse il carattere 'జ్ఞా'. Nel 2020 su Android il messaggio 'Ꙭ' (occhio di Cirillo) poteva bloccare Instagram. Gli sviluppatori usano 'fuzzing' — inondare app con input casuali — per trovare questi bug prima dei malintenzionati. Anche il WiFi ha vulnerabilità: alcuni SSID come '%n' potevano disattivare il WiFi di iPhone."),
    _fact("Tecnologia", "L'email è più vecchia del web di 20 anni",
          "La prima email fu inviata nel 1971 da Ray Tomlinson. Il World Wide Web nacque nel 1991 grazie a Tim Berners-Lee.",
          "Tomlinson scelse la '@' dalla tastiera perché 'non compariva in nessun nome'. Il primo messaggio? 'QWERTYUIOP' (non lo ricordava nemmeno lui). Oggi si scambiano 333 miliardi di email al giorno. Berners-Lee creò invece il WWW al CERN per condividere documenti tra ricercatori; il primo sito (info.cern.ch) è ancora online. Il web è solo uno dei servizi di Internet (come email, FTP, SSH): spesso i due termini vengono confusi."),
    _fact("Tecnologia", "Bluetooth prende il nome da un re vichingo",
          "Harald Blåtand 'Dente Blu' unì Danimarca e Norvegia nel 958. Il logo Bluetooth è il monogramma delle sue rune ᚼ e ᛒ.",
          "Gli ingegneri Intel, Ericsson e Nokia cercavano un nome temporaneo per la loro tecnologia di unificazione wireless nel 1997. Harald unificò popoli; loro volevano unificare dispositivi. Il logo combina le rune H (ᚼ, Hagall) e B (ᛒ, Bjarkan). Il 'Dente Blu' del re? Probabilmente un dente morto (scuro), non letteralmente blu. Bluetooth Low Energy (2010) ha reso possibile l'IoT moderno: oggi oltre 4 miliardi di dispositivi all'anno."),

    # ========== NATURA (+5) ==========
    _fact("Natura", "Esiste una medusa immortale",
          "La Turritopsis dohrnii può tornare allo stadio larvale quando è in pericolo. Teoricamente, può vivere per sempre.",
          "Scoperta nel 1988, questa medusa mediterranea grande 4 mm inverte il suo ciclo biologico: da medusa adulta torna a polipo giovane, un processo chiamato transdifferenziazione. È l'unico organismo conosciuto capace di 'ringiovanire' biologicamente. Non è davvero immortale (può morire per predazione o malattia), ma non invecchia. Oggi è studiata intensivamente per comprendere l'invecchiamento cellulare. Lo scienziato giapponese Shin Kubota ne alleva una colonia da decenni."),
    _fact("Natura", "Gli alberi più vecchi del mondo sono cloni",
          "Pando, un colonia di pioppi tremuli in Utah, condivide un unico sistema radicale. Ha 80.000 anni e pesa 6.000 tonnellate.",
          "Pando ('mi diffondo' in latino) è tecnicamente UN UNICO ORGANISMO: 47.000 tronchi geneticamente identici connessi da radici comuni. Copre 43 ettari ed è considerato l'essere vivente più pesante della Terra. Purtroppo sta morendo: gli erbivori mangiano i giovani germogli prima che crescano. Gli scienziati stanno recintando aree per salvarlo. Altre piante formano organismi simili: il fungo Armillaria in Oregon copre 9 km² ed è considerato il più grande organismo terrestre.",
          [{"title": "Friends of Pando", "url": "https://www.friendsofpando.org/"}]),
    _fact("Natura", "I fulmini sono 5 volte più caldi del Sole",
          "Un fulmine può raggiungere 30.000°C: 5 volte la temperatura della superficie solare (~5.500°C).",
          "L'estremo riscaldamento causa l'espansione supersonica dell'aria, generando il tuono (onda d'urto). Ogni secondo colpiscono la Terra circa 100 fulmini. Il record di fulmine più lungo mai registrato: 768 km, in Texas e Louisiana nel 2020 (WMO). La 'fulguratite' è un minerale vetrificato formatosi quando un fulmine colpisce la sabbia: ricercato dai collezionisti. La probabilità di essere colpiti è 1 su 700.000 all'anno."),
    _fact("Natura", "Le piante urlano in ultrasuoni",
          "Sotto stress (siccità, tagli), le piante emettono suoni ad alta frequenza: un geniale pianto vegetale, impercettibile all'orecchio umano.",
          "Uno studio del Tel Aviv University (Cell, 2023) ha registrato pomodori e tabacco che emettono 'click' ad alta frequenza (20-100 kHz) quando sotto stress idrico o fisico. Una pianta non irrigata emette 30-40 click/ora. Le piante sane sono quasi silenziose. Insetti, topi e pipistrelli possono probabilmente percepirli. Non sono vocalizzazioni coscienti ma cavitazione nei vasi xilematici. Aprono la via a agricoltura guidata dall'AI che 'ascolta' le colture.",
          [{"title": "Cell Press Study 2023", "url": "https://www.cell.com/cell/fulltext/S0092-8674(23)00262-3"}]),
    _fact("Natura", "Il 70% dell'ossigeno viene dagli oceani",
          "Non sono gli alberi a produrre la maggior parte dell'ossigeno terrestre, ma il fitoplancton marino. Il più prolifico: la Prochlorococcus.",
          "La Prochlorococcus è il più piccolo fotosintetizzatore del pianeta (0,5-0,8 μm) ma anche il più abbondante: ce ne sono 3 ottilioni (3×10^27) negli oceani. Produce da sola il 5% dell'ossigeno terrestre. Il fitoplancton complessivamente copre il 50-80% dell'ossigeno. Questo dato ribalta il mito 'salva l'Amazzonia per respirare': in realtà l'Amazzonia consuma quasi tutto l'ossigeno che produce tramite respirazione ecosistemica. Gli oceani sono i veri 'polmoni blu'."),

    # ========== SPAZIO (+5) ==========
    _fact("Spazio", "Su Saturno potrebbero piovere diamanti come su Giove",
          "Le pressioni estreme dei giganti gassosi trasformano il metano atmosferico in cristalli di diamante che precipitano verso il nucleo.",
          "Secondo simulazioni Caltech/Wisconsin (2013), su Saturno potrebbero piovere fino a 1000 tonnellate di diamanti all'anno. Il processo: fulmini scompongono il metano in carbonio, che compattandosi a pressioni di milioni di atmosfere si cristallizza. Un fenomeno simile avviene su Giove, Urano e Nettuno. Se colonizzeremo mai i giganti gassosi (ipoteticamente via aerostati), potremmo 'raccogliere' diamanti cadenti. Nel frattempo la Terra dispone di 'fontane' di carbonio sotto i vulcani che fanno risalire diamanti dal mantello."),
    _fact("Spazio", "Una giornata su Mercurio dura 2 anni mercuriani",
          "Mercurio ruota così lentamente rispetto alla sua rivoluzione che il Sole compie due orbite solari prima che il pianeta abbia un giorno completo.",
          "Un giorno solare mercuriano (176 giorni terrestri) è pari a 2 anni mercuriani (88 giorni × 2). L'effetto è dovuto alla risonanza orbitale 3:2 con il Sole: Mercurio ruota 3 volte su se stesso ogni 2 orbite. Stando sulla superficie, si vedrebbe il Sole sorgere, fermarsi a metà cielo, indietreggiare, ripartire, poi tramontare. Le temperature oscillano da 430°C (giorno) a -180°C (notte). La Terra potrebbe rientrare nell'orbita di Mercurio."),
    _fact("Spazio", "Siamo fatti di polvere di stelle",
          "Ogni atomo pesante del tuo corpo (ferro, calcio, ossigeno) è stato forgiato nel cuore di una stella esplosa miliardi di anni fa.",
          "Il Big Bang creò solo idrogeno, elio e tracce di litio. Tutti gli altri elementi (carbonio del DNA, calcio delle ossa, ferro del sangue, iodio della tiroide) si formarono per fusione nucleare nelle stelle. Elementi più pesanti del ferro nascono solo in eventi cataclismici: supernove ed collisioni di stelle di neutroni. L'oro del tuo anello venne creato in una collisione stellare ~5 miliardi di anni fa. Carl Sagan disse: 'Siamo un modo per il cosmo di conoscere se stesso'."),
    _fact("Spazio", "Esistono pianeti vagabondi senza sole",
          "Tra le stelle vagano miliardi di pianeti 'orfani' espulsi dai loro sistemi. Alcuni potrebbero ospitare vita con vulcani come fonte di calore.",
          "Stimati 50-100 miliardi nella sola Via Lattea, i 'rogue planets' furono scoperti nel 2011. Senza stella, sono freddi e oscuri, ma alcuni (grandi come Giove) hanno core caldi radioattivi. Le lune sotto ghiaccio (come Europa di Giove) potrebbero avere oceani liquidi riscaldati da maree gravitazionali. Teoricamente, un pianeta vagabondo con luna in orbita potrebbe ospitare vita in oceani sotterranei. Il telescopio James Webb sta cercando 'rogue worlds' nel 2025."),
    _fact("Spazio", "La voce di Neil Armstrong non disse davvero 'un uomo'",
          "La frase 'un piccolo passo per l'uomo' manca dell'articolo 'a'. Armstrong sostenne di averlo detto, ma non è nelle registrazioni.",
          "La frase intesa era: 'That's one small step for a man, one giant leap for mankind' (un uomo vs umanità — senza 'a' è ridondante). Armstrong giurò di averlo pronunciato, ma l'analisi audio del 1969 non lo rivela. Nel 2006 un ingegnere australiano sostenne di aver trovato l'articolo in analisi acustiche avanzate: controverso. Armstrong morì nel 2012 senza risoluzione. La frase, comunque, rimane uno dei momenti più memorabili della storia umana, ascoltata in diretta da 600 milioni di persone."),

    # ========== CUCINA (+4) ==========
    _fact("Cucina", "Le banane sono radioattive",
          "Contengono potassio-40, un isotopo radioattivo. Mangiarne 100 al giorno equivale alla dose di radiazione di una radiografia dentale.",
          "L'unità informale 'BED' (Banana Equivalent Dose) è usata dai fisici per rendere comprensibili le dosi radioattive: 1 banana ≈ 0,1 μSv. Una radiografia toracica = 100 banane. Un volo aereo trans-Pacifico = 400 banane. L'eruzione di Chernobyl: miliardi di banane. Ironicamente, Brasile e gli oceani sono più radioattivi per unità di massa. Il corpo umano stesso emette 8.000 decadimenti al secondo dal potassio-40 naturale interno."),
    _fact("Cucina", "Il caffè era bandito a La Mecca",
          "Nel 1511 il governatore de La Mecca bandì il caffè perché stimolava 'pensieri sovversivi'. Fu imprigionato dal sultano.",
          "Il caffè, scoperto in Etiopia nel IX secolo secondo la leggenda del pastore Kaldi, arrivò nel mondo arabo dove le 'qahveh khaneh' (caffetterie) divennero centri di discussione politica. Il governatore Khair Beg temeva le cospirazioni tra i bevitori di caffè. Nel 1675 anche Carlo II d'Inghilterra tentò di vietare i 'coffee houses' come covi di sedizione. I bevitori protestarono così violentemente che revocò la legge in 2 giorni. Oggi si bevono 2,25 miliardi di tazzine di caffè al giorno nel mondo."),
    _fact("Cucina", "I ketchup era un farmaco",
          "Nel 1834 il Dr. John Cook Bennet vendeva pillole di 'ketchup di pomodoro' per curare diarrea e indigestione.",
          "Il ketchup originale (dal cinese 'kôe-chiap', salsa di pesce fermentato) era un condimento di acciughe. Bennett, medico dell'Ohio, sostenne che il pomodoro curasse problemi digestivi: vendeva pillole che si rivelarono un pasticcio di zucchero con laureli lassativi. Il successo commerciale di Heinz (1876) popolarizzò la versione dolce moderna. Oggi il ketchup è una delle pochissime salse usate universalmente: ogni americano ne consuma 3 bottiglie all'anno."),
    _fact("Cucina", "Il croissant è austriaco, non francese",
          "Il 'kipferl' austriaco ispirò il croissant per celebrare la vittoria di Vienna sui turchi nel 1683 (la sua forma è una falce turca).",
          "Leopoldo I d'Austria, dopo aver respinto l'assedio ottomano del 1683, fece commissionare ai panettieri dolci a forma di mezzaluna (simbolo ottomano) da 'mangiare' simbolicamente. Maria Antonietta (austriaca) lo portò in Francia nel 1770 sposando Luigi XVI. Solo a fine '800 la versione francese con pasta sfoglia soppiantò l'originale a pasta brioche. Oggi la Francia consuma 1,5 milioni di croissant al giorno, ma legalmente il 'croissant au beurre' è protetto solo in Francia."),

    # ========== SPORT (+3) ==========
    _fact("Sport", "Le Olimpiadi antiche erano nude",
          "Gli atleti greci gareggiavano completamente nudi per onorare gli dei. La parola 'ginnastica' deriva da 'gymnos' (nudo).",
          "Dal 720 a.C. la nudità divenne regola dopo che Orsippo di Megara, perdendo involontariamente il perizoma, vinse la corsa. Le donne sposate non potevano assistere (pena morte), le vergini sì. Pausania raccontò di una madre che si travestì per vedere il figlio vincere: da allora anche gli allenatori dovettero essere nudi. Le Olimpiadi durarono 1169 anni (776 a.C. - 393 d.C.) prima che l'imperatore Teodosio le abolisse come 'pagane'. Rinacquero nel 1896 ad Atene con Pierre de Coubertin."),
    _fact("Sport", "Il primo pallone da basket era una pesca",
          "James Naismith inventò il basket nel 1891 usando cesti di pesca come canestri. Ogni volta bisognava recuperare la palla con una scala.",
          "Naismith, insegnante di ginnastica canadese, cercava uno sport indoor per l'inverno del Massachusetts. Fissò due cesti di pesca a 3,05m (ancora l'altezza ufficiale). Le regole originali erano 13; la prima partita (21 dicembre 1891) vide 9 giocatori per squadra, finì 1-0. Nel 1894 arrivò il primo pallone specifico. Nel 1906 il retro dei canestri venne sostituito da tabelloni e le reti aperte eliminarono il problema del recupero palla. Oggi il basket è il 3° sport più seguito al mondo."),
    _fact("Sport", "Un re britannico annullò il calcio",
          "Nel 1314 Edoardo II proibì il calcio a Londra per 'preservare la pace del re'. La pena: prigione.",
          "Il calcio medievale era un caos violento: squadre di centinaia di persone si contendevano la palla attraversando interi villaggi, con numerosi morti. Diversi re inglesi (Edoardo II, III, Riccardo II, Enrico IV, V) emisero editti contro il 'foteball'. Giacomo I lo vietò in Scozia definendolo 'adatto solo a rompere gambe'. Nel 1540 Enrico VIII contribuì però alla sua sopravvivenza facendo costruire il primo campo di calcio documentato. Il rugby nacque nel 1823 quando William Webb Ellis, in una partita di football, prese la palla in mano."),

    # ========== ARTE (+4) ==========
    _fact("Arte", "La Gioconda fu quasi dimenticata fino al furto del 1911",
          "Prima del furto, la Monna Lisa era un dipinto minore del Louvre. Il clamore mediatico la rese l'opera d'arte più famosa al mondo.",
          "Il 21 agosto 1911 un operaio italiano, Vincenzo Peruggia, rubò il quadro nascondendolo sotto il camice. Voleva restituirlo all'Italia (nazionalismo). Per 2 anni la tela mancante fu celebrità assoluta; Kafka, Rilke e Picasso vennero interrogati. Nel 1913 Peruggia tentò di venderla agli Uffizi. Recuperata, la Monna Lisa tornò a Parigi da icona globale. Oggi è coperta da vetro antiproiettile e riceve 20.000 visitatori al giorno. Leonardo la portò con sé in Francia e vi lavorò fino alla morte (1519), senza mai consegnarla al committente."),
    _fact("Arte", "Van Gogh vendette UN solo quadro in vita",
          "In 37 anni di vita vendette ufficialmente solo 'La vigna rossa' per 400 franchi (nel 1890). Oggi i suoi dipinti superano i 100 milioni.",
          "Van Gogh dipinse oltre 2.100 opere in 10 anni di attività. Viveva grazie al sostegno economico del fratello Theo, mercante d'arte, a cui scrisse oltre 900 lettere. Dopo il suicidio nel 1890, la vedova di Theo (Jo Bonger) dedicò la vita a promuoverne l'opera, organizzando mostre e pubblicando le lettere: senza di lei, Van Gogh sarebbe rimasto ignoto. Oggi il suo 'Ritratto del Dottor Gachet' è uno dei quadri più costosi al mondo (152 milioni di dollari, 1990).",
          [{"title": "Van Gogh Museum", "url": "https://www.vangoghmuseum.nl/"}]),
    _fact("Arte", "Michelangelo scolpì il David da un blocco scartato",
          "Il blocco di marmo di Carrara era stato abbandonato per 40 anni da due scultori precedenti. Michelangelo lo chiamò 'il gigante'.",
          "Il marmo, scavato nel 1464, era considerato 'sbagliato' dal Duomo di Firenze. Nel 1501 Michelangelo, 26enne, lo ricevette come sfida. Lavorò 3 anni in segreto dietro una recinzione. Il David (5,17m, 6 tonnellate) fu un capolavoro prospettico: la testa è volutamente sovradimensionata perché pensato per essere visto dal basso. Originariamente doveva stare sul Duomo; i fiorentini lo vollero in Piazza della Signoria come simbolo di libertà contro Golia/Firenze tirannica. Vi rimase 369 anni prima dell'attuale copia."),
    _fact("Arte", "Il 'Grido' di Munch fu graffiato dall'autore",
          "Munch graffiò 'Può essere stato dipinto solo da un pazzo!' nell'angolo del quadro. Era reazione ai critici che lo giudicavano mentalmente instabile.",
          "L'iscrizione nascosta è stata confermata nel 2021 tramite analisi infrarosse del Museo Nazionale di Oslo. Munch soffriva di ansia, depressione e allucinazioni. 'Il Grido' (1893) rappresenta un attacco di panico vissuto al tramonto con 'il cielo rosso come sangue'. Il 'Grido' esiste in 4 versioni, di cui una in pastello venduta a 119,9 milioni di dollari nel 2012 (record per un'opera d'arte all'asta all'epoca). Il cielo rosso potrebbe essere ispirato all'eruzione del Krakatoa del 1883."),

    # ========== PSICOLOGIA (+4) ==========
    _fact("Psicologia", "L'effetto Dunning-Kruger: gli incompetenti si credono esperti",
          "Le persone meno competenti in un campo tendono a sopravvalutarsi. I veri esperti, al contrario, tendono a sottovalutare le proprie capacità.",
          "Studio del 1999 di David Dunning e Justin Kruger alla Cornell, premio Ig Nobel 2000. La causa: per riconoscere la propria incompetenza servono le stesse capacità che mancano. La 'valle dell'umiltà' (dopo aver imparato abbastanza da capire quanto non sai) è un indicatore di vera competenza. Applicazioni: dibattiti politici, social media, lavoro. Bertrand Russell lo aveva anticipato: 'Il problema del mondo è che gli stupidi sono sempre sicuri di sé, e gli intelligenti pieni di dubbi'."),
    _fact("Psicologia", "Sorridere ti rende più felice (anche se è finto)",
          "Il feedback facciale: mantenere un sorriso attiva gli stessi neurotrasmettitori della gioia reale. Anche tenere una matita in bocca funziona.",
          "Teoria del facial feedback (Paul Ekman, 1992): i muscoli del viso inviano al cervello segnali chimici che influenzano l'emozione. Uno studio del 1988 fece tenere a partecipanti una matita in bocca (forzando un sorriso involontario) mentre guardavano cartoni: li trovarono più divertenti. Repliche più recenti hanno ridimensionato l'effetto ma confermato una debole correlazione. Conseguenze: il Botox (che paralizza la fronte) riduce la capacità di provare tristezza/rabbia. Smile therapy è usata clinicamente contro la depressione."),
    _fact("Psicologia", "Gli odori sono i più potenti innesco di memoria",
          "L'olfatto è l'unico senso direttamente connesso al sistema limbico. Un profumo può trasportarti istantaneamente nell'infanzia.",
          "Gli altri sensi (vista, udito, tatto, gusto) passano prima dal talamo, che filtra. L'olfatto va direttamente ad amigdala (emozioni) e ippocampo (memoria). Proust lo chiamò 'memoria involontaria': il famoso momento del madeleine. Le 'memorie proustiane' sono 2-4 volte più emotive e dettagliate delle memorie visive. L'anosmia (perdita dell'olfatto, comune col COVID) è associata a depressione e sensazione di 'perdere parte di sé'. Le aziende (hotel, negozi) usano 'scent branding' per creare associazioni memorabili."),
    _fact("Psicologia", "Vedi meglio i pericoli in visione periferica",
          "Il cervello processa il movimento nella periferia visiva prima di 'riconoscerlo'. Per questo 'senti' qualcuno alle spalle prima di vederlo.",
          "La retina periferica è ricca di cellule a bastoncello (rilevano movimento e basse luci), mentre il centro (fovea) ha coni (colore, dettagli). Il cervello archeologicamente evoluto rileva pericoli (predatori) anche prima che la coscienza li elabori. Ecco perché ci voltiamo 'senza motivo' — avevamo già visto. Nella guida: i rabdomanti stradali usano questa capacità. L'orologio peripherale è anche strategico: i segnali stradali ai lati sono spesso percepiti prima di essere 'letti' consciamente."),

    # ========== CINEMA (+3) ==========
    _fact("Cinema", "Il primo film porno è del 1896",
          "'Le Coucher de la Mariée' durava 7 minuti e mostrava una donna che si spogliava. Fu proiettato a Parigi due anni dopo i Lumière.",
          "Il cinema aveva appena 2 anni. Albert Kirchner (alias Léar) diresse il film a Parigi con l'attrice Louise Willy. Nonostante la nudità fosse brevissima, scandalizzò la società ottocentesca. Il primo film erotico 'parlato' fu 'A Free Ride' (1915, USA). Alla fine dell'800 le 'kinetoscope arcades' offrivano già cortometraggi piccanti. Hollywood introdusse il 'Codice Hays' (1934-1968) bandendo nudi e temi sessuali, creando un mercato parallelo fiorente."),
    _fact("Cinema", "Il suono di R2-D2 è George Lucas che gioca con un bambino",
          "Ben Burtt creò il linguaggio di R2 mescolando la sua voce che imitava un bambino, sintetizzatori analogici e richiami di delfini.",
          "Burtt è il 'papà' del sound design di Star Wars: il respiro di Darth Vader (una maschera subacquea), lo spadalaser (un tubo TV + un motore di proiettore), il Wookie (orso, tricheco, morsa, cammello). L'effetto ACE123 (cane abbaia) è in ogni film dagli anni '80. Ha vinto 4 Oscar. R2 parlava un linguaggio coerente ('astromech binary') che Anthony Daniels (C-3PO) imparò a 'capire' per recitare meglio. Oggi è insegnato al MIT come caso di 'sonic branding' perfetto."),
    _fact("Cinema", "Sylvester Stallone vendette il suo cane per poter scrivere Rocky",
          "Senza soldi e rifiutato da tutti gli studios, Stallone vendette il suo cane per 25 dollari. Dopo il successo di Rocky, lo ricomprò per 15.000.",
          "Nel 1975 Stallone era al verde. Ispirato dalla vittoria di Chuck Wepner contro Ali, scrisse Rocky in 3 giorni e mezzo. Gli studios offrirono 325.000 dollari per il copione ma solo se cedeva il ruolo a Redford o Burt Reynolds. Rifiutò e dovette vendere il cane Butkus. Quando United Artists accettò (125.000 dollari + recitare lui), Stallone tornò dal nuovo proprietario e pagò 15.000 dollari per riavere il cane. Butkus recitò poi nel film stesso, inquadrato con Stallone che si allena."),

    # ========== MUSICA (+3) ==========
    _fact("Musica", "I Beatles non sapevano leggere la musica",
          "Nessuno dei Fab Four sapeva leggere la notazione musicale. Imparavano e componevano a orecchio, incluse sinfonie con orchestra.",
          "John Lennon disse: 'Nessuno di noi sa leggere. Non sapremmo neanche scrivere una canzone in scala di C'. Paul McCartney ammise di averlo 'provato ma essere troppo pigro'. Lavoravano con il produttore George Martin (musicista classico) che trascriveva le loro idee per orchestrali come 'Yesterday' o 'Eleanor Rigby'. Musica e notazione sono abilità separate: Stevie Wonder, Michael Jackson, Jimi Hendrix e Prince erano analfabeti musicali. Sinistra come Jimi Hendrix imparò la chitarra con strumenti per destri suonati al contrario."),
    _fact("Musica", "La 'Canzone più ascoltata al mondo' è 'Happy Birthday'",
          "La registrazione Spotify mostra che 'Happy Birthday' è cantata/ascoltata più di ogni altra canzone al mondo, ogni giorno.",
          "Composta dalle sorelle Hill nel 1893 come 'Good Morning to All', divenne 'Happy Birthday to You' nel 1912. Warner/Chappell ne deteneva il copyright e incassava 2 milioni di dollari all'anno licenziandola a film e TV fino al 2016, quando un tribunale la dichiarò di dominio pubblico. Tradotta in ogni lingua, è cantata ~3 miliardi di volte all'anno nel mondo. Alternative in altri paesi: 'Las Mañanitas' (Messico), 'Joyeux Anniversaire' (Francia), 'Tanti Auguri a Te' (Italia)."),
    _fact("Musica", "Il disco più venduto della storia NON è dei Beatles",
          "È 'Thriller' di Michael Jackson (1982): 70 milioni di copie ufficiali, stimate fino a 100 milioni. Resta invincibile da 40+ anni.",
          "Thriller cambiò l'industria musicale. Quincy Jones e Jackson lavorarono 8 mesi con budget record (750.000 dollari). Il video di 14 minuti diretto da John Landis fu il primo 'cinematografico', trasformando MTV. Il tape di video musicali di Thriller vendette 9 milioni di copie, record. Jackson divenne il primo musicista ad essere lanciato come entertainer globale. Nel 2009, dopo la sua morte, le vendite di Thriller balzarono a 130 milioni di streams. Le stime più alte arrivano a 105 milioni di copie fisiche totali."),

    # ========== GEOGRAFIA (+3) ==========
    _fact("Geografia", "In Africa c'è un lago rosa che uccide quasi tutti gli animali",
          "Il Lake Natron in Tanzania è alcalino (pH 10,5) e a 60°C: calcifica e 'pietrifica' gli uccelli che tentano di atterrarci.",
          "Colorato di rosa da microalghe alofile, il lago è uno dei luoghi più inospitali della Terra. Solo i fenicheri rosa (che lo chiamano casa) e pochi pesci si sono adattati. Gli animali morti vengono preservati come 'mummie minerali' per l'alta concentrazione di carbonato di sodio. Il fotografo Nick Brandt vi ha fatto un libro leggendario. Il colore deriva dai carotenoidi delle cianobatteri Spirulina. Il lago è sacro per la tribù masai e fonte del loro latte per cosmetica e sopravvivenza."),
    _fact("Geografia", "L'Italia ha più UNESCO di qualsiasi altro paese al mondo",
          "60 siti UNESCO (dato 2024). Seconda è la Cina (59), terza la Germania (54). Francia ha 52.",
          "Dall'ultima Cena di Leonardo al Centro Storico di Firenze, dai Sassi di Matera a Pompei, dagli Scavi di Siracusa alle Dolomiti. L'Italia aggiunge siti quasi ogni anno: 2024 ha visto l'inclusione del 'Paesaggio delle Langhe-Roero-Monferrato' già patrimonio dal 2014, della Via Appia 'Regina Viarum' in 2024. Il più famoso visitato è il Colosseo (7,5 milioni di turisti/anno). L'Italia ha anche 12 siti UNESCO nel Patrimonio Immateriale (opera lirica, pizza napoletana, Commedia dell'Arte, ecc.).",
          [{"title": "UNESCO World Heritage Centre", "url": "https://whc.unesco.org/en/statesparties/it"}]),
    _fact("Geografia", "Esistono più anni lunari che solari in Etiopia",
          "L'Etiopia usa un calendario proprio di 13 mesi. Oggi per loro è 7-8 anni indietro rispetto al nostro.",
          "Il calendario etiope deriva dal calendario copto egizio. Ha 12 mesi di 30 giorni + un 13° mese di 5 o 6 giorni (Pagume). L'anno inizia l'11 settembre (12 in anni bisestili). Il Natale cade il 7 gennaio. Il capodanno etiope 2017 è iniziato l'11 settembre 2024 del nostro calendario. Altri paesi con calendari alternativi: Nepal (Vikram Samvat), Iran (Solar Hijri), Thailandia (Buddista). Lo slogan turistico etiope era '13 mesi di sole'."),

    # ========== MEDICINA (+3) ==========
    _fact("Medicina", "Il tuo stomaco si rigenera ogni 3-4 giorni",
          "Le cellule dello stomaco vengono distrutte dall'acido che producono. Devono essere sostituite ogni 3-4 giorni per non autodivorarti.",
          "Lo stomaco produce HCl a pH 1-2, abbastanza aggressivo da dissolvere metalli. Una barriera di muco (rinnovata ogni 3-4 giorni) protegge la mucosa. Quando fallisce: ulcere. Fu rivoluzionato nel 1982 quando Barry Marshall e Robin Warren scoprirono che le ulcere sono causate dal batterio Helicobacter pylori (e non dallo stress). Marshall per convincere i critici bevve una coltura del batterio sviluppando ulcera intenzionalmente. Vinsero il Nobel 2005. Ogni cellula umana vive 7-10 anni in media: siamo un 'flusso' cellulare costante."),
    _fact("Medicina", "I trapianti d'organo possono cambiare la personalità",
          "'Cellular memory': alcuni pazienti trapiantati riportano cambiamenti di gusti, preferenze, persino ricordi del donatore.",
          "Un fenomeno documentato dai medici Gary Schwartz e Linda Russek (1998). Una paziente di 8 anni trapiantata di cuore iniziò ad avere incubi di un omicidio: la polizia risolse grazie ai suoi ricordi il caso del donatore assassinato. La scienza è scettica ma i casi sono molti. Ipotesi: i neuroni del sistema nervoso enterico (intestinale) e del cuore ('cervello cardiaco', 40.000 neuroni) possono conservare memoria biochimica. Resta zona grigia tra neurofisiologia e psicologia post-trauma del trapianto."),
    _fact("Medicina", "La penicillina fu scoperta per un errore di pulizia",
          "Alexander Fleming andò in vacanza nel 1928 lasciando una coltura batterica sporca. Al ritorno, trovò muffa che uccideva batteri.",
          "Fleming stava lavorando sullo Stafilococco al St. Mary's Hospital di Londra. Tornando dalle ferie il 3 settembre 1928, notò una piastra contaminata da Penicillium notatum con aloni privi di batteri intorno alla muffa. Capì il potenziale ma non riuscì a purificare la penicillina. Howard Florey ed Ernst Chain riuscirono nel 1941; tutti e tre vinsero il Nobel 1945. La penicillina ha salvato oltre 200 milioni di vite. Il disordine di Fleming è diventato proverbiale tra i ricercatori."),

    # ========== FILOSOFIA (+2) ==========
    _fact("Filosofia", "Gli stoici si allenavano alla morte quotidianamente",
          "Il 'memento mori' (ricorda che morirai) era pratica stoica giornaliera. Marco Aurelio lo annotava nei suoi 'Pensieri'.",
          "Stoicismo romano (Seneca, Epitteto, Marco Aurelio): la consapevolezza della morte libera dalle paure futili e rende ogni momento prezioso. 'Vivi come se fosse il tuo ultimo giorno' non era cliché, era pratica filosofica. Gli stoici praticavano 'praemeditatio malorum' (premeditare i mali): immaginare perdite prima che accadano per attenuarne l'impatto emotivo. Oggi la psicoterapia cognitiva applica principi stoici. Ryan Holiday e Tim Ferriss hanno rilanciato lo stoicismo come filosofia di vita moderna."),
    _fact("Filosofia", "Diogene viveva in una botte e sputava in faccia ai ricchi",
          "Filosofo cinico, Diogene rifiutò tutte le convenzioni. Ad Alessandro Magno chiese solo di 'spostarsi perché gli toglieva il sole'.",
          "Diogene di Sinope (V-IV sec a.C.) disprezzava ricchezza, fama, potere. Viveva per strada in una giara (non proprio una botte) con un mantello e una ciotola (che buttò quando vide un bambino bere con le mani). Si masturbava in pubblico, affermando di desiderare di 'placare la fame con lo stesso gesto'. Diceva di 'cercare un uomo onesto' con una lanterna in pieno giorno. Alessandro Magno, stupito dall'uomo che nulla voleva, disse: 'Se non fossi Alessandro, vorrei essere Diogene'."),

    # ========== ECONOMIA (+2) ==========
    _fact("Economia", "I Rothschild sono più ricchi di tutti i miliardari moderni combinati",
          "Al picco del XIX secolo, la fortuna dei Rothschild era stimata allo 0,62% del PIL mondiale, equivalente oggi a ~500 miliardi di dollari.",
          "La dinastia ebraico-tedesca, fondata da Mayer Amschel Rothschild (1744-1812) a Francoforte, finanziò governi durante le guerre napoleoniche. Nathan Rothschild usò piccioni viaggiatori per anticipare i risultati di Waterloo e fare fortuna in borsa. Finanziò il Canale di Suez per l'Inghilterra, fermò Bismarck, sostenne i Romanov. Oggi la famiglia (circa 400 discendenti documentati) gestisce 630 miliardi in asset bancari. La crescita esponenziale ha portato Forbes a non considerare la famiglia nel ranking dei miliardari (troppo dispersa)."),
    _fact("Economia", "Il pezzo di carta da 100 dollari costa 13,1 centesimi",
          "La banconota da $100 costa 13 centesimi agli USA. Il guadagno del signoraggio: $99,87 per ogni banconota stampata.",
          "Il 'signoraggio' è la differenza tra valore facciale e costo di produzione. Gli USA stampano 8,3 miliardi di banconote l'anno (la maggior parte per sostituire quelle usurate). La $100 è la più 'contraffatta' al mondo, con il 20% delle fake dollar circulation. Il valore è garantito solo dalla fiducia nel governo federale (fiat money) dal 1971, quando Nixon abolì il gold standard. Bitcoin nacque come 'signoraggio digitale' alternativo, ma la sua volatilità lo rende ancora impraticabile come valuta."),

    # ========== LETTERATURA (+2) ==========
    _fact("Letteratura", "Agatha Christie scrisse 66 gialli; solo Shakespeare vende di più",
          "Le sue 66 detective novels hanno venduto 2 miliardi di copie. È seconda solo a Shakespeare e alla Bibbia come autrice più letta.",
          "Hercule Poirot apparve in 33 romanzi, Miss Marple in 12. Christie è anche autrice della più longeva opera teatrale al mondo: 'The Mousetrap' è in scena a Londra ininterrottamente dal 1952 (con pausa COVID). Ha scritto sotto pseudonimo (Mary Westmacott) e usato la sua conoscenza di farmacologia per creare 83 veleni nelle storie. Nel 1926 scomparve misteriosamente per 11 giorni, tornò senza mai spiegarlo (probabile amnesia dissociativa)."),
    _fact("Letteratura", "Tolkien creò il Quenya (elfico) prima della storia del Signore degli Anelli",
          "Tolkien era filologo: costruì prima le lingue elfiche, poi inventò un mondo e una storia per giustificarle.",
          "Lavorò a Quenya (alto elfico) e Sindarin per 50 anni. Disse: 'Le storie furono create per fornire un mondo alle lingue'. Era professore di anglosassone a Oxford. Il Silmarillion, genealogie elfiche complete, è più lungo del Signore degli Anelli. Al suo funerale nel 1973, fu letto un passaggio in Sindarin. Esistono oggi dizionari elfici accademici, persone che si sposano in Quenya, e gruppi di linguisti che ancora espandono le grammatiche. Tolkien inventò anche il Khuzdul (nanico), Adunaic e la 'Black Speech' di Mordor."),

    # ========== ANIMALI (+4) ==========
    _fact("Animali", "I delfini si chiamano per nome",
          "Ogni delfino ha un fischio-firma unico. Altri delfini 'invocano' un amico riproducendo il suo fischio-nome.",
          "Studio del St Andrews University (2013): analizzando 4.000 fischi di delfini della Florida, gli scienziati identificarono nomi unici. Quando riproducono il 'nome' di un delfino familiare, questo risponde; il nome di uno sconosciuto: silenzio. Sono l'unica specie (oltre all'uomo) a usare nomi per individui specifici. I delfini madre insegnano il loro 'nome' alla prole. Si riconoscono allo specchio, risolvono problemi complessi, e in Giappone sono stati addestrati al servizio militare. Il loro cervello ha 40 miliardi di neuroni (l'umano ne ha 86)."),
    _fact("Animali", "I koala dormono 22 ore al giorno",
          "Mangiano eucalipto, il cui tossico consumo di energia li costringe a 22 ore di sonno. Al cervello arriva pochissimo ossigeno.",
          "L'eucalipto è altamente tossico e povero di nutrienti; il koala ha un sistema digestivo specializzato (caecum lunghissimo, 2 metri) con batteri che neutralizzano i tannini. Masticano lentamente, dormono tanto per risparmiare energia. Il cervello del koala è atrofizzato (0,2% del peso corporeo, rapporto più basso dei primati). Sono solitari, non sono tecnicamente 'orsi'. Le epidemie di clamidia (trasmessa sessualmente tra koala) hanno decimato la specie del 30%. Classificati 'a rischio' dal 2022."),
    _fact("Animali", "Il cuore di una balenottera azzurra pesa come un'auto",
          "Il cuore della blue whale pesa 180 kg ed è grande come una Smart. I suoi vasi sanguigni sono abbastanza grandi da far passare un uomo.",
          "La balenottera azzurra (33m, 200 tonnellate) è il più grande animale mai vissuto, più grande di qualsiasi dinosauro. Il suo cuore batte 8-10 volte al minuto (4-8 volte sott'acqua), ma può pompare 220 litri di sangue per battito. La sua lingua pesa 3,5 tonnellate (quanto un elefante). Il suo canto è più forte di un jet (188 dB) e viaggia per 1.000 km sott'acqua. Quasi estinto a inizio '900 (300.000 uccise per olio), oggi ne restano 10.000-25.000.",
          [{"title": "WWF Blue Whale Factsheet", "url": "https://www.worldwildlife.org/species/blue-whale"}]),
    _fact("Animali", "I pinguini imperatori fanno fila per centinaia di km",
          "Ogni anno i maschi camminano 120 km nell'Antartide (-60°C) per incubare l'uovo. Non mangiano per 65 giorni.",
          "Il pinguino imperatore riproduce durante l'inverno antartico. La femmina depone un uovo e lo consegna al maschio che lo 'cova' sui piedi sotto una plica di pelle. Lei torna all'oceano a pescare per 65 giorni. Senza cibo e a temperature letali, i maschi si stringono in 'huddles' (cerchi rotanti) riscaldandosi a turno al centro. Perdono metà peso corporeo. L'uovo schiude quando torna la madre che nutre il piccolo. Documentato magistralmente in 'March of the Penguins' (2005, Oscar al Miglior Documentario)."),

    # ========== MATEMATICA (+2) ==========
    _fact("Matematica", "C'è un numero primo più grande di tutti gli altri",
          "No! Euclide dimostrò 2300 anni fa che i primi sono infiniti. La dimostrazione è elegante e ancora insegnata oggi.",
          "Euclide, negli 'Elementi' (libro IX, proposizione 20, ~300 a.C.): assumiamo che esista un numero primo più grande, chiamiamolo P. Moltiplica tutti i primi fino a P e aggiungi 1: (2×3×5×7×...×P)+1. Questo numero N non è divisibile per nessun primo fino a P (resto sempre 1). Quindi o N è primo, oppure è divisibile per un primo maggiore di P. Contraddizione. I primi sono infiniti. Il più grande attualmente conosciuto (2024) è 2^136279841-1, con oltre 41 milioni di cifre. Scoperto nell'ottobre 2024 dal GIMPS project.",
          [{"title": "GIMPS Mersenne Primes", "url": "https://www.mersenne.org/"}]),
    _fact("Matematica", "0,999... è esattamente uguale a 1",
          "Non 'quasi' 1. Sono matematicamente identici. La dimostrazione: se x = 0,999..., allora 10x = 9,999..., quindi 10x - x = 9, da cui x = 1.",
          "Questo fatto sconvolge chiunque ma è elementare. Dimostrazione alternativa: 1/3 = 0,333... Moltiplicando per 3: 3/3 = 0,999... ma 3/3 = 1. Quindi 0,999... = 1. I numeri reali hanno rappresentazioni decimali multiple: 1 = 1,000... = 0,999... L'errore intuitivo deriva dal pensare al decimale come 'si avvicina a 1' invece che ESSERE 1. In teoria dei numeri, questo illustra che i decimali sono notazione, non l'essenza del numero. Nella analisi, limite e valore coincidono."),

    # ========== VIAGGI (+2) ==========
    _fact("Viaggi", "Il volo più corto al mondo dura 47 secondi",
          "Westray-Papa Westray nelle Isole Orcadi (Scozia): 2,7 km, volo da record. Alcuni piloti l'hanno fatto in 47 secondi con vento favorevole.",
          "Operato da Loganair dal 1967, collega due isole scozzesi con meno di 70 abitanti complessivi. Il biglietto costa ~30 sterline. Il tempo medio di volo è 1,5 minuti, ma il record (2015) è di 47 secondi. Lo usano scolari, pazienti e lavoratori. Paradosso: il volo programmato più corto del mondo in un paese dove il treno più lungo da fondo a capo (LondonEurostar) dura ~7 ore. I piloti lo usano anche come ultimo training per piste corte."),
    _fact("Viaggi", "In Giappone esistono più hotel abbandonati che in attività",
          "Bubble-era hotels vuoti (chiamati 'haikyo') punteggiano il paese. Alcuni sono tramutati in attrazioni di dark tourism.",
          "La bolla speculativa giapponese degli anni '80 portò alla costruzione di migliaia di hotel resort. Dopo il crollo del 1991, molti fallirono. 'Haikyo' (廃墟 - rovine) è un sottoturismo in crescita. Gli esempi: 'Nara Dreamland' (parco Disneyland copia, chiuso 2006), 'Gunkanjima' (isola mineraria abbandonata, UNESCO), gli hotel di Hashima. Il Giappone ha anche 8 milioni di case vuote ('akiya'), alcune gratuite per chi vuole trasferirsi. Fenomeno legato al calo demografico e alla concentrazione urbana a Tokyo."),

    # ========== MITOLOGIA (+2) ==========
    _fact("Mitologia", "Gli dei greci erano terribili genitori",
          "Zeus inghiottì una moglie, Cronos divorava i figli, Afrodite era nata dai testicoli tagliati di Urano. Nessun culto più dark.",
          "La genealogia greca è un horror freudiano: Urano odiava i figli e li ricacciava nel grembo di Gea. Cronos lo evirò e divorò a sua volta i figli per timore della profezia. Rea nascose Zeus e diede a Cronos una pietra avvolta da fasce. Zeus crescendo avvelenò Cronos facendogli rigettare i fratelli. Poi sposò la sorella Hera (incestuosa-consensuale) con tanti tradimenti divini. Il culto olimpico era meno morale di quelli misterici (Eleusi, Orfismo) dove si cercava purificazione. I Romani ereditarono tutto e aggiunsero crudeltà politica."),
    _fact("Mitologia", "Il drago non è europeo: è universale",
          "Tutte le culture del mondo hanno draghi: cinesi, aztechi, egizi, norreni, australiani aborigeni. Nessun collegamento storico.",
          "I dragoni cinesi (Long) portano fortuna e pioggia. Quetzalcoatl (azteco) era il serpente piumato della conoscenza. Apophis (egizio) incarnava il caos. Jormungandr (norreno) circondava il mondo. I Rainbow Serpents aborigeni creavano i fiumi. Perché ovunque? Teorie: (a) ricordi evolutivi di predatori rettili-avifauna, (b) fossili di dinosauri interpretati da civiltà antiche, (c) archetipo junghiano del caos primordiale. Carl Sagan ipotizzò nei 'Drammi dell'Eden' un'origine in ricordi genetici di coccodrilli preistorici."),
]
