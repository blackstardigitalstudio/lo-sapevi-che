"""Seed database with curated Italian fun facts across all niches."""
from typing import List, Dict

CATEGORIES = [
    "Scienza", "Storia", "Tecnologia", "Natura", "Spazio",
    "Cucina", "Sport", "Arte", "Psicologia", "Cinema",
    "Musica", "Geografia", "Medicina", "Filosofia", "Economia",
    "Letteratura", "Animali", "Matematica", "Viaggi", "Mitologia",
]

CATEGORY_EMOJI = {
    "Scienza": "flask",
    "Storia": "book",
    "Tecnologia": "hardware-chip",
    "Natura": "leaf",
    "Spazio": "planet",
    "Cucina": "restaurant",
    "Sport": "football",
    "Arte": "color-palette",
    "Psicologia": "happy",
    "Cinema": "film",
    "Musica": "musical-notes",
    "Geografia": "earth",
    "Medicina": "medkit",
    "Filosofia": "bulb",
    "Economia": "trending-up",
    "Letteratura": "library",
    "Animali": "paw",
    "Matematica": "calculator",
    "Viaggi": "airplane",
    "Mitologia": "flash",
}

# Image category mapping for cover
CATEGORY_IMAGE_GROUP = {
    "Spazio": "background_space",
    "Storia": "background_history",
    "Mitologia": "background_history",
    "Scienza": "background_science",
    "Medicina": "background_science",
    "Matematica": "background_science",
    "Tecnologia": "background_science",
    "Natura": "background_nature",
    "Animali": "background_nature",
    "Geografia": "background_nature",
    "Viaggi": "background_nature",
    "Arte": "background_history",
    "Letteratura": "background_history",
    "Filosofia": "background_history",
    "Cucina": "background_nature",
    "Sport": "background_science",
    "Cinema": "background_space",
    "Musica": "background_space",
    "Psicologia": "background_science",
    "Economia": "background_history",
}

IMAGE_URLS = {
    "background_space": "https://images.unsplash.com/photo-1505506874110-6a7a69069a08?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNDR8MHwxfHNlYXJjaHwyfHxzcGFjZSUyMGdhbGF4eSUyMHN0YXJzJTIwZGFyayUyMGJhY2tncm91bmR8ZW58MHx8fHwxNzc2NTM0NjkyfDA&ixlib=rb-4.1.0&q=85",
    "background_history": "https://images.unsplash.com/photo-1555689572-28a3fb27533f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjh8MHwxfHNlYXJjaHw0fHxhbmNpZW50JTIwcm9tYW4lMjBzY3VscHR1cmUlMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzY1MzQ2ODR8MA&ixlib=rb-4.1.0&q=85",
    "background_science": "https://images.unsplash.com/photo-1766713655637-45c84da72c37?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2OTV8MHwxfHNlYXJjaHw0fHxtaWNyb3Njb3BlJTIwZ2xvd2luZyUyMHNjaWVuY2UlMjBhYnN0cmFjdHxlbnwwfHx8fDE3NzY1MzQ2OTJ8MA&ixlib=rb-4.1.0&q=85",
    "background_nature": "https://images.unsplash.com/photo-1548320685-0b7a2d62bac4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTJ8MHwxfHNlYXJjaHwzfHxkYXJrJTIwbWlzdHklMjBmb3Jlc3QlMjBjYW5vcHklMjB2ZXJ0aWNhbHxlbnwwfHx8fDE3NzY1MzQ2OTJ8MA&ixlib=rb-4.1.0&q=85",
}


def _image_for(category: str) -> str:
    group = CATEGORY_IMAGE_GROUP.get(category, "background_space")
    return IMAGE_URLS[group]


def _fact(category: str, title: str, short: str, deep: str) -> Dict:
    return {
        "category": category,
        "title": title,
        "short_fact": short,
        "deep_dive": deep,
        "image_url": _image_for(category),
        "source": "seed",
    }


