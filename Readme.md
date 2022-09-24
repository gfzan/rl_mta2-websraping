## Processo recupero dati annuali RL-MTA

### (analisi tempi di attesa ambulatoriali)



Dopo aver visto come si ottengono i dati relativi ai tempi di attesa da un database aziendale, come aggregarli, elaborarli e presentarli (relativamente all'acquisizione rispetto ad un giorno indice) in ottemperanza alle disposizioni Regionali vigenti in tema di <u>rilevazione dei Tempi di Attesa</u> ([DGR n_XI_1865 del 2019](./Doc/DGR%20n_XI_1865%20del%202019%20tempi%20d'attesa.pdf) e [Disciplinare Tecnico Ambulatoriale, Ricoveri e Radioterapia versione Aprile 2011](./Doc/RL-MTA_DisciplinareTecnicoAnno_2011.pdf)); vediamo ora come arricchire l'analisi recuperando i dati di più rilevazioni indice, in questo caso già elaborate rispetto ai dati grezzi aziendali, per poter costruire serie temporali.

Il primo passo ora è : trovare i dati!

Siccome le Aziende Sanitarie sono tenute a pubblicare tali dati sulla sezione "Amministrazione Trasparente" dei loro portali web, proviamo ad utilizzare un algoritmo di *WEBSCRAPING* che ci permetta di automatizzare il reperimento dei links dai quali scaricare tali dati.

Ci accorgeremo che non c'è uniformità nella fornitura di questi dati!



#### 1 - Start

Inizieremo semplicemente dall'URL di google maps dove abbiamo già applicato la query "asst Lombardia" ( https://www.google.it/maps/search/asst+Lombardia/@45.6801063,9.0172596,9z) che renderizza questa pagina:



![asstGoogleMaps](.\img\asstGoogleMaps.jpg)



Analizzando tutti i link presenti in questa pagina, della quale dobbiamo fare prima uno scrolling completo, registriamo alcune informazioni tra cui i links ai portali web aziendali che memorizziamo in un foglio elettronico (tabella).

Otterremo ciò con una semplice classe in PYHTON qui schematizzata:

![classAsstUrlRetrieve](.\img\classAsstUrlRetrieve.jpg)

che con un paio di semplici funzioni permette di recuperare gli URLs e di memorizzarli su PC.

I parametri forniti in ingresso, nella costruzione della classe sono l'url di google maps visto prima e il percorso del driver (in questo caso di google chrome) essenziale per il parsing/scraping delle pagine web.



#### 2 - Individuazione dei links dove sono memorizzati i dati

Per ogni singola ASST, di cui abbiamo già memorizzato il riferimento alla home page, navighiamo attraverso il relativo portale per giungere alla landing page dove sono reperibili i file dati.

Memorizziamo l'url della pagina da cui si possono scaricare i file con i dati relativi alle rilevazioni dei giorni indice, solitamente mensili, dei tempi di attesa. Noteremo che non c'è uniformità nella gestione di questa attività da parte delle varie aziende, per cui troveremo dati di diverse annualità e memorizzati in modalità/formati differenti.

Per questa fase utilizziamo una seconda classe così composta.

![classAsstGoogleMapScraper](.\img\classAsstGoogleMapScraper.jpg)

che dapprima carica la lista dei links trovati al passo precedente per l'accesso ai portali aziendali, utilizza delle stringhe per le interrogazioni sui TAG delle pagine web, utilizza strutture dati per la memorizzazione di tutte le liste di link trovati per poi giungere all'unico link a noi utile e salvarlo nuovamente in formato tabellare.



#### 3 - Struttura del Processo

Il seguente diagramma illustra la struttura (file system) del processo.

![albero](.\img\albero.jpg)

1. nella cartella `./DATA` sono contenti i file con i dati di alcune aziende sanitarie, ho scaricato solo quelli in formato tabellare e non PDF, per pigrizia più che altro. Un passaggio seguente sarebbe di integrare l'algoritmo con la verifica e lo scarico in automatico di tutti i file dati, di tutte le aziende;
2. nella cartella `./DRIVER` sono contenuti i file con i driver per lo scraping su diversi browsers;
3. nella cartella `./img` sono contenuti alcuni file immagine inseriti in questa relazione;
4. nella cartella `./XLS` c'è l'unico file tabellare con la memorizzazione dei links utilizzati per lo scraping;
5. infine gli ultimi 2 file nella `directory principale` sono il file `ASST_scrapy.py` che contiene il codice utile per tutto il processo ed il file `ASST_scraping.ipynb` che può essere eseguito in un `NOTEBOOK` di `JUPYTER` ed aiuta i visualizzare i vari passaggi ed eventualmente  a interagire sull'analisi da effettuare.



#### 4 - Note conclusive

Il file di scripting con estensione *.py è stato scritto con tutti i parametri inseriti, basta lanciarlo ed aspettare (almeno 1/2 oretta, circa, a seconda della tecnologia a disposizione). 

Vengono trovati un'ottantina di siti da parsare ed infine una trentina di siti che contengono riferimenti alle liste di attesa. Tra questi vi sono i portali delle ATS che in realtà non trattano questi dati e sono siti solamente informativi.

Qualora tutti questi portali/siti dovessero subire restyling potrebbero non essere più raggiunti e bisognerebbe rimettere mano ai parametri dell'algoritmo.

Piccola nota tecnica interessante, nella classe "*AsstGoogleMapScraper*" viene <u>utilizzata una funzione in modo ricorsivo</u>, questa è una alternativa molto efficiente per trattare strutture dati ma può rivelarsi foriera di grossi grattacapi per il rischio di inserire cicli infiniti nella procedura!