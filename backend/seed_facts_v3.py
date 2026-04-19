"""v3 seed facts: Mafia, Guerre, Motori, Macchine, Moto with sub_category."""
from typing import List, Dict
from image_library import image_for_fact


def _f(category: str, sub: str, title: str, short: str, deep: str, sources=None) -> Dict:
    return {
        "category": category,
        "sub_category": sub,
        "title": title,
        "short_fact": short,
        "deep_dive": deep,
        "image_url": image_for_fact(category, title),
        "source": "seed",
        "sources": sources or [],
    }


V3_FACTS: List[Dict] = [
    # ============ MAFIA ============
    _f("Mafia", "Cosa Nostra",
       "Il primo 'pentito' fu Tommaso Buscetta, padre dei maxiprocessi",
       "Buscetta rivelò nel 1984 a Falcone la struttura piramidale di Cosa Nostra. Le sue rivelazioni cambiarono per sempre la lotta alla mafia.",
       "Tommaso Buscetta era un boss di alto rango entrato in conflitto con i Corleonesi di Totò Riina, che gli uccisero due figli, fratello, cognato e nipoti. Dopo l'estradizione dal Brasile nel 1984, raccontò a Giovanni Falcone la struttura gerarchica della Cupola: famiglie, mandamenti, commissione. Fu il primo a usare il termine 'Cosa Nostra' ufficialmente. Le sue testimonianze permisero i maxiprocessi di Palermo (1986-87) con 475 imputati e 360 condanne. Falcone lo considerava 'un professore di mafiologia'.",
       [{"title": "Wikipedia - Tommaso Buscetta", "url": "https://it.wikipedia.org/wiki/Tommaso_Buscetta"}]),
    _f("Mafia", "Cosa Nostra",
       "Totò Riina fu arrestato dopo 23 anni di latitanza",
       "Il 15 gennaio 1993 Riina fu catturato a Palermo in pieno giorno. Era latitante dal 1969.",
       "Salvatore Riina, detto 'u' curtu' per la bassa statura, era il capo indiscusso dei Corleonesi e ideatore della strategia stragista (Falcone, Borsellino, via dei Georgofili). Fu arrestato dai Carabinieri del ROS guidati dal capitano Ultimo (Sergio De Caprio) mentre guidava tranquillamente la sua auto. Viveva con la famiglia a Palermo sotto falsa identità. Il suo appartamento non fu perquisito per 18 giorni: le istituzioni hanno ancora domande senza risposta su quel vuoto. Morì in carcere nel 2017 a 87 anni."),
    _f("Mafia", "Camorra",
       "La Camorra è più antica di Cosa Nostra",
       "Le origini documentate risalgono al 1400 a Napoli, quindi pre-unitaria. La mafia siciliana è documentata solo dal 1860.",
       "La parola 'Camorra' deriverebbe da 'gamurra' (vestito corto dei malviventi spagnoli) o dall'arabo 'kumar' (gioco d'azzardo). Nasce nelle carceri borboniche come 'Bella Società Riformata', con statuti e rituali. Dopo l'Unità d'Italia i camorristi parteciparono persino alle elezioni. Oggi la Camorra è una delle organizzazioni criminali più ricche del mondo (stimato giro d'affari 100+ miliardi). Differenza chiave con Cosa Nostra: struttura orizzontale (clan in competizione) invece che piramidale.",
       [{"title": "Wikipedia - Camorra", "url": "https://it.wikipedia.org/wiki/Camorra"}]),
    _f("Mafia", "'Ndrangheta",
       "La 'Ndrangheta è la mafia più ricca del mondo",
       "Fattura circa 53 miliardi di euro l'anno: più di McDonald's e Deutsche Bank messe insieme.",
       "Secondo il rapporto Demoskopika 2021, la 'Ndrangheta calabrese controlla l'80% del traffico di cocaina in Europa. Sfrutta la struttura familiare (le 'ndrine sono gruppi di parentela, non si entra senza sangue) che la rende impenetrabile dai pentiti. È presente in 32 paesi (persino Canada e Australia). Il cuore operativo è San Luca, paese di 4.000 abitanti in Aspromonte. Scoperta al mondo dopo la Strage di Duisburg (2007) in Germania dove furono uccisi 6 italiani in una faida interna."),

    # ============ GUERRE ============
    _f("Guerre", "Prima guerra mondiale",
       "La Prima Guerra Mondiale finì per un errore di traduzione",
       "L'ultimatum austriaco alla Serbia del 1914 fu tradotto male: la Serbia accettò 9 punti su 10, ma l'Austria dichiarò comunque guerra.",
       "Il 23 luglio 1914, dopo l'attentato a Sarajevo, l'Austria inviò un ultimatum umiliante alla Serbia con 10 richieste. La Serbia accettò tutte tranne una (permettere investigatori austriaci sul proprio territorio). Alcuni storici ritengono che il rifiuto fosse dovuto anche a traduzioni imprecise tra le cancellerie. L'Austria dichiarò guerra il 28 luglio innescando la reazione a catena delle alleanze. Morirono 17 milioni di persone in 4 anni. La Grande Guerra fu anche la prima con carri armati, gas tossici e aerei da combattimento."),
    _f("Guerre", "Seconda guerra mondiale",
       "I nazisti crearono il primo personal computer (Zuse Z3)",
       "Nel 1941 Konrad Zuse costruì in Germania il primo computer completamente automatico e programmabile, lo Z3. Era per calcoli aeronautici militari.",
       "Lo Z3 usava relè elettromeccanici (2.600 pezzi), calcolava in binario e sapeva eseguire sottoprogrammi. Fu distrutto dai bombardamenti alleati nel 1943. Zuse sviluppò anche Plankalkül, considerato il primo linguaggio di programmazione ad alto livello. Le autorità naziste non capirono l'importanza strategica: finanziarono solo timidamente il progetto. Parallelamente in Inghilterra, Turing e il team di Bletchley Park costruirono Colossus per decrittare Enigma. Il primo computer americano, ENIAC, arrivò solo nel 1945."),
    _f("Guerre", "Guerra fredda",
       "Fu a un passo dalla guerra nucleare 3 volte",
       "Crisi di Cuba (1962), allarme falso nel 1983 (Petrov), Able Archer 83: tre momenti in cui l'estinzione fu questione di minuti.",
       "Stanislav Petrov, ufficiale sovietico, il 26 settembre 1983 ricevette l'allarme di 5 missili intercontinentali americani in arrivo. Aveva pochi minuti per lanciare la rappresaglia. Scelse di non farlo, intuendo il falso allarme (era un riflesso solare sui satelliti). Salvò letteralmente il mondo. Durante Able Archer 83, esercitazione NATO, i sovietici la credettero preludio di un attacco reale e mobilitarono armi nucleari. Durante la Crisi di Cuba, il sottomarino sovietico B-59 stava per lanciare un siluro nucleare, fermato solo dal rifiuto del commissario Vasili Arkhipov. Petrov morì nel 2017 senza aver ricevuto riconoscimenti ufficiali in Russia.",
       [{"title": "Wikipedia - Stanislav Petrov", "url": "https://it.wikipedia.org/wiki/Stanislav_Petrov"}]),
    _f("Guerre", "Guerre napoleoniche",
       "Napoleone perse in Russia per il freddo... ma anche per i bottoni",
       "I bottoni delle divise francesi erano di stagno. A -30°C lo stagno si sbriciola (peste stagnina). I soldati rimasero letteralmente senza vestiti.",
       "La 'peste stagnina' è una trasformazione allotropica dello stagno: sotto i 13°C cambia struttura cristallina e diventa fragile come polvere. A -30°C dell'inverno russo 1812, i bottoni delle Grande Armée francese si disintegrarono, lasciando migliaia di soldati senza divise. Su 600.000 invasori, solo 40.000 tornarono vivi. La teoria dei bottoni è affascinante ma controversa: alcuni storici la ridimensionano rispetto alla logistica, fame e guerriglia russa. Questo episodio ispirò il libro 'I bottoni di Napoleone' (Le Couteur/Burreson) sulla chimica che ha cambiato la storia."),

    # ============ MOTORI ============
    _f("Motori", "Formula 1",
       "Ferrari ha vinto più GP di chiunque altro: 248 in 75 anni",
       "La Scuderia Ferrari detiene quasi tutti i record F1: più costruttori (16), più piloti (15), più pole position (252), più podi (817).",
       "Fondata nel 1929 a Modena da Enzo Ferrari come Scuderia Ferrari (correva per Alfa Romeo), divenne costruttore indipendente nel 1947. Unica squadra ad aver partecipato a TUTTI i campionati F1 dal 1950. Il Cavallino Rampante fu donato da Francesca Baracca, madre dell'asso italiano morto in WWI. Le vittorie più iconiche: Lauda 1977, Schumacher 2000-2004 (5 titoli consecutivi), Leclerc 2019 Monza (prima Ferrari a Monza da 9 anni). Il budget attuale F1 è capped a 135 milioni $/anno (Ferrari spendeva 500M prima delle regole).",
       [{"title": "F1 Official Records", "url": "https://www.formula1.com/en/latest/article.f1-records-wins-poles-podiums.html"}]),
    _f("Motori", "MotoGP",
       "Valentino Rossi ha vinto 9 titoli in 3 diverse categorie",
       "125cc (1997), 250cc (1999), 500cc (2001), MotoGP (2002-2005, 2008-2009). Totale: 9 titoli mondiali in 26 anni di carriera.",
       "Valentino Rossi, il Dottore, ha rivoluzionato il motomondiale portando lo spettacolo mediatico a livelli mai visti. Ha vinto con 3 costruttori diversi (Aprilia, Honda, Yamaha). La sua rivalità con Marc Márquez a Sepang 2015 è entrata nella storia. È il pilota con più podi nella storia della MotoGP (199). Ha creato l'Accademy a Tavullia (VR46 Riders Academy) formando Morbidelli, Bagnaia, Bezzecchi. Il suo casco è cambiato 98 volte in carriera, ciascuno con design diverso. Si è ritirato nel 2021 all'età di 42 anni, correndo ora in GT e Endurance."),
    _f("Motori", "Rally",
       "Il Rally di Monte Carlo esiste dal 1911",
       "È il rally più antico del mondo: la prima edizione partì contemporaneamente da 14 città europee convergendo su Monte Carlo.",
       "Creato dal principe Alberto I per rilanciare il turismo invernale di Monte Carlo, il rally combinò sfida tecnica e prestigio. Nei primi decenni i partecipanti dovevano fare migliaia di km da Berlino, Stoccolma, Glasgow. Le tappe alpine (Col de Turini, Stelvio) sono leggendarie. Nel 1966 l'edizione fu vinta prima da Mini e poi squalificata per fari 'illegali': ancora oggi contesa. Dal 1973 è parte del WRC. Sebastien Loeb (7 vittorie) e Ogier (9 vittorie) sono i piloti più vincenti. Il rally moderno usa pneumatici chiodati per gelo improvviso."),

    # ============ MACCHINE ============
    _f("Macchine", "Ferrari",
       "La prima Ferrari stradale nacque quasi per caso",
       "Enzo Ferrari odiava le auto stradali. Costruì la 166 Inter (1948) solo per finanziare le gare. Oggi vale milioni.",
       "Enzo Ferrari diceva: 'Costruisco auto per vincere, non per essere comode'. La 166 Inter fu il primo modello stradale Ferrari, progettato perché i ricchi clienti chiedevano versioni 'civili' delle racing. Prodotta in soli 38 esemplari, ha motore V12 di 1995cc (ecco il '166', che sta per la cilindrata per cilindro). Una 166 MM Barchetta vale oggi oltre 5 milioni di euro. Ferrari oggi produce circa 13.000 auto l'anno intenzionalmente meno della domanda, per mantenere esclusività. Unica azienda al mondo che ferma produzioni per evitare di vendere troppo."),
    _f("Macchine", "Lamborghini",
       "Lamborghini nacque per ripicca contro Ferrari",
       "Ferruccio Lamborghini reclamò a Ferrari per una frizione difettosa. Enzo lo liquidò dicendogli: 'Pensa a fare trattori'. Lui iniziò a fare supercar.",
       "Ferruccio Lamborghini era già un miliardario grazie ai trattori Lamborghini (ancora oggi tra i leader mondiali). Appassionato di auto sportive, comprò una Ferrari 250 GT che aveva problemi di frizione. Andò di persona a Maranello a lamentarsi. Enzo Ferrari gli disse sprezzantemente: 'Tornatene a fare trattori'. Ferruccio, offeso, fondò Automobili Lamborghini nel 1963. La prima 350 GT sfidò direttamente le Ferrari. La Miura (1966) creò il genere 'supercar'. Oggi Lamborghini è del Gruppo Volkswagen. Il logo toro rappresenta Ferruccio (segno Toro) e la sua passione per le corride."),
    _f("Macchine", "Tesla",
       "La Tesla Roadster inviata nello spazio è ancora in viaggio",
       "Nel 2018 SpaceX lanciò una Tesla Roadster con 'Starman' al volante verso Marte. Ha già superato l'orbita di Marte.",
       "Elon Musk inviò la sua Tesla Roadster rossa personale come carico del primo lancio del Falcon Heavy (6 febbraio 2018). A bordo: un manichino chiamato 'Starman' in tuta SpaceX, il cruscotto con scritto 'Don't Panic' (omaggio a Guida Galattica), una copia della trilogia di Asimov in memoria di silicio. L'orbita è eliocentrica: passa vicino a Marte e alla Terra in cicli lunghi. Nel 2025 si stima abbia percorso oltre 4 miliardi di km. Musk sostiene che se ci fossero alieni evoluti, potrebbero già pensare che la Terra esporti 'automobili spaziali'."),
    _f("Macchine", "Fiat",
       "La 500 originale fu progettata per stare in un ascensore",
       "Dante Giacosa nel 1957 la disegnò piccola abbastanza (3m) da entrare in un ascensore di palazzo italiano, per risolvere il problema del parcheggio.",
       "La Fiat Nuova 500 (1957) aveva motore bicilindrico raffreddato ad aria montato posteriormente, 13 CV, 85 km/h. Costava 490.000 lire (~9 mesi di stipendio operaio). In 18 anni ne furono vendute 3,8 milioni. Progettata come 'utilitaria' per motorizzare l'Italia post-bellica. Giacosa progettò anche Topolino, 600 e 127. La nuova 500 del 2007 è un restyling nostalgico, prodotta anche elettrica (500e). La Topolino del 2023 è elettrica, 45 km/h, guidabile senza patente dai 14 anni. In Italia ne sono state vendute 12.000 nel primo anno."),

    # ============ MOTO ============
    _f("Moto", "Ducati",
       "Ducati ha vinto la MotoGP con piloti italiani dopo 16 anni",
       "Francesco Bagnaia ha conquistato il titolo 2022: primo italiano campione con Ducati da Gilera/Agostini degli anni '60.",
       "Fondata a Bologna nel 1926 dai fratelli Ducati come società per condensatori radiofonici, divenne produttrice di moto nel 1946 con il 'Cucciolo' (motorino per bicicletta). La prima moto vera fu la 98 Sport del 1948. Il motore desmodromico (valvole controllate meccanicamente senza molle) inventato da Fabio Taglioni nel 1956 è ancora distintivo Ducati. Oggi è del Gruppo Audi/VW. Nel 2023 Ducati è stato vice-campione dominante in MotoGP con Bagnaia (bis) e Martin. Il nuovo motore V4 Granturismo ha performance superiori ai rivali giapponesi."),
    _f("Moto", "Harley-Davidson",
       "Harley-Davidson è nata in una baracca del giardino",
       "William Harley e Arthur Davidson costruirono la prima moto nel 1903 in una baracca di legno 3x5 metri a Milwaukee.",
       "Oggi un'icona americana, nacque come hobby di due giovani: Harley (21 anni) e Davidson (20). La prima moto aveva motore da 7 pollici cubi montato su una bicicletta. Nel 1907 fondarono la società. Durante la WWII produssero 90.000 moto militari (modello WLA). Negli anni '60 Harley-Davidson era quasi fallita: salvata dalla proprietà AMF nel 1969 con qualità in caduta ('the ruined era'). Ri-privatizzata nel 1981 in leveraged buyout iconico. Il rumore caratteristico del motore V-twin 45° è talmente distintivo che Harley tentò di brevettarlo nel 1994 (fallì). Il 'Potato Potato' è parte del DNA americano."),
    _f("Moto", "Vespa",
       "La Vespa è nata da un elicottero",
       "Corradino D'Ascanio, padre della Vespa (1946), era un ingegnere aeronautico. Odiava le moto tradizionali: voleva qualcosa di 'pulito e pratico'.",
       "Piaggio nel dopoguerra cercava un prodotto popolare. Enrico Piaggio chiese a D'Ascanio (costruttore del primo elicottero italiano) di progettare un mezzo a 2 ruote. D'Ascanio applicò principi aeronautici: carrozzeria portante monoscocca, motore laterale come i motori a elica, cambio al manubrio come i comandi elicottero. Piaggio la vide e disse: 'Sembra una vespa!' (per vita stretta). Nacque il nome. In 75 anni ne sono state vendute 19 milioni in 130 paesi. Simbolo di stile italiano, protagonista di 'Vacanze Romane' con Audrey Hepburn. Piazzale Piaggio a Pontedera, stabilimento storico, è ancora attivo."),
    _f("Moto", "MV Agusta",
       "MV Agusta ha dominato il motomondiale per 17 anni",
       "Dal 1952 al 1974 ha vinto 38 titoli mondiali costruttori (record assoluto) e 37 piloti. Giacomo Agostini ne vinse 13 con MV.",
       "Fondata nel 1945 a Schiranna (Varese) dal conte Domenico Agusta per riconvertire la fabbrica di aerei (MV = Meccanica Verghera) nel dopoguerra. Le moto erano capolavori artigianali: rosso e argento, dettagli estremi, prezzi proibitivi. Nel 1977 chiuse la partecipazione alle gare, nel 1980 la produzione. Rifondata da Castiglioni (Cagiva) nel 1992. Oggi è una delle moto più esclusive al mondo, prodotta in piccolissime serie. La F4 è considerata la moto più bella mai costruita (MoMA di New York). Attualmente Pierer Mobility (KTM) è azionista di maggioranza."),
]