SEED_FACTS: List[Dict] = [
    # ---------- SCIENZA ----------
    _fact("Scienza", "L'acqua calda può ghiacciare prima di quella fredda",
          "In certe condizioni, l'acqua calda congela più velocemente di quella fredda: è l'effetto Mpemba.",
          "Scoperto ufficialmente nel 1963 dallo studente tanzaniano Erasto Mpemba, questo fenomeno sfida l'intuizione termodinamica. Le spiegazioni proposte includono: evaporazione più intensa nell'acqua calda (riducendone la massa), minori gas disciolti, correnti convettive differenti e la struttura dei legami idrogeno che si riorganizzano. Ancora oggi gli scienziati dibattono sul meccanismo principale, ma l'effetto è replicabile e viene studiato per migliorare sistemi di refrigerazione industriale."),
    _fact("Scienza", "I diamanti piovono su Nettuno",
          "Sui giganti gassosi Nettuno e Urano la pressione è così elevata che il metano si trasforma letteralmente in pioggia di diamanti.",
          "A migliaia di chilometri sotto la superficie nuvolosa, le pressioni superano i milioni di atmosfere e temperature di migliaia di gradi. Il metano (CH4) viene spezzato: l'idrogeno si libera e il carbonio si compatta fino a cristallizzare in diamanti, che poi 'piovono' verso il nucleo. Nel 2017, esperimenti al laser SLAC hanno ricreato queste condizioni e osservato la formazione di nanodiamanti in tempo reale, confermando l'ipotesi teorizzata per decenni."),
    _fact("Scienza", "Il tuo corpo è più batterio che umano",
          "Ospiti circa 38 trilioni di batteri: più del numero delle tue stesse cellule.",
          "Il microbioma umano pesa fino a 2 kg e contiene 100 volte più geni del nostro genoma. Questi microbi regolano digestione, sistema immunitario, umore (attraverso l'asse intestino-cervello) e persino il rischio di obesità. La ricerca moderna ha mostrato che trapianti fecali possono curare infezioni resistenti, e composizioni specifiche del microbioma sono collegate ad autismo, depressione e malattie autoimmuni."),

    # ---------- STORIA ----------
    _fact("Storia", "Cleopatra visse più vicino al primo iPhone che alla piramide di Giza",
          "Tra Cleopatra (69 a.C.) e il primo iPhone (2007) passano ~2076 anni. Tra Cleopatra e la Grande Piramide (~2560 a.C.) ne passano 2491.",
          "Questa prospettiva temporale sconvolge perché mostra quanto sia antica la civiltà egizia. Cleopatra era affascinata dalle piramidi come reliquie di un passato già remoto. Al suo tempo esisteva già una 'turismo archeologico' egiziano, con guide e iscrizioni graffite lasciate da visitatori greci e romani. Parlava nove lingue e fu l'ultima faraona d'Egitto, governante abile più che seduttrice come la racconta la propaganda romana di Augusto."),
    _fact("Storia", "Oxford è più antica degli Aztechi",
          "L'Università di Oxford teneva lezioni nel 1096. L'Impero Azteco nacque nel 1428, oltre 300 anni dopo.",
          "Oxford è una delle università più antiche del mondo occidentale ancora attive. Quando i primi professori discutevano di teologia scolastica, il popolo Mexica era ancora una tribù seminomade. Tenochtitlán, la straordinaria capitale azteca costruita su un lago, venne fondata nel 1325, con Oxford che già sfornava teologi da oltre due secoli. Ci ricorda che la 'storia' non è lineare: civiltà molto distanti sono fiorite in epoche sovrapposte in modi sorprendenti."),
    _fact("Storia", "La Seconda Guerra Mondiale tecnicamente continuò fino al 2006",
          "L'ultimo soldato giapponese si arrese nel 1974, ma una piccola isola restò ufficialmente in guerra con la Germania fino al 2006.",
          "Hiroo Onoda combatté nelle Filippine fino al 1974, quando il suo ex ufficiale andò personalmente a ordinargli di deporre le armi. Inoltre, l'isola olandese di Berlengas-Schiermonnikoog firmò solo nel 2006 un trattato formale di pace con la Germania: la dichiarazione originale era stata dimenticata. Gli accordi di pace formali, distinti dagli armistizi, sono complessi: tecnicamente Russia e Giappone non hanno mai firmato un trattato di pace per la Seconda Guerra Mondiale."),

    # ---------- TECNOLOGIA ----------
    _fact("Tecnologia", "Il primo spam fu inviato nel 1978",
          "Gary Thuerk spedì un'email pubblicitaria a 393 persone sulla rete ARPANET: vendette computer per 13 milioni di dollari.",
          "Thuerk, marketing manager di Digital Equipment Corporation, è considerato il padre dello spam. L'email promuoveva i nuovi DECSYSTEM-20. La reazione fu mista: molti si lamentarono, ma il ROI fu enorme. Oggi lo spam rappresenta oltre il 45% delle email mondiali (circa 122 miliardi al giorno), generato principalmente da botnet. I filtri antispam moderni usano machine learning bayesiano e analisi delle reputazioni IP per bloccarne il 99,9%."),
    _fact("Tecnologia", "Google cancellava i risultati per 'il gioco' per ore",
          "Il primo videogioco Google Doodle (Pac-Man, 2010) fece perdere al mondo 4,8 milioni di ore di produttività in un giorno.",
          "Secondo stime di RescueTime, i 500 milioni di persone che giocarono a Pac-Man sul logo Google causarono una perdita globale stimata in 120 milioni di dollari di produttività. Google non si scoraggiò: da allora ha rilasciato decine di giochi interattivi nei Doodle. Il più longevo è 'Coding Carrots' del 2017, primo Doodle AI-powered. Il team Doodle conta circa 10 artisti stabili chiamati 'Doodlers' e produce oltre 5000 Doodle l'anno."),

    # ---------- NATURA ----------
    _fact("Natura", "Gli alberi 'parlano' tra loro attraverso il suolo",
          "Le foreste comunicano via funghi micorrizici: una 'wood wide web' sotterranea che scambia zuccheri e segnali chimici.",
          "Scoperta dalla biologa Suzanne Simard, la rete micorrizica collega fino al 90% delle piante terrestri. Gli alberi più vecchi (madri) trasferiscono carbonio ai giovani, avvertono dell'arrivo di parassiti rilasciando segnali chimici, e supportano specie diverse. In una singola cucchiaiata di terreno forestale ci sono più organismi di tutti gli umani mai esistiti. Questa scoperta ha rivoluzionato la silvicoltura: tagliare 'alberi madre' destabilizza intere foreste."),
    _fact("Natura", "Il miele non scade mai",
          "Archeologi hanno trovato vasi di miele di 3000 anni nelle tombe egizie ancora perfettamente commestibili.",
          "Il miele è uno dei pochi alimenti praticamente eterni grazie a tre proprietà: bassissima umidità (17%), elevata acidità (pH 3-4.5) e presenza di perossido di idrogeno prodotto dalle api. Questi fattori impediscono qualsiasi crescita microbica. I greci lo usavano come conservante per la carne, e Alessandro Magno fu trasportato a Babilonia immerso nel miele per preservarne il corpo. L'unica nemica è l'acqua: se diluito, fermenta e si trasforma in idromele."),

    # ---------- SPAZIO ----------
    _fact("Spazio", "Un giorno su Venere dura più di un anno",
          "Venere ruota così lentamente che un giorno venusiano (243 giorni terrestri) è più lungo del suo anno (225 giorni).",
          "Venere è l'unico pianeta del Sistema Solare che ruota in senso orario (retrogrado). Una teoria suggerisce che un impatto colossale nel passato rovesciò completamente il pianeta. La sua atmosfera di anidride carbonica crea un effetto serra estremo: 462°C in superficie, abbastanza da fondere il piombo. La pressione equivale a trovarsi a 900 metri sott'acqua. Nonostante ciò, alcune proposte scientifiche ipotizzano colonie galleggianti a 50 km di altitudine, dove pressione e temperatura sono quasi terrestri."),
    _fact("Spazio", "Esiste una nube di alcol nello spazio",
          "Nel 2006 è stata scoperta una nube di etanolo grande miliardi di chilometri: conterrebbe abbastanza alcol per 400 quadrilioni di pinte di birra.",
          "La nube G34.3 si trova a 10.000 anni luce dalla Terra nella costellazione dell'Aquila. Non è solo etanolo: contiene anche metanolo (tossico) e molecole organiche complesse come amminoacidi precursori. Queste 'fabbriche chimiche' interstellari rafforzano la teoria che i mattoni della vita si siano formati nello spazio e trasportati sulla Terra dalle comete. La chimica prebiotica spaziale è uno dei campi più caldi dell'astrobiologia."),

    # ---------- CUCINA ----------
    _fact("Cucina", "Le carote erano viola, non arancioni",
          "Le carote originali erano viola, gialle o bianche. La varietà arancione fu creata dagli olandesi nel XVII secolo per onorare Guglielmo d'Orange.",
          "Le prime carote coltivate in Afghanistan ~900 d.C. erano viola e gialle. I selezionatori olandesi incrociarono varietà mutanti per creare un ibrido arancione dolce, meno amaro e più ricco di betacarotene. Divenne simbolo patriottico della Casa d'Orange. Oggi stanno tornando di moda le carote viola 'heirloom' per il loro contenuto di antociani, potenti antiossidanti. L'Italia coltiva ancora la rara 'carota di Polignano' viola, presidio Slow Food."),
    _fact("Cucina", "La Nutella nacque come ripiego bellico",
          "Nel 1946 Pietro Ferrero, non potendo comprare cacao a causa del razionamento, lo mescolò con nocciole piemontesi creando la Giandujot, antenata della Nutella.",
          "Il blocco commerciale del dopoguerra rese il cacao proibitivo. Ferrero ebbe l'intuizione di usare le nocciole 'Tonda Gentile delle Langhe', abbondanti in Piemonte. Il risultato, inizialmente un pane di cioccolato da tagliare a fette, divenne spalmabile nel 1951 come 'Supercrema' e nel 1964 fu ribattezzato Nutella. Oggi Ferrero usa il 25% delle nocciole mondiali: 365.000 tonnellate l'anno. Un vaso viene prodotto ogni 2,5 secondi."),

    # ---------- SPORT ----------
    _fact("Sport", "Il calcio moderno fu inventato dagli studenti inglesi nel 1848",
          "Le 'Regole di Cambridge' del 1848 furono il primo tentativo di unificare le regole del football: prima ogni scuola aveva le sue.",
          "Prima del 1848, ogni college inglese giocava secondo regole proprie: Eton calciava, Rugby portava la palla in mano. Gli studenti di Cambridge si riunirono per creare un codice condiviso, abolendo il gioco con le mani. Nel 1863 nacque la Football Association, che codificò definitivamente le regole. Il Brasile, che non inventò il calcio, lo perfezionò: ha vinto 5 Mondiali, più di chiunque altro. Ma il paese con più vittorie per abitante è l'Uruguay: 2 Mondiali con 3,5 milioni di abitanti."),

    # ---------- ARTE ----------
    _fact("Arte", "Monet dipinse Le Ninfee mentre diventava cieco",
          "Negli ultimi vent'anni Monet soffrì di cataratta grave: le sue ninfee divennero sempre più astratte e rossastre perché percepiva così il mondo.",
          "Dopo l'operazione nel 1923 (tecnica rudimentale), Monet riacquistò la visione dei blu e dei viola: rimase scioccato nel vedere che alcune sue tele erano dominate dal rosso, e ne distrusse molte. I suoi ultimi capolavori delle Ninfee, oggi esposti all'Orangerie di Parigi, mostrano come percezione alterata e genio creativo possano fondersi. Studi del MIT hanno simulato digitalmente la sua vista, permettendo di 'vedere' i dipinti come li vedeva lui: un'esperienza commovente."),

    # ---------- PSICOLOGIA ----------
    _fact("Psicologia", "Il cervello è prevedibilmente irrazionale",
          "Gli umani non sono 'a volte' irrazionali: lo sono sistematicamente. Lo ha dimostrato Daniel Kahneman con la teoria dei due sistemi di pensiero.",
          "Kahneman (Nobel 2002) distinse 'Sistema 1' (veloce, intuitivo, emotivo) e 'Sistema 2' (lento, logico, faticoso). Il Sistema 1 domina il 95% delle decisioni e crea bias cognitivi: ancoraggio, effetto framing, avversione alle perdite (soffriamo il doppio per perdere 100€ rispetto al piacere di guadagnarne 100). Aziende e governi usano 'nudge' per sfruttare questi bias: un salvadanaio automatico di default aumenta i risparmi del 300% rispetto all'opt-in manuale."),

    # ---------- CINEMA ----------
    _fact("Cinema", "Toy Story fu quasi perso completamente",
          "Nel 1998, un comando errato cancellò il 90% dei file di Toy Story 2. Solo la copia di backup di una dipendente in maternità salvò il film.",
          "Durante un normale backup, qualcuno eseguì 'rm -rf' sulla root del server Pixar. In 20 secondi sparirono due anni di lavoro. I backup erano corrotti. La supervisor Galyn Susman aveva però una copia completa a casa per lavorare con il figlio neonato: fu trasportata come una reliquia alla Pixar. Il film, comunque, fu riscritto e ridisegnato largamente dopo. Oggi Pixar ha sistemi di backup ridondanti multipli distribuiti. La storia è raccontata nel documentario 'The Pixar Story'."),

    # ---------- MUSICA ----------
    _fact("Musica", "Mozart scrisse la sua prima sinfonia a 8 anni",
          "A 8 anni Mozart aveva già composto la Sinfonia n.1 in Mi bemolle maggiore. A 14 trascrisse a memoria il Miserere di Allegri, segreto del Vaticano.",
          "Il Miserere era cantato solo nella Cappella Sistina; copiarlo era scomunica. Mozart lo ascoltò una volta e lo riscrisse perfettamente dopo due ascolti. Il Papa, invece di punirlo, gli conferì l'Ordine dello Speron d'Oro. Mozart compose oltre 600 opere in 35 anni di vita, incluse 41 sinfonie, 27 concerti per piano e 22 opere liriche. Morì a 35 anni, probabilmente di febbre reumatica, lasciando incompiuto il suo Requiem. La sua musica attiva più aree cerebrali di qualsiasi altra: il fenomeno 'effetto Mozart'."),

    # ---------- GEOGRAFIA ----------
    _fact("Geografia", "Esiste un lago dentro un lago dentro un'isola dentro un lago",
          "Sulla Filippina Luzon, Vulcan Point è un'isola in un lago, su un'isola (Volcano Island), in un lago (Taal Lake), su un'isola (Luzon).",
          "Questa matrioska geografica nasce da un cratere vulcanico riempito d'acqua. Il vulcano Taal è uno dei più attivi delle Filippine (ultima eruzione 2022) e tra i più pericolosi: 'Decade Volcano' classificato dall'ONU. L'acqua del Taal Lake era un tempo un'insenatura marina isolata da eruzioni: ancora oggi ospita l'unico squalo di acqua dolce del mondo, specie in via di estinzione. La struttura simile esiste anche in Canada (Isola di Victoria) e in Indonesia."),

    # ---------- MEDICINA ----------
    _fact("Medicina", "Il cuore può battere anche fuori dal corpo",
          "Il cuore umano ha un sistema elettrico autonomo: continua a battere per ore se tenuto in soluzione nutritiva.",
          "Il nodo senoatriale genera impulsi elettrici indipendenti dal cervello. Nei trapianti, il cuore viene conservato fuori dal corpo fino a 6 ore a 4°C, e nuove tecnologie di 'perfusione ex vivo' (come OCS Heart) lo mantengono battente e funzionante fino a 12 ore. Questo ha rivoluzionato i trapianti: oggi si possono valutare i cuori prima di impiantarli. Il cuore di un donatore morto (DCD) ora può essere riavviato con successo, aumentando del 30% gli organi disponibili."),

    # ---------- FILOSOFIA ----------
    _fact("Filosofia", "Socrate non scrisse mai nulla",
          "Tutto ciò che sappiamo del pensiero di Socrate lo conosciamo tramite i suoi allievi, soprattutto Platone. Lui stesso sosteneva che la scrittura indebolisse la memoria.",
          "Nel 'Fedro', Platone fa dire a Socrate che la scrittura è un 'farmaco' ingannevole: dà l'illusione della conoscenza senza vera comprensione. Oggi gli studiosi parlano di 'problema socratico': distinguere il Socrate storico da quello letterario platonico è quasi impossibile. Ironicamente, l'uomo che preferiva il dialogo orale è diventato il filosofo più influente della storia occidentale attraverso i testi scritti. Studi recenti sulla memoria confermano: memorizziamo il 10% di ciò che leggiamo ma il 70% di ciò che discutiamo."),

    # ---------- ECONOMIA ----------
    _fact("Economia", "La crisi dei tulipani fu la prima bolla finanziaria",
          "Nel 1637, ad Amsterdam, un singolo bulbo di tulipano valeva più di una casa. Poi il mercato crollò in una settimana.",
          "La 'Tulipomania' olandese del 1634-37 fu il primo caso documentato di bolla speculativa. I tulipani, rari e esotici, divennero status symbol. Si crearono mercati a termine su bulbi che non esistevano ancora. Un 'Semper Augustus' fu venduto per 10.000 fiorini (15 volte lo stipendio annuo di un artigiano). Quando un'asta ad Haarlem non trovò compratori, il panico fece crollare i prezzi del 99%. Lezione applicata ancora oggi a bitcoin, NFT e meme stock: le bolle hanno tutte gli stessi 4 stadi (Hyman Minsky): stealth, awareness, mania, blow-off."),

    # ---------- LETTERATURA ----------
    _fact("Letteratura", "Dante inventò l'italiano moderno",
          "Prima della Divina Commedia (1321) si parlavano solo dialetti regionali. Il 'volgare illustre' di Dante divenne la base dell'italiano standard.",
          "Dante scelse di scrivere in volgare toscano invece che in latino per raggiungere il popolo. Aggiunse oltre 1200 neologismi ancora in uso: 'quisquilia', 'fulgore', 'trasumanar', 'inurbarsi'. Nel 'De Vulgari Eloquentia' teorizzò l'italiano come lingua letteraria. L'italiano moderno è il più vicino al latino tra le lingue romanze e ancora oggi il 90% delle parole italiane è riconducibile al toscano trecentesco. La prima grammatica italiana (Pietro Bembo, 1525) prese Dante come modello canonico."),

    # ---------- ANIMALI ----------
    _fact("Animali", "I polpi hanno tre cuori e sangue blu",
          "Due cuori pompano ai branchie, uno al corpo. Il sangue è blu perché usa rame invece di ferro per trasportare ossigeno.",
          "L'emocianina (proteina del rame) è meno efficiente dell'emoglobina ma funziona meglio in acque fredde e povere di ossigeno. I polpi hanno anche 9 cervelli: uno centrale e uno per ogni braccio, capaci di decidere autonomamente. Il 60% dei loro neuroni è nei tentacoli. Sanno aprire barattoli, riconoscere volti umani, usare strumenti, risolvere labirinti e scappare da acquari chiusi. Vivono solo 1-5 anni: la morte è programmata dopo la riproduzione. Sono considerati tra gli animali più alieni della Terra."),

    # ---------- MATEMATICA ----------
    _fact("Matematica", "Esistono infiniti più grandi di altri infiniti",
          "Georg Cantor dimostrò che ci sono 'dimensioni' di infinito: quello dei numeri naturali è minore di quello dei numeri reali.",
          "Cantor introdusse gli 'aleph' per classificare gli infiniti: ℵ₀ (aleph-zero) è l'infinito numerabile dei naturali, ℵ₁ il successivo. Con il metodo diagonale dimostrò che i numeri reali tra 0 e 1 sono 'più infiniti' dei naturali: impossibili da mettere in corrispondenza uno a uno. La sua scoperta fece impazzire matematici contemporanei come Kronecker ('Cantor è un corruttore di gioventù') e alla fine Cantor stesso: morì in un manicomio. Oggi è considerato il padre della teoria degli insiemi."),

    # ---------- VIAGGI ----------
    _fact("Viaggi", "La Russia confina con la Corea del Nord",
          "Russia e Corea del Nord condividono 17 km di confine terrestre: uno dei confini più sottili e controllati del mondo.",
          "Il confine segue il fiume Tumen ed è attraversato da un'unica ferrovia 'Amicizia' aperta nel 1959. La Russia ha 14 paesi confinanti, record mondiale. La Cina ne ha anch'essa 14. Esistono confini bizzarri: l'enclave italiana di Campione d'Italia in Svizzera, Baarle-Hertog (Belgio in Olanda), il punto tri-confine Brasile-Argentina-Paraguay (una città con tre fusi orari culturali). Il confine più lungo del mondo è USA-Canada (8891 km), completamente non militarizzato."),

    # ---------- MITOLOGIA ----------
    _fact("Mitologia", "I vichinghi credevano in un arcobaleno-ponte",
          "Bifrǫst era il ponte di fuoco e arcobaleno che collegava Midgard (Terra) ad Asgard (regno degli dei). Un giorno crollerà nel Ragnarǫk.",
          "La mitologia norrena è straordinariamente complessa: 9 mondi connessi dall'albero cosmico Yggdrasil, dei destinati a morire (Ragnarǫk), e un pantheon diverso dai canoni mediterranei. Odino sacrificò un occhio per la saggezza e rimase appeso 9 giorni a Yggdrasil per imparare le rune. Thor, dio del tuono, è oggi più famoso grazie ai fumetti Marvel. Le saghe islandesi sono la fonte principale: scritte nel XIII secolo, dopo secoli di tradizione orale. Molti termini moderni derivano dai norreni: Thursday = Thor's day."),
]
