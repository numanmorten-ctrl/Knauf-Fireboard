# Knauf Fireboard – Funktionel kravspecifikation

**Version:** 1.0  
**Status:** Til gennemgang – Knauf Digital  
**Dato:** 4. november 2026  
**Overdragelse af prototype:** Knauf Digital modtager en ZIP-kopi af prototypens kildekode, herunder de data, test og dokumenter, der henvises til.  
**Formål:** Funktionelle krav til produktionsapplikationen; egnet til tilpasning til Confluence.

**Dokumentnavigation**

1. [Indledning og formål](#1-indledning-og-formål)
2. [Omfang og målgrupper](#2-omfang-og-målgrupper)
3. [Brugerens arbejdsgang](#3-brugerens-arbejdsgang)
4. [Funktionelle krav](#4-funktionelle-krav)
5. [Krav til projekthåndtering](#5-krav-til-projekthåndtering)
6. [Materiale- og miljøkrav](#6-materiale--og-miljøkrav)
7. [Krav til rapporter og eksport](#7-krav-til-rapporter-og-eksport)
8. [Sprogtilpasning og brugeroplevelse](#8-sprogtilpasning-og-brugeroplevelse)
9. [Beregnings- og datakrav](#9-beregnings--og-datakrav)
10. [Acceptkriterier](#10-acceptkriterier)
11. [Prototypen som reference og kendte begrænsninger](#11-prototypen-som-reference-og-kendte-begrænsninger)
12. [Åbne spørgsmål og forudsætninger](#12-åbne-spørgsmål-og-forudsætninger)

## 1. Indledning og formål

### Resumé

Fireboard bestemmer den nødvendige brandbeskyttelsestykkelse for understøttede stålprofiler og leverer vejledende materialeoverslag og projektdokumentation. Den eksisterende prototype er den funktionelle reference for produktionsapplikationen, herunder dens beregningsdata, understøttede konfigurationer og demonstrerede arbejdsgange.

Produktionsapplikationen skal understøtte standardprofiler og brugerdefinerede profiler, beregningsforløbet i fire trin, projektredigering og lokal lagring/genåbning, materiale- og miljøoplysninger, dansk/engelsk visning samt de godkendte eksporter til PDF, Excel, ZIP og redigerbare projektfiler. Denne specifikation adskiller kravene fra prototypens begrænsninger og fastlægger acceptkriterier og udestående beslutninger til den formelle overdragelsesgennemgang via Confluence. Knauf Digital har ansvaret for valg og implementering af produktionsteknologi, arkitektur og driftsforhold; prototypens teknologi er ikke foreskrevet.

Fireboard understøtter valg af tykkelsen af Knauf Fireboard til brandbeskyttelse af stålprofiler. Applikationen kombinerer profiloplysninger og brandtekniske inddata med beregningsdata og leverer dimensioneringsresultater, vejledende materialeforbrug, miljøoplysninger om produkter og projektdokumentation.

Denne specifikation beskriver **hvad produktionsapplikationen skal kunne**. Den eksisterende applikation er en funktionel prototype og referenceimplementering. Dens applikationsramme, programmeringssprog, filstruktur og driftsmodel er ikke teknologikrav til produktionsløsningen. Knauf Digital fastlægger produktionsteknologi, arkitektur, hosting, sikkerhed, idriftsættelse og driftsforhold.

Kravene bygger på de beslutninger om funktionalitet og produktomfang, som Knauf Commercial / den udpegede produktejer har leveret, den eksisterende [funktionelle beskrivelse af den implementerede løsning](functional-specification.md) samt kildekoden, dataene og testene i den prototype-ZIP, som leveres til Knauf Digital. Godkendelse af det funktionelle omfang udgør ikke en ingeniørfaglig, myndighedsmæssig eller miljøfaglig godkendelse; de relevante ansvarskategorier er adskilt i afsnit 12. Beskrivelsen af den implementerede løsning vedrører en tidligere referenceversion og er ikke ændret. Hvor den afviger fra den aktuelle kode eller de godkendte beslutninger, angiver dette dokument forskellen frem for at videreføre forældede udsagn til kravene til den fremtidige løsning.

### 1.1 Konventioner for krav

| Præfiks | Betydning |
| --- | --- |
| FR | Funktionalitet, projekthåndtering samt materiale- og miljøfunktioner |
| DR | Beregnings- og datakrav |
| UX | Krav til brugerinteraktion og sprogtilpasning |
| EX | Krav til rapporter og eksport |

Hvert nummereret krav indeholder en kravformulering, prioritet, verificerbare acceptkriterier og aktuel prototypestatus. **Skal** angiver nødvendig funktionalitet, som Knauf Commercial / den udpegede produktejer har godkendt inden for produktomfanget, hvor den eksisterende referenceadfærd bruges til at gøre funktionaliteten testbar. Denne gennemgangsversion indfører ikke spekulative funktioner som Bør- eller Kan-krav. Ikke-godkendte udvidelser og uafklarede principper fremgår af afsnit 12 uden kravprioriteter.

Prototypestatus har følgende betydning:

- **Implementeret:** Den relevante adfærd findes i den gennemgåede kode; dette er ikke en erklæring om produktionsaccept eller uafhængig ingeniørfaglig verifikation.
- **Delvist implementeret:** En del af adfærden findes, men en konstateret mangel forhindrer fuld opfyldelse af kravet.
- **Mangler:** Den godkendte adfærd for den fremtidige løsning er ikke implementeret.
- **Ufuldstændig dokumentation:** Kildematerialet kan ikke dokumentere opfyldelsen, eksempelvis hvilke livscyklusmoduler de enkelte miljøfaktorer dækker.

### 1.2 Betydningen af beregninger og metadata

En **aktuel beregning** er den beregning, der indtastes eller redigeres. En **gemt beregning** er en post, der udtrykkeligt er tilføjet eller opdateret i et projekt. Et **gemt materialeresultat** er det materialeresultat, der lagres ved denne Tilføj/Opdater-handling. Lagring af en projektfil bevarer projektet; det svarer ikke til at opdatere dets beregninger.

Det senest indtastede projektnavn, forfatternavn, firmanavn og beskrivelsesfelt skal registreres som en del af handlingen til download af en rapport, uden at de enkelte felter skal anvendes særskilt. Dette opdaterer ikke ubemærket gemte dimensioneringsresultater eller gemte materialeresultater. Individuelle eksporter vedrører den aktuelle gyldige beregning; projekteksporter vedrører de udtrykkeligt gemte beregninger. Afsnit 12 angiver behovet for at bekræfte denne fortolkning af »senest bekræftede beregning« ved den formelle gennemgang.

## 2. Omfang og målgrupper

Applikationen understøtter personer, som specificerer, gennemgår eller estimerer Fireboard-beskyttelse af stålelementer, herunder projekterende, rådgivende ingeniører, tekniske rådgivere og kalkulationsmedarbejdere. Dette er tilsigtede anvendelser, ikke foreskrevne kontoroller eller adgangsrettigheder. Formelle målgruppebegrænsninger skal fortsat bekræftes af Knauf Commercial / den udpegede produktejer; formuleringer om ingeniørfagligt ansvar kræver input fra den relevante tekniske/F&U-ansvarlige hos Knauf.

Det funktionelle omfang omfatter:

- Standardprofiler og brugerdefinerede profiler, understøttede inddækningsløsninger og tabelbaseret bestemmelse af tykkelse.
- Vejledende materialemængder, længde og spildtillæg, alternative godkendte lagopbygninger, CO₂-oplysninger og links til produktdokumenter.
- Projekter med flere beregninger, udtrykkelig opdatering af beregninger samt lokal lagring og genåbning af projektfiler.
- Individuelle rapporter og projektrapporter, materialearbejdsbøger og dokumentationspakker.
- Dansk og engelsk visning.

Applikationen bestemmer ikke bæreevne, laster eller den dimensionerende ståltemperatur. Temperaturen leveres af den konstruktionsprojekterende eller den ansvarlige rådgivende ingeniør, typisk via stålproducentens tegninger eller tilhørende projekteringsdokumentation. Applikationen verificerer ikke den ingeniørfaglige egnethed af denne eksternt leverede temperatur.

Kravene godkender ikke generel geometrimodellering, materialeestimering for brugerdefinerede profiler, automatisk tilskærings- eller pakkeoptimering, indkøb, prissætning, lagerstyring eller bestilling hos leverandører. Disse funktioner findes ikke i prototypen og er ikke godkendte tilføjelser. Brugerkonti, projektlagring på server og samarbejdsfunktioner er hverken angivet som påkrævede eller forbudte produktionsfunktioner; beslutninger om sådanne tjenester hører til det efterfølgende produktmæssige og tekniske omfang, der aftales med Knauf Digital.

Et beregningsresultat er ikke en certificering, myndighedsgodkendelse eller uafhængig ingeniørfaglig verifikation. Miljøoplysningerne udgør ikke en fuldstændig livscyklusvurdering af en bygning. Henvisninger til BR18 beskriver den anvendte metode, der er godkendt for dette produktomfang, og er ikke en garanti for overholdelse af lovgivningen.

## 3. Brugerens arbejdsgang

| Trin | Brugeraktivitet | Funktionelt resultat |
| --- | --- | --- |
| Profil | Vælg en standardkategori og -størrelse, eller definer en brugerdefineret profil og dens metode til indtastning af Ap/V. | Profilidentitet og grundlag for profilforholdet. |
| Inddækning | Vælg inddækningsmetode og antal beskyttede sider. | En understøttet beskyttelsesløsning og, hvor relevant, færdigberegnet geometribaseret Ap/V. |
| Brandkrav | Vælg R30, R60, R90 eller R120, og indtast den eksternt fastlagte dimensionerende ståltemperatur. | Inddata til de relevante tykkelsesdata. |
| Resultat | Gennemgå Ap/V og tykkelse, projektoplysninger og relevante materialeresultater; tilføj/opdater en beregning eller eksporter. | Et gyldigt beregningsresultat og de tilladte projekt-/eksporthandlinger. |

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| UX-001 | Tilbyd et beregningsforløb i fire trin: Profil, Inddækning, Brandkrav og Resultat, med forståelig navigation og validering af inddata. | Skal | Brugere kan bevæge sig mellem de fire trin uden at miste relevante inddata. Åbning af Resultat med ufuldstændige eller ikke-understøttede inddata giver en handlingsanvisende forklaring og viser ikke en ugyldig tykkelse som et gyldigt resultat. | Arbejdsgang og kontroller er implementeret; nogle valideringsmeddelelser er kun delvist sprogtilpasset. |

Tilbagevenden til et tidligere trin gør det muligt at gennemgå og redigere. Produktionsapplikationen behøver ikke gengive prototypens præcise navigationselementer eller sideopbygning. Enhver ændret indtastet værdi skal afspejles i den aktuelle beregning, før resultatet vises eller eksporteres som aktuelt.

## 4. Funktionelle krav

### 4.1 Profiler og branddimensionering

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| FR-001 | Gør det muligt at vælge standardstålprofiler fra det leverede kategorispecifikke katalog. | Skal | Kataloget omfatter H-profiler (HEA/HEB/HEM), I-profiler (IPE/INP), U-profiler (UNP), varm- og koldvalsede kvadratiske og rektangulære hulprofiler samt middelsvære og svære cirkulære hulprofiler. Den valgte kategori og størrelse kan skelnes fra hinanden gennem hele beregningen og rapporteringen. | Implementeret. Katalogindholdet er datastyret; den gennemgåede referenceversion har 3.050 forskellige konfigurationer af kategori/profil/metode/sider. |
| FR-002 | Understøt navngivne brugerdefinerede profiler med direkte indtastet Ap/V. | Skal | En bruger kan navngive en brugerdefineret profil og indtaste et positivt Ap/V i m²/m³. Afrund værdien opad til nærmeste hele tal før opslag af tykkelsen; et resultat kræver, at den afrundede værdi højst er 380, og at der findes en gyldig tykkelse. Gemte brugerdefinerede navne og værdier kan gendannes. | Delvist implementeret: indtastning og gendannelse findes, men prototypen afskærer decimalerne i direkte indtastet Ap/V i stedet for at anvende den godkendte oprunding. |
| FR-003 | Understøt brugerdefinerede profiler, hvis Ap/V bestemmes ud fra referencegeometriens inddata. | Skal | Brugere kan indtaste a og b i mm samt stålarealet A i mm², vælge beskyttede sider, få beregnet Ap/V og se vejledning til indtastningskonventionen. Afrund positivt beregnet Ap/V opad til nærmeste hele tal før tykkelsesopslag, og anvend maksimumgrænsen på 380. Ugyldig eller ufuldstændig geometri må ikke give et gyldigt resultat. | Delvist implementeret: geometri og dansk/engelsk vejledning findes, men prototypen afrunder Ap/V til nærmeste hele tal frem for altid opad. Der er tale om en foreskrevet geometrikonvention, ikke modellering af vilkårlige former. |
| FR-004 | Understøt inddækning med klammer og inddækning med bjælke-/PHL-profiler med de tilladte kombinationer af beskyttede sider. | Skal | Den valgte metode og de valgte sider indgår i matchningen af beregningsdata. Ikke-understøttede kombinationer afvises. Ifølge de aktuelle data understøtter cirkulære standardprofiler klammeinddækning på fire sider; øvrige kategorier understøtter kun kombinationer, der faktisk findes i dataene. | Validering af opslag er implementeret. Nogle ikke-understøttede valgmuligheder er fortsat synlige frem til valideringen. |
| FR-005 | Understøt brandmodstandstiderne R30, R60, R90 og R120. | Skal | Hver brandmodstandstid vælger de tilhørende godkendte tykkelsesdata. Den valgte brandmodstandstid fremgår af resultater, gemte beregninger og beregningsrapporter. | Implementeret. |
| FR-006 | Modtag den dimensionerende ståltemperatur som en eksternt fastlagt ingeniørfaglig værdi, og forklar dens kilde og ansvarsplacering. | Skal | Brugere indtaster den temperatur, som den konstruktionsprojekterende eller ansvarlige rådgiver har leveret. Applikationen beregner den ikke og antyder ikke, at den har verificeret den konstruktive tilstrækkelighed. Værdierne skal være understøttet af beregningsdataene; den aktuelle reference accepterer hele grader fra og med 350 til og med 750 °C. | Delvist implementeret: indtastning og intervalvalidering findes; den fulde godkendte vejledning om ansvar er ikke indarbejdet i brugergrænsefladen. |
| FR-007 | Vis det beregnede Ap/V og den nødvendige samlede Fireboard-tykkelse for gyldige inddata. | Skal | Et understøttet tilfælde viser Ap/V i m²/m³ og tykkelse i mm sammen med de valgte dimensioneringsinddata. Ikke-understøttede eller ufuldstændige tilfælde får ikke et gyldigt tykkelsesresultat. En ændret indtastet værdi må ikke vises sammen med et uvedkommende tidligere resultat. | Dimensionering og resultatvisning er implementeret; nogle fejlmeddelelser er endnu ikke sprogtilpasset. |

### 4.2 Funktionel afgrænsning for brugerdefinerede profiler

Brugerdefinerede profiler understøtter tykkelsesberegninger, beregningsrapporter og lagring i projekter. Prototypen beregner ikke deres materialeforbrug eller materialerelaterede CO₂, heller ikke for geometribaserede brugerdefinerede profiler. Dette udkast godkender ikke en udvidelse til materialemængder for brugerdefinerede profiler. Eksporter skal angive, at mængder ikke er tilgængelige, frem for at antyde, at behovet er nul; se FR-020 og EX-004.

## 5. Krav til projekthåndtering

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| FR-008 | Vedligehold fælles projektmetadata bestående af projektnavn, udarbejdet af, firma og en beskrivelse over flere linjer. | Skal | Metadata kan redigeres, gemmes og genåbnes. Genererede beregningsrapporter anvender de projektoplysninger, der gælder for eksporthandlingen. Ingen brugerindtastet rapportdato tilsidesætter genereringsdatoen. | Delvist implementeret: felter og lagring findes; der er konstateret en mangel ved synkronisering under direkte download. Det overflødige datofelt er fjernet. |
| FR-009 | Gør det muligt for et projekt at indeholde flere uafhængige beregninger, hvor én beregning kan dokumentere flere profiler under identiske dimensioneringsforhold. | Skal | Tilføjelse af en ny gyldig beregning bevarer eksisterende poster og deres gemte materialeresultater. Standardprofiler og brugerdefinerede profiler kan indgå sammen. Ti HEB100-profiler på hver 6 m med identisk kategori, størrelse, brandmodstandstid, dimensionerende ståltemperatur, inddækningsmetode og beskyttede sider kan anvende én beregning og en samlet længde til materialeestimering på 60 m. Der kræves ikke et særskilt felt til antal profiler eller dublerede beregninger i dette tilfælde. | Implementerede projektposter og længdebaserede overslag understøtter den godkendte fremgangsmåde. Prototypen forhindrer en nøjagtig gentagelse af den senest tilføjede beregning; der kræves ingen ny funktion til dublerede beregninger. |
| FR-010 | Gendan den valgte gemte beregning til gennemgang og redigering. | Skal | Valg af beregning A efter B gendanner A's kategori, profil/navn, metode, beskyttede sider, brandinddata og materialeindstillinger. Brugerdefinerede profiler gendanner deres Ap/V-metode og relevante direkte værdier eller geometriværdier. Andre gemte poster forbliver intakte. | Implementeret, herunder den rettede gendannelse af brugerdefinerede profiler. |
| FR-011 | Tilbyd en udtrykkelig handling, Opdater beregning, som erstatter den valgte gemte beregning og dens relevante gemte materialeresultat. | Skal | Opdatering af en eksisterende post ændrer denne post uden at øge antallet af beregninger i projektet. Dens gemte resultat og materialemængder svarer til de gennemgåede gyldige inddata. Andre beregninger er uændrede. | Implementeret med regressionstestdækning. |
| FR-012 | Tillad sletning af en valgt gemt beregning efter bekræftelse. | Skal | Bekræftelsen identificerer den tilsigtede sletning. Annullering efterlader projektet uændret; bekræftelse fjerner kun den pågældende post og dens bidrag til de samlede materialemængder. | Delvist implementeret: sletning og genberegning af summer findes; bekræftelse mangler. |
| FR-013 | Tilbyd Ny beregning som en uafhængig aktuel beregning uden at ændre gemte projektberegninger. | Skal | Efter Ny beregning overskriver redigering og tilføjelse af den nye beregning ikke en eksisterende post. Gemte beregninger og fælles projektmetadata forbliver intakte. | Uafhængighed er implementeret. Nogle brugerdefinerede inddata kan fortsat være synlige; denne prototypeadfærd er accepteret og er ikke en uafklaret fejl. Kravet pålægger ikke et fuldstændigt tomt beregningsudkast. |
| FR-014 | Tilbyd Nyt projekt til at rydde det aktuelle projekt efter bekræftelse. | Skal | Annullering bevarer aktuelle projektoplysninger og beregninger. Bekræftelse rydder projektberegninger og metadata og nulstiller det aktuelle beregningsforløb til dets udgangstilstand. Tidligere downloadede lokale filer påvirkes ikke. | Delvist implementeret: rydning/nulstilling findes, men prototypen udfører handlingen uden bekræftelse. |
| FR-015 | Gør det muligt at gemme projekter lokalt og genåbne dem med forståelig håndtering af inkompatible eller ugyldige filer. | Skal | En understøttet projektfil bevarer projektmetadata, flere beregninger og gemte materialeresultater ved lagring og genåbning. En ugyldig fil udløser en forklaring frem for at blive accepteret som et gyldigt projekt. Eksisterende understøttede `.fireboard`-filer indgår i accept af kompatibilitet. | Lokal lagring/åbning i version 1 og strukturvalidering er implementeret. Produktionskompatibilitet ud over det leverede filsæt behandles i OQ-05. |
| FR-016 | Bevar tidligere gemte resultater ved åbning uden automatisk genberegning på grundlag af nyere data. | Skal | Åbning af en ældre understøttet fil bevarer dens gemte Ap/V, tykkelse og materialemængder. Brugere skal vælge, gennemgå og udtrykkeligt opdatere en post for at anvende aktuelle data. Uændrede poster forbliver uændrede. | Bevaring er implementeret. Identifikation af datarevisioner og vejledning om historiske filer er begrænset. |
| FR-017 | Bevar hver beregnings relevante materialeindstillinger under navigation og skift mellem beregninger. | Skal | Profillængde, spildprocent og gyldig valgt lagopbygning gendannes for den valgte beregning. Navigation væk og tilbage må ikke ubemærket kassere disse indstillinger eller kopiere en anden beregnings indstillinger. | Implementeret. Bevarede indstillinger og gemte mængder kan være forskellige indtil Opdater beregning. |

Historiske dimensioneringsresultater må ikke ubemærket »rettes«, blot fordi et gammelt projekt genåbnes eller dets rapport downloades. Dette omfatter filer fra før rettelserne af kategorispecifikke opslag, klammekataloget eller den maksimale Ap/V-værdi. Brugeren skal udtrykkeligt gennemgå og opdatere de berørte beregninger; visning af og vejledning om historiske filer kræver beslutningerne i afsnit 12.

## 6. Materiale- og miljøkrav

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| FR-018 | Tilbyd de gyldige materialelagopbygninger for den nødvendige samlede Fireboard-tykkelse. | Skal | Kun varianter, som understøttes af de leverede lagregler, kan vælges. Ændring af en variant opdaterer relevante produkter og mængder uden at ændre den nødvendige samlede tykkelse. En tidligere valgt variant bevares kun, hvis den fortsat er gyldig. | Implementeret. |
| FR-019 | Understøt profillængde i meter og spildprocent som decimalværdier til materialeoverslag med standardværdier på 6,0 m og 10%. | Skal | Længden skal være større end 0 m; spildprocenten skal være mindst 0% uden en særskilt øvre spildgrænse. For flere profiler med identiske dimensioneringsforhold anvendes deres samlede længde. Begge inddata og enheder forbliver synlige og bevares med beregningen. Ugyldig indtastning giver en tydelig valideringsmeddelelse og bliver aldrig ubemærket til nul. | Delvist implementeret: indtastningsfelter, godkendte standardværdier og længdebaserede overslag findes, men prototypen håndhæver ikke konsekvent disse grænser eller afviser ugyldig tekst i stedet for at omdanne den til nul. |
| FR-020 | Opdater det aktuelle materialeresultat, når længde, spildprocent eller lagopbygning ændres, hvor materialeberegning understøttes. | Skal | Efter ændring af en gyldig indtastet værdi stemmer den aktuelle tabel, relevante CO₂-værdier og den individuelle materialeeksport overens med denne værdi. Ugyldig længde eller spildprocent forklares frem for at blive vist som et gyldigt overslag med nulmængder. For brugerdefinerede profiler uden materialeunderstøttelse angiver applikationen udtrykkeligt, at mængder og materialerelateret CO₂ ikke er tilgængelige. | Delvist implementeret: opdatering og udelukkelse af brugerdefinerede profiler findes; validering af længde/spild skal rettes. Noter i projektarbejdsbøger kan fortsat vise numeriske nulværdier som pladsholdere. |
| FR-021 | Opdater kun gemte materialeresultater i projektet gennem udtrykkelige handlinger til Tilføj/Opdater beregning. | Skal | For en gemt beregning på 6 m opdaterer ændring af den aktuelle længde til 12 m det aktuelle overslag, men lader det gemte materialeresultat på 6 m være uændret indtil Opdater beregning. Lagring/genåbning af projektet alene indsætter ikke mængderne for 12 m. | Implementeret. Forskellen skal kommunikeres tydeligere til brugeren. |
| FR-022 | Tilbyd samlede materialemængder ud fra gemte materialeresultater i projektet, og bevar en opdeling pr. beregning. | Skal | Samlede summer svarer til summen af de inkluderede gemte mængder for hvert materiale og hver enhed. Sletning/opdatering af en post ændrer kun dens bidrag. Et ikke-gemt aktuelt udkast medtages ikke ubemærket. | Summer og eksporter med opdeling er implementeret med begrænsninger vedrørende identitet/sprogtilpasning beskrevet i afsnit 11. |
| FR-023 | Skeln mellem faktiske materialer uafhængigt af oversatte beskrivelser og tilsigtet tomme viste artikelnumre. | Skal | Forskellige klammer på 50 mm og 64 mm holdes adskilt, selv når begge vises med tomme artikelnumre. Gentagne identiske klammer sammenlægges. Sprogskift må ikke ændre materialeidentitet eller fejlagtigt opdele/sammenlægge mængder. | Delvist implementeret: det rettede klammekatalog og sammenlægning i den aktuelle liste er dækket af test; samlede eksporter anvender fortsat viste beskrivelser som alternativ, når artikelnumre er tomme. |
| FR-024 | Beskriv materialeforbruget som vejledende frem for som en præcis indkøbsliste. | Skal | Brugere informeres om, at det faktiske forbrug afhænger af montage, tilskæringsmetoder, materialeudnyttelse og projektforhold. Rapporterede mængder vises ikke som optimerede pladeantal, handelslængder eller pakkebestillinger. | Delvist implementeret: overslag er implementeret; den fulde godkendte forklaring kræver indholdsgennemgang. Der findes ingen indkøbs-/tilskæringsoptimering. |
| FR-025 | Vis produktidentifikation, mængder, CO₂-oplysninger og tilgængelige links til dokumentation for relevante materialer. | Skal | Materialeresultater identificerer produkt, producent, tilgængelige artikel-/DB-numre, enhed, forbrug pr. længdeenhed og samlet mængde. Relevante numeriske CO₂-værdier angives i kg CO₂e; tilgængelige EPD- og databladlinks kan åbnes, og manglende links opfindes ikke. | Aktuelle tabeller og links er implementeret med forbehold for begrænsninger i sprogtilpasning og katalogkvalitet. |
| FR-026 | Vis materialerelateret CO₂ for livscyklusmodulerne A1–A3 og C3–C4 med de aftalte BR18-relaterede undtagelser for mindre komponenter. | Skal | Det angivne omfang identificerer A1–A3 og C3–C4. Relevante skruer, klammer, fugestrimmel og andre specifikt undtagne mindre komponenter markeres som udeladt og tilfører ikke et numerisk bidrag. Medtagelse/udeladelse følger den godkendte produktklassificering, ikke en generel antagelse om alle mindre produkter. | Delvist implementeret / ufuldstændig dokumentation: faktorbaseret CO₂ og `IGNORE`-undtagelser findes; kildematerialet alene dokumenterer ikke hver faktors livscyklusdækning eller det fulde metodegrundlag. |

De aktuelle lagdata indeholder følgende referencelagopbygninger. Dette er dataindhold, ikke et krav om at hardkode valgmulighederne i den fremtidige applikation.

| Samlet tykkelse | Understøttede referencelagopbygninger |
| --- | --- |
| 15 mm | 15 mm |
| 20 mm | 20 mm |
| 25 mm | 25 mm |
| 30 mm | 30 mm; 15 + 15 mm |
| 35 mm | 20 + 15 mm |
| 40 mm | 20 + 20 mm |
| 45 mm | 25 + 20 mm; 30 + 15 mm |
| 50 mm | 25 + 25 mm; 30 + 20 mm |

Kataloget i den gennemgåede referenceversion indeholder 23 entydige artikelnumre. Artikel `90000005` er stålklammen på mindst 50 × 9 × 1,5 mm; `90000006` er klammen på mindst 64 × 9 × 1,5 mm. Førstnævnte vælges til relevante konstruktioner med 20 mm plader. Disse produkter er nyttige referencetilfælde ved accepttest af identitet og sammenlægning.

## 7. Krav til rapporter og eksport

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| EX-001 | Eksporter en individuel PDF med brandbeskyttelsesdimensionering for den aktuelle gyldige beregning, herunder brugerdefinerede profiler. | Skal | Rapporten identificerer projektmetadata, profilkategori/-navn, inddækningsmetode, beskyttede sider, brandmodstandstid, dimensionerende ståltemperatur, Ap/V og nødvendig Fireboard-tykkelse. Den kan genereres uden først at tilføje beregningen til projektet. Den indeholder ikke materialetabeller eller CO₂-opgørelser. | Godkendt rapportindhold er implementeret; senest indtastede metadata ved direkte download mangler. |
| EX-002 | Eksporter en samlet PDF med brandbeskyttelsesdimensionering for gemte projektberegninger. | Skal | Rapporten indeholder hver gemt beregning med dens lagrede dimensioneringsresultat, fælles projektmetadata og tydelig sidenummerering. Den udelader ikke-gemte udkast, materialetabeller og CO₂-opgørelser og genberegner ikke automatisk historiske resultater. | Én side pr. gemt beregning og godkendte indholdsgrænser er implementeret; metadatasynkronisering er delvist implementeret. |
| EX-003 | Eksporter den aktuelle understøttede vejledende materialeliste til Excel. | Skal | Arbejdsbogen indeholder produktidentifikation, producent, beskrivelse, forbrug pr. løbende meter, enhed og samlet mængde, som svarer til det aktuelle gyldige materialeresultat. Ikke-understøttede mængder for brugerdefinerede profiler opfindes ikke. Kolonner med CO₂, EPD- og databladlinks er udeladt. | Godkendte indholdsgrænser er implementeret; sprogtilpasning er fortsat delvis. |
| EX-004 | Eksporter samlede vejledende projektmaterialemængder og en materialeopdeling pr. beregning til Excel. | Skal | Bevar begge materialelistemuligheder. Begge visninger stemmer overens med gemte materialeresultater. Identiske produkter sammenlægges korrekt; forskellige produkter holdes adskilt. Mængder for brugerdefinerede profiler eller manglende gemte materialeresultater angives som utilgængelige, ikke som beregnet nul. Kolonner med CO₂, EPD- og databladlinks er udeladt. | Delvist implementeret: begge eksporter og godkendte indholdsgrænser findes; beskrivelsesbaseret gruppering, uoversatte noter og nulværdier som pladsholdere skal rettes. Prototypens kolonne med summeret forbrug pr. meter er ikke et meningsfuldt forbrugstal for projektet som helhed. |
| EX-005 | Eksporter en ZIP med projektdokumentation, der indeholder beregningsrapporten, relevante projektmaterialearbejdsbøger og tilgængelig supplerende dokumentation. | Skal | Pakken indeholder den samlede PDF, samlede materialearbejdsbøger og arbejdsbøger opdelt pr. beregning, hvor relevant, Fireboard-afsnit om projektering/montage samt relevante produkt-EPD'er/datablade. Den anvender samme gemte projektgrundlag som de tilsvarende selvstændige eksporter. Den redigerbare `.fireboard`-fil medtages ikke automatisk. | Godkendt pakkestruktur er implementeret; seneste metadata og sprogtilpasning er delvist implementeret. |
| EX-006 | Håndter utilgængelige eksterne dokumenter i pakken udtrykkeligt uden at give et misvisende indtryk af pakkens fuldstændighed. | Skal | Et mislykket eller tomt download af et eksternt dokument må ikke ubemærket fremstå som en vellykket medtagelse. Den genererede pakke identificerer udeladte dokumenter på det valgte applikationssprog. Gentagne produktdokumenthenvisninger skaber ikke unødvendige dubletter af samme dokumenttype. | README for oversprungne filer og fjernelse af dublerede URL'er er implementeret; nogle beskrivende filnavne og underliggende fejltekster er ikke fuldt sprogtilpasset. |
| EX-007 | Eksporter og genåbn redigerbare projektdata adskilt fra PDF-, Excel- og ZIP-dokumentation. | Skal | Projektfilen bevarer metadata, oplysninger om det aktuelle beregningsforløb, gemte beregninger, materialeindstillinger og gemte resultater, der er nødvendige for fortsat gennemgang. Lagring af filen genberegner ikke resultater og indebærer ikke, at en ZIP indeholder redigerbare projektdata. | `.fireboard`-formatet er implementeret; kompatibilitet og uafklarede identiteter i ældre filer behandles i OQ-05. |
| EX-008 | Vis PDF'ens genereringsdato i Europe/Copenhagen med formatet DD-MM-YYYY, ensartet i hele den genererede rapport. | Skal | Test generering omkring midnat UTC og begge overgange mellem sommer- og vintertid. Alle sider i en samlet rapport har den samme registrerede dato. Senere download af en uændret, tidligere genereret/cachelagret fil bevarer dens oprindelige genereringsdato. | Implementeret og dækket af automatiserede test. Tilgængeligheden af tidszonedata i det aktive driftsmiljø er ikke direkte verificeret. |
| EX-009 | Ombryd projektbeskrivelser inden for det godkendte aktuelle PDF-layout med højst to linjer og synlige udeladelsesprikker ved overløb. | Skal | Kort tekst bevarer sin fastlagte placering. Længere tekst ombrydes efter den viste bredde; udtrykkelige linjeskift respekteres, hvor det er muligt; lange ord/URL'er overskrider ikke feltet. Overløb afsluttes med udeladelsesprikker, som er tilpasset den tilgængelige plads. Danske tegn og de bogstavelige tegn `<`, `>` og `&` bevares. Den fulde gemte beskrivelse er uændret. Gælder begge sprog og PDF-typer. | Fælles gengivelse og koordinatbaserede test mod begge skabeloner er implementeret. |
| EX-010 | Sørg for, at hver genereret eksport anvender et sammenhængende sæt beregnings-/materialeresultater og de projektmetadata, der er accepteret for den pågældende eksporthandling. | Skal | Individuelle output afspejler den aktuelle gyldige beregning; projektoutput afspejler udtrykkeligt gemte beregnings-/materialeresultater. Senest indtastede metadata medtages uden en særskilt Anvend-handling. En tidligere eksport må ikke leveres som aktuel efter relevante metadataændringer; uændrede historiske filer bevarer deres oprindelige bytes/dato. | Delvist implementeret: grænser mellem beregninger/gemte resultater og indholdsbaserede cacher findes, men første download kan indeholde forældede metadata. |

### 7.1 Eksisterende rapportdesign og indholdsafgrænsning

De eksisterende danske og engelske PDF-skabeloner fastlægger det godkendte beskrivelsesområde og de omgivende felter. Bevar det fastlagte udseende for korte beskrivelser, tilpas ombrudt tekst inden for området, og undgå overlap med tilstødende indhold. Referenceskabelonerne og layouttestene understøtter visuel accept uden at foreskrive et gengivelsesbibliotek eller en koordinatbaseret implementering.

Knauf Commercial / den udpegede produktejer har godkendt bevarelse af den eksisterende opdeling mellem eksporttyper og deres indhold som funktionelt omfang. Individuelle og samlede PDF'er dokumenterer brandbeskyttelsesdimensioneringen, mens individuelle, beregningsopdelte og samlede Excel-materialelister indeholder vejledende materialemængder. ZIP-filen samler beregningsdokumentation, materialelister og tilgængelig supplerende produktdokumentation; den separate `.fireboard`-fil bevarer redigerbare projektdata.

Beregnings-PDF'er indeholder ikke materialetabeller eller CO₂-opgørelser; prototypen udelader også længde-/spildfelter og geometrimål for brugerdefinerede profiler. Materialeeksporter til Excel udelader kolonner med CO₂, EPD- og databladlinks. ZIP-filen indeholder ikke automatisk en redigerbar `.fireboard`-fil og har aktuelt ingen separate PDF'er for individuelle beregninger. Denne specifikation godkender ingen yderligere eksporttyper eller indholdsudvidelser.

Den samlede arbejdsbog summerer aktuelt både forbrug pr. løbende meter og samlede mængder. Dette er prototypeadfærd: det summerede forbrugstal må ikke fortolkes som et meningsfuldt forbrug pr. meter for projektet som helhed. FR-022 kræver korrekte samlede mængder. Denne specifikation indfører ingen alternativ formel til sammenlægning af forbrugstal.

## 8. Sprogtilpasning og brugeroplevelse

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| UX-002 | Understøt dansk og engelsk for alt brugerrettet indhold, som applikationen styrer. | Skal | Sprogskift tilpasser betegnelser i beregningsforløbet, vejledning, validering, fejl, advarsler, bekræftelser, materialenoter, rapportbetegnelser og forklaringer i pakker, som applikationen selv danner. Indbyggede meddelelser fra applikationsrammen/systemet må forblive engelske, hvor de ligger uden for applikationens praktiske kontrol. | Delvist implementeret: hovedbetegnelser og PDF-skabeloner er tosprogede; flere validerings- og eksportmeddelelser er fortsat danske. |
| UX-003 | Brug det eksisterende katalogs værdier i BESKRIVELSE_DK og BESKRIVELSE_EN til materialebeskrivelser på det tilsvarende sprog uden at omskrive indholdet. | Skal | For et identificeret produkt bruger dansk dets DK-felt og engelsk dets EN-felt i relevante tabeller og eksporter. Applikationen oversætter ikke automatisk, udskifter ikke formuleringer i og forbedrer ikke ubemærket leverede beskrivelser. Et sprogskift bevarer identitet og mængder. | Ensartet brug mangler: aktuelle tabeller tager udgangspunkt i danske beskrivelser og anvender teksterstatninger; gemte resultater kan bevare tekst fra et tidligere sprog. Manglende oversættelser og katalogets sproglige kvalitet behandles i OQ-08. |
| UX-004 | Vis decimalværdier med dansk komma og engelsk punktum uden at ændre deres numeriske betydning. | Skal | Samme mængde vises eksempelvis som 12,50 på dansk og 12.50 på engelsk. Længde og spildprocent understøtter decimalindtastning. Numeriske rapporter/materialeeksporter stemmer overens på tværs af sprog. Sprogskift ændrer ikke beregnede værdier. | Delvist implementeret: materialeformatering bruger aktuelt komma på begge sprog. Accepterede indtastningsseparatorer og materiale-/CO₂-præcision behandles fortsat i OQ-09; oprunding af Ap/V samt grænser og standardværdier for længde/spild er godkendt. |
| UX-005 | Sprogtilpas Excel-arknavne og beskrivende rapport-/dokumentfilnavne, som applikationen styrer. | Skal | Engelske eksporter bruger engelske arknavne/beskrivende filnavne, og danske eksporter bruger danske ækvivalenter. Noter om brugerdefinerede profiler, som applikationen danner, følger det valgte sprog. Brugerindtastede dele af filnavne oversættes ikke automatisk. | Delvist implementeret: nogle titler og navne er sprogtilpasset; arknavne og flere produktdokumentfilnavne/noter er fortsat danske. |
| UX-006 | Bevar tekniske identifikatorer og brugerdefinerede navne ved sprogskift og genåbning af projekter. | Skal | Artikelnumre, materialekoder, interne nøgler og overskriften `SYSTEM` forbliver uændrede. Brugerindtastede eller tidligere gemte profilnavne og projekttekster oversættes ikke automatisk. Ændringer i viste betegnelser må ikke ændre matchningen af dimensioneringsdata. | Delvist implementeret: navne og primære tekniske identifikatorer bevares; ældre oversatte materialebeskrivelser indgår fortsat i visse grupperings-/opslagsforløb. |
| UX-007 | Registrer de senest indtastede projektmetadata som en del af downloadhandlingen uden Ctrl+Enter eller et unødvendigt Gem/Anvend-trin for hvert felt. | Skal | Mens fokus stadig er i en ændret beskrivelse over flere linjer, klikker brugeren direkte på Download beregning; den første downloadede PDF indeholder den senest indtastede værdi, kun begrænset af den godkendte synlige afkortning. Gentag for samlede PDF'er og rapporter i ZIP-filer, herunder eksisterende cachelagrede downloads og tømning af et felt. Der indføres ingen yderligere klargørings-/anvendelseshandling alene for at tilpasse sig prototypens applikationsramme. | Mangler: direkte downloads kan anvende tidligere genererede bytes. Projekteksporter i sidepanelet behandles også før den varige metadataopdatering i prototypen. |
| UX-008 | Kræv bekræftelse før sletning af en beregning eller rydning af projektet med Nyt projekt. | Skal | Bekræftelsen forklarer, hvilken beregning eller hvilket projekt der berøres. Annullering har ingen destruktiv virkning; bekræftelse udfører kun den angivne handling. | Mangler: begge handlinger udføres aktuelt straks. Dette er et godkendt krav til den fremtidige løsning, ikke en uafklaret produktbeslutning. |
| UX-009 | Gør forskellen mellem aktuelle redigeringer, gemte beregninger og gemte materialeresultater tydelig og forudsigelig. | Skal | Brugere kan identificere, hvilken beregning der redigeres, og om projektmængder kræver Opdater beregning. En opdatering tilføjer ikke uventet en post. Ny beregning ændrer ikke ubemærket en eksisterende gemt post. Registrering af metadata ved rapportgenerering forveksles ikke med opdatering af gemte materialemængder. | Delvist implementeret: tilføjelses-/opdateringstilstande og uafhængige beregninger findes; de gemte materialeresultaters aktualitet og eksporttidspunktet er utilstrækkeligt tydeliggjort. |
| UX-010 | Forklar ugyldige, ufuldstændige eller ikke-understøttede inddata på det valgte sprog uden at vise diagnosticering som almindelig brugervejledning. | Skal | Manglende dimensioneringsinddata, en ikke-understøttet konfiguration, oprundet Ap/V over 380 eller en utilgængelig tykkelse giver en handlingsanvisende sprogtilpasset meddelelse og intet gyldigt resultat for det pågældende tilfælde. Længde på eller under nul, negativ spildprocent og ugyldig numerisk indtastning giver tydelige valideringsmeddelelser; ugyldig indtastning bliver aldrig ubemærket til nul. Gyldig længde/spildprocent med decimaler og spild over 100% afvises ikke alene, fordi værdierne har decimaler eller overstiger 100%. Fejlfindingsdetaljer, som applikationen styrer, er ikke brugerens eneste forklaring. | Delvist implementeret: kontroller findes, men Ap/V-afrunding og validering af længde/spild opfylder ikke de godkendte regler; nogle meddelelser er hardkodet på dansk, og ét forløb for ikke-understøttede opslag viser fejlfindingsdetaljer. |

Eksterne EPD'er, datablade og tekniske dokumenter oversættes ikke automatisk. Deres originalsprog og indhold forbliver leverandørens. Dette adskiller sig fra sprogtilpasning af applikationens linktekster, forklarende noter og beskrivende downloadnavne.

Produktionskrav må ikke videreføre et krav om at trykke på en bestemt genvej i applikationsrammen, tilføje en Anvend-knap eller acceptere et andet downloadforsøg. UX-007 forbliver et krævet resultat, som Knauf Digital skal implementere med den valgte teknologi. Prototypens synkroniseringsbegrænsning ændrer ikke dette godkendte resultat.

## 9. Beregnings- og datakrav

| ID | Krav | Prioritet | Acceptkriterier | Aktuel prototypestatus |
| --- | --- | --- | --- | --- |
| DR-001 | Match Ap/V- og materialeforbrugsdata for standardprofiler ved at anvende kategori, profil, inddækningsmetode og beskyttede sider samlet. | Skal | Alle 3.050 referencekonfigurationer finder deres egne poster uafhængigt af rækkefølgen af kilderækker. Navnesammenfald på tværs af kategorier vælger aldrig en anden kategori. Manglende konfigurationer forbliver ikke-understøttede frem for at anvende et match uden kategori. | Rettelse og udtømmende referencetest er implementeret; der findes ingen dublerede firefeltsnøgler i referenceversionen. |
| DR-002 | Afrund alle positive Ap/V-værdier opad til nærmeste hele tal før tykkelsesopslag, og håndhæv et maksimum på 380 m²/m³ for alle standardberegninger, brugerdefinerede beregninger og understøttede brandmodstandstider. | Skal | Eksakte heltal forbliver uændrede. Verificer 125,0 → 125, 125,1 → 126, 125,7 → 126, 379,9 → 380, 380,0 → 380 og 380,1 → 381 → afvist. Test direkte værdier og geometriværdier for R30/R60/R90/R120 og begge sprog. Værdierne 379 og 380 kræver en gyldig tabelcelle; 381, 400 og 401 afvises. En tabelværdi over 380 kan ikke tilsidesætte maksimumgrænsen. | Delvist implementeret: heltalsmaksimum er implementeret, men afskæring af decimaler ved direkte indtastning og afrunding til nærmeste heltal ved geometri afviger fra den godkendte regel om oprunding. Standardkatalogets heltalsværdier ændres ikke ved oprunding. |
| DR-003 | Bestem kun tykkelse ud fra de relevante godkendte data for brandmodstandstid og understøttede kombinationer af oprundet Ap/V og temperatur. | Skal | Resultaterne svarer til referencetilfældene i afsnit 10. Manglende kombinationer eller tomme celler afvises, selv når oprundet Ap/V er på eller under 380. Anvend DR-002 før opslag; afrunding tillader ikke interpolation, ekstrapolation eller erstatningsværdier for manglende tykkelsesdata. | Delvist implementeret: præcist tabelopslag findes, men prototypens forudgående normalisering af Ap/V afviger fra DR-002. |
| DR-004 | Bevar de fysiske enheder og referencebetydningen af inddata for brugerdefineret Ap/V, og anvend godkendt oprunding på den resulterende værdi. | Skal | Direkte indtastning er i m²/m³. Geometriinddata er a/b i mm og A i mm². Ugyldig ikke-positiv eller ufuldstændig geometri giver intet resultat. Referenceeksempler for geometri gengiver den nedenfor beskrevne beregning af omkreds i forhold til areal og afrunder derefter det positive resultat opad efter DR-002 uden forudgående afrunding til nærmeste heltal eller afskæring af decimaler. | Delvist implementeret: den foreskrevne geometri er implementeret; dens afsluttende afrunding til nærmeste heltal skal ændres til oprunding i produktionsløsningen. Ingeniørfaglig bekræftelse af referencegeometriens vejledning behandles i OQ-04. |
| DR-005 | Bestem materialelagopbygninger og tilhørende produkter ud fra de relevante lag- og komponentregler. | Skal | Hver tilbudt variant summerer til den nødvendige tykkelse. Skruer/klammer findes ud fra det relevante pladelag/den relevante pladetykkelse; bjælke- og vinkelmaterialer følger de relevante profil-/sideregler. Ikke-understøttede kombinationer skaber ikke vilkårlige produkter. | Implementeret med data for lag, fastgørelse, vinkler og bjælkeprofiler. |
| DR-006 | Bevar referencens mængdegrundlag, herunder samlet profillængde, spild og gentagne lag. | Skal | For decimallængde L > 0 og decimalspildprocent w ≥ 0 giver et sammenlagt forbrug pr. meter r mængden r × L × (1 + w/100) i den relevante enhed uden særskilt øvre spildgrænse. L kan være den samlede længde af identiske profiler efter FR-009; ti elementer på 6 m bruger L = 60 m uden en særskilt antalsmultiplikator. Gentagne lag bidrager med deres fulde materialeforbrug. Efterbehandlingsprodukter bevarer deres referencearealgrundlag frem for uden videre at blive ganget med antallet af lag. | Delvist implementeret: mængdeformler for understøttede standardprofiler og estimering ud fra samlet længde findes, men inputvalideringen afviger fra FR-019. Visningspræcision for materialer/CO₂ behandles fortsat i OQ-09. |
| DR-007 | Anvend arealbaserede CO₂-faktorer for Fireboard på det fulde sammenlagte pladeareal inklusive spild. | Skal | For gentagne identiske Fireboard-lag omfatter både rapporteret areal og CO₂ alle lag. For en arealfaktor f og et sammenlagt areal Q inklusive spild er CO₂ lig med Q × f før afrunding til visning. Sammenlægning af identiske rækker må ikke fjerne deres udledninger. | Rettelse er implementeret med regressionstest af gentagne lag. |
| DR-008 | Anvend hvert produkts godkendte CO₂-beregningsgrundlag og undtagelser konsekvent. | Skal | Lineære produkter bruger den relevante samlede længdemængde; arealbaserede produkter bruger deres foreskrevne arealgrundlag; spartelmasse bevarer beregningen ud fra referenceareal. Udeladte produkter bidrager ikke med numerisk CO₂. Viste summer stemmer overens med de medtagne rækker efter den aftalte afrundingspolitik og faktorernes godkendte omfang A1–A3/C3–C4. | Delvist implementeret / ufuldstændig dokumentation: produktspecifikke beregningstyper og undtagelser findes; faktorgrundlag og præcisionspolitik kræver bekræftelse. |
| DR-009 | Sammenlæg materialer efter stabil faktisk identitet og kompatible enheder uafhængigt af visningssproget. | Skal | Sammenlægning af beregninger med samme produkt på dansk og engelsk bevarer den summerede mængde og relevante CO₂. De to klammeartikler holdes adskilt trods tomme viste numre. Omordning af data eller oversættelse af betegnelser ændrer ikke summer. | Delvist implementeret: fjernelse af dubletter i den aktuelle liste er dækket; brug af beskrivelser som alternativ identifikation i samlede eksporter og identitet i ældre gemte materialeresultater er fortsat mangler. |
| DR-010 | Bevar de logiske relationer mellem profildata, tykkelsesdata, komponentregler og produktkataloget. | Skal | Hvert understøttet standardopslag har en entydig firefeltsidentitet. Produkter, der refereres til i komponentregler, findes som det tilsigtede katalogprodukt. Datainkonsistenser løses ikke ved at vælge en vilkårlig modstridende post eller opfinde et dimensioneringsresultat. | Det aktuelle datasæt har 3.050 entydige konfigurationsnøgler, 23 entydige katalogartikler og rettede klammehenvisninger. Omfattende validering af dataudgivelser til produktionsløsningen er ikke etableret. |
| DR-011 | Anvend kun nyere beregningsdata på en gemt post efter brugerens udtrykkelige gennemgang og Opdater beregning. | Skal | Et ældre projekt åbner med sine oprindelige resultater. Gennemgang og opdatering af én valgt beregning anvender aktuelle relevante data og erstatter denne posts resultat/gemte materialeresultat; andre gemte poster forbliver uændrede. Eksport eller lagring af projektfilen alene genberegner den ikke. | Bevaring/opdatering er implementeret. Gemte filer indeholder ikke en identifikator for beregningsdataenes revision; dette udkast kræver ikke indførelse af en sådan. |

### 9.1 Ingeniørfaglige referencekonventioner

Geometrireferencen anvender den eksponerede omkreds P = a + 2b for én eller tre beskyttede sider, P = a + b for to sider og P = 2a + 2b for fire sider. Det uafrundede Ap/V er P × 1.000 / A. Disse konventioner kræver den tilhørende indtastningsvejledning; de må ikke fremstilles som en universel model for enhver stålprofilform. Bekræftelse af denne vejledning som del af de ingeniørfaglige referencedata behandles fortsat i OQ-04.

**Godkendt regel for produktionsløsningen:** Afrund alle positive Ap/V-værdier opad til nærmeste hele tal, mens eksakte heltal bevares uændrede. Ved geometri anvendes reglen på den uafrundede beregnede værdi; ved direkte indtastning anvendes den på den indtastede værdi. Valider det resulterende heltal mod maksimum på 380 før opslag af tykkelsen. Reglen gælder for R30, R60, R90 og R120 og ændrer ikke kategorispecifikt valg eller geometriformler. Dermed bliver 379,9 til 380 og kan få en tykkelse, hvis en gyldig celle findes, mens 380,1 bliver til 381 og afvises.

**Forskel i prototypen:** Den aktuelle kode afskærer decimaler i direkte indtastet Ap/V og afrunder geometriberegnet Ap/V til nærmeste heltal før kontrol af maksimumgrænsen. Den opfylder derfor endnu ikke den godkendte afrundingsregel for produktionsløsningen. Denne dokumentationsopdatering ændrer ikke koden.

Den aktuelle temperaturreference er 350–750 °C i hele grader. Fireboard-tykkelsesresultatet er en samlet tykkelse i mm; lagvalg er en efterfølgende handling til materialelagopbygning. Resultater uden for de understøttede data forbliver utilgængelige, selv hvis de ligger inden for et generelt indtastningsinterval.

For værdier over maksimumgrænsen er de godkendte meddelelser:

- Dansk: »Profilforholdet (Ap/V) overstiger 380 m²/m³, vælg et andet eller større profil«
- Engelsk: »The profile factor (Ap/V) exceeds 380 m²/m³. Select another or larger steel profile.«

### 9.2 Oversigt over referencedata

Disse filer identificerer det aktuelle referenceindhold. CSV-lagring og disse filnavne er ikke foreskrevet som produktionsløsningens dataarkitektur.

| Referencedata | Formål og relation |
| --- | --- |
| [apv.csv](../data/apv.csv) | Standardprofilkategorier/-navne, inddækning og sider, Ap/V samt forbrugstal for Fireboard-areal, bjælke-/PHL-profiler, vinkler, skruer og klammer. |
| [fireboard_30.csv](../data/fireboard_30.csv), [fireboard_60.csv](../data/fireboard_60.csv), [fireboard_90.csv](../data/fireboard_90.csv), [fireboard_120.csv](../data/fireboard_120.csv) | Tykkelsesværdier efter dimensionerende ståltemperatur og Ap/V for hver brandmodstandstid. Underliggende kolonner over 380 tillader ikke anvendelse af disse værdier. |
| [layer_logic.csv](../data/layer_logic.csv) | Gyldige lagtykkelser/-rækkefølger og lagopbygningsvarianter for en nødvendig samlet tykkelse. |
| [screw_clamp_logic.csv](../data/screw_clamp_logic.csv) | Regler for lag-/pladetykkelse med henvisning til skrue- og klammeprodukter i kataloget. |
| [angle_profile_logic.csv](../data/angle_profile_logic.csv) | Forbrug af vinkelprofiler knyttet til beskyttede sider. |
| [beam_profile_logic.csv](../data/beam_profile_logic.csv) | Profilafhængigt valg af bjælke-/PHL-produkt. |
| [materials.csv](../data/materials.csv) | Produktidentitet, producent, danske/engelske beskrivelser, CO₂-faktorer/-typer og eksterne dokumentlinks. Understøtter identifikation af produkter valgt efter komponentregler. |

Beregningsdata og brandbeskyttelsesforudsætninger kræver den relevante tekniske/F&U-ansvarlige hos Knauf; miljøfaktorer, livscyklusomfang og undtagelser kræver den relevante bæredygtigheds-/dataansvarlige hos Knauf. Formelle udpegninger af ansvarlige, vedligeholdelsesordninger og godkendelsesprocesser for dataudgivelser skal fortsat aftales ved overdragelsen. Funktionel accept aftales i fællesskab mellem Knauf Commercial og Knauf Digital og erstatter ikke disse datagodkendelser. At en værdi findes i en kildefil, er ikke i sig selv dokumentation for uafhængig ingeniørfaglig validering.

## 10. Acceptkriterier

Kriterierne i hver kravrække er normative for dette udkast. Følgende integrerede scenarier understøtter accept på tværs af beregninger, projekter, eksporter og sprog. Prototypens testresultater er understøttende dokumentation, ikke en erstatning for produktionsaccept i den teknologi, som Knauf Digital vælger.

### 10.1 Referencetilfælde for beregninger

Den godkendte regel om oprunding tilføjer følgende accepttilfælde for produktionsløsningen. Afprøv hver værdi som direkte indtastning og som uafrundet geometriresultat for alle fire brandmodstandstider og begge sprog. Tilladte værdier kræver fortsat en gyldig tykkelse ved den afrundede tabelposition.

| Positivt Ap/V før afrunding | Påkrævet Ap/V til opslag | Resultat af grænsekontrol |
| --- | --- | --- |
| 125,0 | 125 | Tilladt, hvis tabelcellen er gyldig |
| 125,1 | 126 | Tilladt, hvis tabelcellen er gyldig |
| 125,7 | 126 | Tilladt, hvis tabelcellen er gyldig |
| 379,9 | 380 | Tilladt, hvis tabelcellen er gyldig |
| 380,0 | 380 | Tilladt, hvis tabelcellen er gyldig |
| 380,1 | 381 | Afvist før tykkelsesopslag |

Følgende eksisterende referencetilfælde med heltal gælder fortsat; oprunding efterlader deres Ap/V uændret.

| Profil og løsning | Påkrævet resultat |
| --- | --- |
| Svær cirkulær 100 mm, klammer, fire sider | Ap/V 130 m²/m³; R60 / 350 °C giver 25 mm. |
| Middelsvær cirkulær 100 mm, klammer, fire sider | Ap/V 154 m²/m³; må ikke overtage værdien fra den svære kategori. |
| Koldvalset kvadratisk 100 × 100 × 4 mm, bjælke/PHL, tre sider | Ap/V 242 m²/m³; R60 / 750 °C giver 20 mm. |
| Koldvalset rektangulær 100 × 60 × 5 mm, bjælke/PHL, tre sider | R90 / 550 °C giver 35 mm. |
| Koldvalset rektangulær 180 × 100 × 5 mm, bjælke/PHL, fire sider | Ap/V 258 m²/m³; R120 / 750 °C giver 40 mm. |
| HEB100 og IPE120, klammer, tre sider | Ap/V forbliver henholdsvis 116 og 231 m²/m³. |
| Ap/V 379 og 380, temperatur 750 °C | Gyldige referencetykkelser: R30 15 mm; R60 30 mm; R90 30 mm; R120 40 mm. |
| Ap/V 381, 400 og 401 | Ingen gyldig tykkelse for nogen profiltilstand eller understøttet brandmodstandstid, heller ikke hvor underliggende tabeller indeholder en værdi. |
| R90 / 747 °C / Ap/V 379; R120 / 664 °C / Ap/V 17 | Utilgængelige referenceceller forbliver ikke-understøttede, selv om Ap/V ligger inden for maksimumgrænsen. |

Dette er referencetilfælde fra referencedata/test, ikke en tilladelse til at generalisere tykkelse mellem inddata. Udtømmende firefeltsopslag og uafhængighed af rækkefølgen af rækker supplerer disse udvalgte eksempler.

### 10.2 Integrerede acceptscenarier

| Scenarie | Dækkede krav | Betingelse for godkendt test |
| --- | --- | --- |
| Arbejdsgang for standardprofiler og brugerdefinerede profiler | UX-001; FR-001–FR-007; DR-001–DR-004 | Gennemfør både direkte og geometribaserede brugerdefinerede tilstande samt standardeksempler på hvert sprog. Manglende/ikke-understøttede inddata giver ikke resultater, der fremstår gyldige. |
| Oprunding af Ap/V | FR-002–FR-003; DR-002–DR-004; UX-010 | Afprøv alle seks decimaltilfælde ovenfor gennem direkte indtastning og geometri for R30/R60/R90/R120 på begge sprog. Eksakte heltal forbliver uændrede; en afrundet værdi over 380 afvises før opslag. Manglende celler ved ellers tilladte afrundede værdier forbliver ikke-understøttede. |
| Uafhængig projektredigering | FR-009–FR-014; UX-008–UX-009 | Gem standardberegninger og to forskelligt navngivne brugerdefinerede beregninger, skift gentagne gange, opdater kun én, tilføj en anden, og annuller/bekræft sletning og Nyt projekt. Antal, navne og uberørte poster forbliver korrekte. |
| Identiske profiler med samlet længde | FR-009; FR-019; DR-006 | Dokumenter ti identiske HEB100-elementer på 6 m som én beregning med 60 m samlet længde og samme brandmodstandstid, dimensionerende ståltemperatur, inddækning og beskyttede sider. Ved uændret spild/lagopbygning er mængderne ti gange mængderne for 6 m før afrunding til visning. Der kræves intet felt til profilantal, ingen ekstra antalsmultiplikator og ingen dublerede beregninger. |
| Lokal lagring og genåbning af historiske filer | FR-015–FR-017; EX-007; DR-011 | Åbn repræsentative eksisterende filer, og bevar gemte resultater. Opdater én post udtrykkeligt; gem/genåbn, og verificer de tilsigtede ændrede og uændrede værdier. |
| Validering af længde og spild | FR-019–FR-020; DR-006; UX-004; UX-010 | Verificer standardværdierne 6,0 m og 10%. Accepter længde 0,5 m, spild 0%, decimalspild 12,5% og spild 150% med gyldige mængder. Afvis længde 0 eller negativ, negativt spild, tomme påkrævede inddata og ikke-numerisk tekst med tydelige sprogtilpassede meddelelser; ingen bliver ubemærket til nul eller et gyldigt overslag med nulmængder. Test decimalindtastning på begge sprog efter den aftalte separatorkonvention. |
| Aktuelle kontra gemte materialeresultater | FR-018–FR-022; DR-005–DR-006 | Ændr længde fra 6 m til 12 m, spild og lagopbygning. Aktuelle mængder opdateres; gemte projektmængder ændres først efter Opdater beregning. |
| Gentagne produkter og CO₂ | FR-023; FR-026; DR-007–DR-009 | Sammenlign enkelte/gentagne pladelag og identiske/forskellige klammer ved 0% og 10% spild. Ingen mængder eller udledninger går tabt ved sammenlægning. Gentag efter sprogskift. |
| Miljøgrundlag | FR-025–FR-026; DR-008 | Den relevante bæredygtigheds-/dataansvarlige hos Knauf leverer den godkendte sammenhæng mellem faktorer/moduler og undtagelser. Medtagne beregninger og det forklarede omfang svarer til dette grundlag; dette indebærer ikke uafhængig myndighedsmæssig verifikation. |
| Metadata ved første download | FR-008; EX-001–EX-002; EX-005; EX-010; UX-007 | Indtast, erstat eller ryd metadata, og klik straks på det relevante download uden først at bekræfte feltet. Undersøg den første faktiske PDF eller PDF i ZIP-filen på begge sprog, både med tomme og eksisterende cacher. Den indeholder de senest accepterede metadata. |
| PDF-dato og beskrivelse | EX-008–EX-009 | Afprøv midnat UTC, begge overgange mellem sommer- og vintertid, flere rapportsider og senere download af uændrede filer. Verificer grænsen på to linjer/udeladelsesprikker for sætninger, LF/CRLF, lange ord og bogstavelige specialtegn i begge skabeloner/rapporttyper. |
| Overensstemmelse mellem materiale-Excel og ZIP | EX-003–EX-006; FR-022; UX-005 | Selvstændige arbejdsbøger/projektarbejdsbøger stemmer overens med deres definerede gemte resultater; ZIP-rapporten svarer til projektgrundlaget. Simulerede manglende eksterne dokumenter identificeres, og gentagne links fjernes som dubletter. |
| Godkendt opdeling mellem eksporttyper | EX-001–EX-005; EX-007 | Individuelle og samlede PDF'er indeholder dimensionering uden materialetabeller eller CO₂-opgørelser. Individuelle, beregningsopdelte og samlede Excel-materialelister udelader kolonner med CO₂/EPD-/databladlinks. ZIP indeholder dokumentation og tilgængelige supplerende filer uden automatisk at medtage redigerbare `.fireboard`-data, som forbliver et separat output til lagring/genåbning. Prototypens summerede forbrug pr. meter må ikke behandles som et forbrugstal for projektet som helhed, og der må ikke indføres en alternativ sammenlægningsformel eller en yderligere eksporttype. |
| Fuld sprogtilpasning | UX-002–UX-006; UX-010; DR-009 | Gennemgå alle skærmbilleder, fejl, bekræftelser, noter, arknavne og beskrivende filnavne, som applikationen styrer, på begge sprog. Katalogbeskrivelser svarer til de udpegede felter, decimaler bruger den valgte konvention, og identifikatorer/brugerangivne navne forbliver uændrede. |

Test på browserniveau er nødvendige for metadata ved direkte download, bekræftelse af destruktive handlinger og navigation. Test må ikke utilsigtet bekræfte et felt på forhånd, før download afprøves. Netværks-/serverforsinkelse og gentagne redigerings-/downloadforløb bør indgå i accepttestene; den præcise dækning af understøttede browsere/enheder behandles i OQ-11.

Den foregående implementeringsvalidering af prototypeversionen, der leveres i ZIP-filen, rapporterede **390 beståede automatiserede test**, herunder 132 tilfælde for maksimal Ap/V og 89 tilfælde for PDF-dato/-beskrivelse. Testsuiten blev ikke kørt igen ved denne rene dokumentationsrevision. Eksisterende test dokumenterer ikke opfyldelse af den nyligt godkendte oprunding og validering af længde/spild eller af kravene til bekræftelse, fuld sprogtilpasning og direkte download i den fremtidige løsning.

## 11. Prototypen som reference og kendte begrænsninger

### 11.1 Referenceversion og sporbarhed

Knauf Digital modtager prototypens kildekode som en ZIP-kopi. Henvisningerne nedenfor identificerer individuelle kilde-, data-, test- og dokumentationsfiler i denne kopi; relative stier følger dens mappestruktur. Den eksisterende `docs/functional-specification.md` bevares uændret. Dette udkast er et separat kravdokument, ikke en revision af den tidligere beskrivelse af den implementerede løsning. ZIP-filen med prototypens kildekode er en overdragelsesleverance, som adskiller sig fra den brugergenererede ZIP med projektdokumentation, der er beskrevet i EX-005.

| Referenceområde | Relevante kilder og test |
| --- | --- |
| Arbejdsgang, profil-/inddækningsvalg, metadata og styring af download | [app.py](../app.py): trinnavigation omkring 3314; endeligt opslag omkring 4195–4370; downloads i sidepanelet omkring 3107–3258; metadata/aktuel PDF omkring 4495–4578. |
| Ap/V-maksimum og validering af understøttede resultater | [validation_helpers.py](../utils/validation_helpers.py), `validate_fireboard_lookup`; [test_apv_maximum.py](../test_apv_maximum.py). |
| Kategorispecifikke opslag | [app.py](../app.py), endelige filtre for Ap/V og materialeforbrug; [test_profile_category_lookup.py](../test_profile_category_lookup.py). |
| Brugerdefineret geometri og gendannelse | [geometry_helpers.py](../utils/geometry_helpers.py), [custom_profile_validation.py](../utils/custom_profile_validation.py); [test_geometry_helpers.py](../test_geometry_helpers.py), [test_custom_profile_state.py](../test_custom_profile_state.py). |
| Materialer, faktisk identitet og CO₂ | [material_helpers.py](../utils/material_helpers.py), `deduplicate_materials`, `build_material_row`, `generate_materials`; [test_material_co2.py](../test_material_co2.py), [test_screw_clamp_logic.py](../test_screw_clamp_logic.py). |
| Gemte beregninger, indtastningsindstillinger og gemte resultater | [calculation_state.py](../utils/calculation_state.py); [test_calculation_state.py](../test_calculation_state.py). |
| Lokale projektfiler | [project_io.py](../utils/project_io.py), `export_project_state`, `parse_project_file`, `import_project_state`; [test_project_io.py](../test_project_io.py). |
| PDF-output og godkendt layout | [pdf_generator.py](../utils/pdf_generator.py), `draw_project_description`, `generate_single_pdf`, `generate_complete_pdf`; [dansk skabelon](../PDF_template.pdf), [engelsk skabelon](../PDF_template_EN.pdf); [test_pdf_report_fields.py](../test_pdf_report_fields.py). |
| Excel, samlede materialer og ZIP | [export_helpers.py](../utils/export_helpers.py), [project_package.py](../utils/project_package.py); [test_excel_export_styling.py](../test_excel_export_styling.py), [test_project_package.py](../test_project_package.py). |
| Sprogtilpasning | [translations.py](../translations.py), katalogets beskrivelsesfelter, materiale-/eksporthjælpere og tekst styret af applikationen i [app.py](../app.py). |

### 11.2 Bekræftede mangler og afgrænsninger i prototypen

| Emne | Aktuel dokumentation | Fortolkning for den fremtidige løsning |
| --- | --- | --- |
| Metadata ved direkte download | Beskrivelsen kopieres til projektmetadata, efter at downloads i sidepanelet er behandlet. Individuelle PDF-bytes forberedes før klikket; afventende redigeringer kan ankomme for sent til første download. | UX-007 og EX-010 er godkendte mangler, som skal afhjælpes. Et ekstra Anvend-trin, der alene skyldes applikationsrammen, er ikke en godkendt løsning. |
| Destruktive handlinger | Sletning og Nyt projekt udføres uden bekræftelse. | Bekræftelse kræves af FR-012, FR-014 og UX-008. |
| Sprogtilpasning og katalogformuleringer | Flere meddelelser/noter, arknavne og filnavne er fortsat danske; den aktuelle materialevisning bruger dansk tekst og erstatninger. Katalogets engelske felter er heller ikke konsekvent skrevet på gennemarbejdet engelsk. | Sprogtilpas applikationsstyret indhold, og brug de leverede DK-/EN-felter uændret. Redaktionelle katalogændringer kræver særskilt godkendelse. |
| Sproguafhængig identitet | Samlede materialer bruger viste artikelnumre med beskrivelser som alternativ; gemte materialeresultater kan bevare tekst fra et tidligere sprog. | Stabil produktidentitet skal styre sammenlægning. Tvetydige ældre rækker kræver en aftalt kompatibilitetspolitik, ikke gættet identitet. |
| Historiske gemte materialeresultater | Åbning bevarer gamle resultater; inddata og gemte mængder kan afvige indtil Opdater beregning. | Bevaring og udtrykkelige opdateringer er godkendt adfærd. En tydelig forklaring kræves; automatisk genberegning gør ikke. |
| Mængder for brugerdefinerede profiler | Der beregnes intet materiale- eller CO₂-resultat for brugerdefinerede profiler. Nogle projektnoter har numeriske nulværdier som pladsholdere. | Opfind ikke mængder, og fremstil ikke utilgængelige overslag som målt nul. Udvidelse til mængder for brugerdefinerede profiler er ikke godkendt. |
| Håndtering af numeriske inddata | Direkte Ap/V får afskåret decimalerne, geometribaseret Ap/V afrundes til nærmeste heltal; længde/spild, som ikke kan fortolkes, kan blive til nul, og negative inddata er ikke konsekvent begrænset. | Produktionsløsningen skal runde positivt Ap/V opad, afvise afrundede værdier over 380, acceptere decimallængde > 0 og spild ≥ 0 uden en særskilt øvre spildgrænse, bruge standardværdier på 6,0 m/10% og forklare ugyldig indtastning uden ubemærket at erstatte den med nul. Dette er godkendte mangler, som skal afhjælpes; kun resterende materiale-/CO₂-præcision og detaljer om indtastningsseparatorer behandles i OQ-09. |
| Identiske profiler | Prototypen understøtter samlet profillængde og forhindrer en nøjagtig gentagelse af den senest gemte beregning. | Én beregning kan dække flere profiler med identiske dimensioneringsforhold ved brug af deres samlede længde. Et felt til profilantal og en funktion til dublerede beregninger er ikke påkrævet. |
| Miljødokumentation | Gemte faktorer/typer og undtagelser styrer resultaterne; koden dokumenterer ikke i sig selv den enkelte faktors livscyklusgrundlag eller aktualitet. | A1–A3/C3–C4 og de angivne undtagelser er godkendt funktionelt omfang. Understøttende dokumentation og formelt ejerskab kræver bekræftelse fra den relevante bæredygtigheds-/dataansvarlige hos Knauf. |
| Eksportafgrænsning | PDF'er udelader materiale-/CO₂-opgørelser; Excel udelader CO₂-/dokumentlinks; ZIP udelader redigerbare projektfiler. Samlede forbrugstal pr. meter summeres. | Bevar den godkendte opdeling og det eksisterende indhold, herunder begge muligheder for projektmaterialelister. Kolonnen med summeret forbrug pr. meter er prototypeadfærd, ikke et meningsfuldt forbrugstal for projektet som helhed; ingen erstatningsformel for sammenlægning eller ny eksporttype er godkendt. |
| Lokal lagring og eksterne dokumenter | Der er ikke implementeret en projektdatabase eller konti. Supplerende dokumenter afhænger af eksterne URL'er og kan udelades med en README, når de ikke er tilgængelige. | Lokal lagring/genåbning er fortsat påkrævet. Knauf Digital bestemmer produktionsplatformen; applikationen garanterer ikke tilgængeligheden af eksterne dokumenter. |

Den aktuelle referenceversion indeholder allerede rettelsen af kategorispecifikke Ap/V-/materialeopslag, rettelsen af CO₂ for det fulde sammenlagte Fireboard-areal, særskilte klammeartikler, rettelsen af gendannelse/nulstilling af brugerdefinerede profiler, håndhævelse af heltalsmaksimum for Ap/V samt genereringsdatoer efter København og PDF-beskrivelser på to linjer. Tidligere udsagn i beskrivelsen af den implementerede løsning om, at disse to sidstnævnte PDF-funktioner eller grænsen på 380 mangler, er forældede for denne referenceversion.

## 12. Åbne spørgsmål og forudsætninger

De fire beslutninger om oprunding af Ap/V, validering og standardværdier for længde/spild, identiske profiler med samlet længde samt opdelingen mellem eksporttyper er godkendt og er ikke længere åbne spørgsmål. De resterende spørgsmåls-ID'er bevares for at fastholde henvisninger; spring i nummereringen er tilsigtede. Ingen af spørgsmålene nedenfor genåbner disse beslutninger eller den godkendte maksimumgrænse, livscyklusomfanget, resultatet med seneste metadata ved download, bekræftelseskravene, sprogunderstøttelsen eller princippet om bevaring af gemte resultater.

Ansvarskategorierne nedenfor angiver, hvor beslutninger ved overdragelsen hører hjemme. De indebærer ikke, at navngivne ansvarlige, formelle godkendelsesmandater eller styringsordninger allerede er udpeget. Intet ansvar for ingeniørfaglig, myndighedsmæssig eller miljøfaglig godkendelse tildeles prototypeudvikleren personligt.

| Ansvarsområde | Relevant organisatorisk kategori |
| --- | --- |
| Funktionelle krav og produktomfang | Knauf Commercial / udpeget produktejer |
| Beregningsdata og brandbeskyttelsesforudsætninger | Relevant teknisk/F&U-ansvarlig hos Knauf |
| Miljøfaktorer, livscyklusomfang og undtagelser | Relevant bæredygtigheds-/dataansvarlig hos Knauf |
| Teknisk implementering, arkitektur, sikkerhed, idriftsættelse og drift | Knauf Digital |
| Funktionel accept | Aftales i fællesskab mellem Knauf Commercial og Knauf Digital |

### 12.1 A. Funktionelle, ingeniørfaglige og miljømæssige oplysninger, som kræver bekræftelse

| ID | Påkrævet beslutning eller dokumentation | Ansvar og resterende usikkerhed |
| --- | --- | --- |
| OQ-01 | Bekræft den tilsigtede målgruppe for produktionsløsningen og den brugerrettede formulering om ingeniørfagligt ansvar. | Knauf Commercial / den udpegede produktejer bekræfter målgruppe og funktionelle begrænsninger, mens den relevante tekniske/F&U-ansvarlige hos Knauf bekræfter formuleringen om ingeniørfagligt ansvar. Formelle kvalifikationer, rollebegrænsninger og formuleringer er fortsat udefinerede. |
| OQ-04 | Bekræft den ingeniørfaglige referenceudgivelse og geometrivejledning, komponentregler, miljøfaktorer og sammenhænge for undtagelser; lever dokumentation, der knytter faktorer til A1–A3/C3–C4. | Den relevante tekniske/F&U-ansvarlige hos Knauf bekræfter beregningsdata og brandbeskyttelsesforudsætninger; den relevante bæredygtigheds-/dataansvarlige hos Knauf bekræfter miljøfaktorer, livscyklusomfang, undtagelser og understøttende dokumentation. Formelle udpegninger og styringsforhold skal aftales med Knauf Digital efter afsnit 12.2. Kildematerialet alene kan ikke dokumentere faktorgrundlag eller uafhængig verifikation. Der forudsættes ingen brugergrænseflade til dataadministration. |
| OQ-08 | Definer en politik for alternativ håndtering og gennemgang, når katalogbeskrivelsen på det valgte sprog er tom, tvetydig eller indeholder danske formuleringer. | Knauf Commercial / den udpegede produktejer bekræfter indholdspolitikken med den relevante katalogdataansvarlige; Knauf Digital implementerer den aftalte alternative håndtering. Eksisterende indhold i BESKRIVELSE_DK/BESKRIVELSE_EN må ikke omskrives automatisk. |
| OQ-09 | Bekræft resterende beregnings- og visningspræcision for materialer/CO₂, afstemning mellem rækker og summer samt accepterede decimaltegn ved indtastning. | Knauf Commercial / den udpegede produktejer bekræfter visnings- og indtastningskonventioner med Knauf Digital. Den relevante tekniske/F&U-ansvarlige bekræfter præcisionen i materialeberegninger; den relevante bæredygtigheds-/dataansvarlige bekræfter CO₂-præcision og afstemning. Oprunding af Ap/V, understøttelse af decimaler for længde/spild, deres grænser/standardværdier og sprogtilpasset decimalvisning er allerede godkendt; dette spørgsmål genåbner dem ikke. Prototypens formatering med to decimaler afklarer ikke alle afrundingsgrænser for materialer/CO₂. |
| OQ-10 | Stadfæst fortolkningen af aktuelle kontra gemte eksporter i afsnit 1.2 og brugervisningen af historiske eller ændrede, men ikke opdaterede, beregninger. | Knauf Commercial / den udpegede produktejer bekræfter den funktionelle betydning og formulering; Knauf Digital implementerer interaktionen. Senest indtastede metadata skal registreres automatisk, mens gemte materialeresultater kræver udtrykkelige opdateringer. Det godkendte eksportomfang forbliver uændret uden en Anvend-omvej pr. felt. |

### 12.2 B. Implementering, accept, styring og driftsforhold ved overdragelsen

Formelt ansvar for datavedligeholdelse og udgivelser under OQ-04 skal aftales ved overdragelsen mellem de relevante tekniske/F&U-ansvarlige og bæredygtigheds-/dataansvarlige hos Knauf, Knauf Commercial og Knauf Digital. Dette omfatter dimensioneringstabeller, komponentregler, miljøfaktorer, undtagelser og dokumenter, der linkes til. Knauf Digital har ansvaret for den tekniske implementering og driftsforholdene; dette styringsarbejde overfører ikke ingeniørfaglig eller miljøfaglig godkendelse til den funktionelle produktejer og godkender ikke ny funktionalitet.

| ID | Påkrævet beslutning eller dokumentation | Ansvar og resterende usikkerhed |
| --- | --- | --- |
| OQ-05 | Aftal, hvilke historiske `.fireboard`-filer der skal være kompatible, og hvordan manglende gemte materialeresultater, uafklarede produktidentiteter og ufuldstændige ældre felter håndteres; beslut, om identifikation af datarevision er påkrævet. | Knauf Digital definerer kompatibilitetsløsningen, mens Knauf Commercial / den udpegede produktejer tilslutter sig understøttede filer og brugersynlig håndtering, og den relevante tekniske/F&U-ansvarlige eller bæredygtigheds-/dataansvarlige inddrages i datafortolkningen. Eksisterende filer bevarer resultater, men mangler en identifikator for beregningsdataenes revision og kan afhænge af viste beskrivelser. Ubemærket genberegning af dimensioneringsresultater er fortsat forbudt. |
| OQ-11 | Aftal ansvar for produktionsaccept, understøttede browsere/enheder, dokumentation til gennemgang og driftsforhold. | Funktionel accept aftales i fællesskab mellem Knauf Commercial og Knauf Digital. Knauf Digital har ansvaret for teknisk implementering, arkitektur, sikkerhed, idriftsættelse og drift. Formelle accept- og driftsordninger skal fortsat aftales; her opfindes ingen ydeevnegrænser, tilgængelighedsstandard, browsermatrix eller serviceniveau. |

Produktionsteknologien og driftsudformningen forbliver Knauf Digitals ansvar. Dette dokument foreskriver ikke Streamlit, Python, CSV-lagring, et bestemt PDF-bibliotek, implementering af sessionstilstand, autentifikationsteknologi eller hostingplatform. Det godkender heller ikke ubemærket nye konto-, delings-, optimerings- eller indkøbsfunktioner.

Gennemgangen af version 1.0 bør bekræfte specifikationen som overdragelsesreference og afklare de resterende spørgsmål via de relevante ansvarskategorier. Gennemgangen giver ikke i sig selv ingeniørfaglig, myndighedsmæssig eller miljøfaglig godkendelse. Efterfølgende revisioner kan registrere disse beslutninger uden at gøre prototypefejl til påkrævet adfærd i produktionsløsningen.
