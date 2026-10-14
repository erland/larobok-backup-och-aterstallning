# 12. Arkitekturprinciper för återställningsbara system

Det är möjligt att känna till både idempotens, Saga och Transactional Outbox och ändå bygga ett system som inte går att återställa. Mönstren är verktyg; återställningsförmåga uppstår först när vi har fattat sammanhängande beslut om **vilka tillstånd som måste överleva, vilka som kan rekonstrueras och hur vi vet att verksamheten kan fortsätta**.

För ärendeplattformen är arkitektfrågan inte längre ”ska vi ha backup på fem databaser?” utan ”vilka garantier måste de fem tjänsterna tillsammans upprätthålla efter ett partiellt haveri?”. Kapitel 12 sammanför konsekvenserna av de föregående kapitlen i beslut som kan dokumenteras, granskas och testas.

## 12.1 Börja med verksamhetens oföränderliga regler

Ett *invariant* är ett villkor som inte får brytas trots fel och återställningar. För vårt system kan det vara:

- Ett externt expedierat beslut måste kunna återfinnas och knytas till rätt ärende.
- Samma expedieringsuppdrag får inte leda till flera verkställda utskick om den externa parten inte medger det.
- En arbetsuppgift får inte behandlas som avslutad enbart därför att en lokal tjänst ser en avslutningshändelse; nödvändiga underlag måste vara verifierbara.

Villkoren preciseras tillsammans med verksamheten. Ett register med *status = klar* är inte bevis för att motparten faktiskt mottagit en handling. Därför behöver man identifiera vilken aktör eller datakälla som är auktoritativ för varje påstående. Utan dessa regler kan man mäta hur snabbt servrarna kommer upp, men inte avgöra om systemet är korrekt återställt.

## 12.2 Sex arkitekturbeslut som bör vara explicita

| Beslut | Arkitektens fråga | Exempel i ärendeplattformen |
|---|---|---|
| Tillståndsklass | Vad måste återläsas, kan återberäknas eller kan kasseras? | Beslutsregister: återställ; sökindex: bygg om; cache: töm |
| Återställningsgräns | Vilka komponenter måste stämmas av tillsammans? | Beslut, expedieringsuppdrag och externa kvittenser |
| Händelsegarantier | Hur hanteras bortfall, dubletter och ändrad ordning? | Beständiga ID:n, lokala transaktioner och avvikelsekö |
| Processåterhämtning | Hur identifieras avbrutna steg och okända resultat? | Beständig processstatus och avstämning före återförsök |
| Isolering | Hur förhindras sidoeffekter under rekonstruktion? | Återställningsmiljö utan externa skrivbehörigheter |
| Bevis | Vilken kontroll krävs innan tjänsten öppnas? | Avstämda beslut, inga obearbetade kritiska avvikelser |

Tabellen är avsiktligt en beslutskarta, inte en ny katalog över tekniska mönster. När ett arkitekturbeslut dokumenteras behöver det ange omfattning, antaganden, ansvarig ägare, beroenden och hur kravet kan verifieras. Ett designbeslut som säger ”konsumenten är idempotent” utan att ange nyckel, lagringstid och transaktionsgräns är inte tillräckligt för en återställningsplan.

## 12.3 RPO och RTO behöver knytas till rätt objekt

Ett traditionellt mål på exempelvis RPO 15 minuter och RTO två timmar kan vara användbart, men blir missvisande om det enbart gäller databasen. För en distribuerad lösning bör målen beskriva **vilken verksamhetsförmåga** som ska vara återupptagen och **vilket data- eller händelsebortfall** som är acceptabelt.

Anta att ärenderegistrering ska återupptas inom två timmar. Då kan sökindex få byggas om under fortsatt drift, medan en tjänst som expedierar beslut behöver avvakta kontroll av externa kvittenser. Allt måste inte öppnas samtidigt, men ordningsföljden och begränsningarna måste vara bestämda i förväg. Ett uppfyllt tekniskt RTO innebär inte automatiskt att varje verksamhetsfunktion är återställd.

Målens innebörd bör vara mätbar: från vilken avbrottstidpunkt räknas tiden, vilka förutsättningar ingår, och när är funktionen tillräckligt verifierad för att betraktas som återställd? Skillnaden mellan *systemet svarar på hälsokontroll* och *nya ärenden kan registreras utan förlust eller dubbla verkningar* kan vara stor.

## 12.4 Designa för avvikelse, inte enbart för normal drift

När något hamnar utanför det automatiskt hanterbara behövs synliga avvikelsetillstånd. En extern begäran som har timeout bör få tillståndet *utfall okänt*, inte automatiskt *misslyckad*. Om en konsument saknar förväntad tidigare händelse bör avvikelsen kunna isoleras och undersökas utan att hela köflödet måste förstöras.

Det innebär att arkitekturen behöver korrelations-ID, spår till auktoritativa källor, tydliga felkategorier och operativa funktioner för att stoppa, läsa om, jämföra och återuppta behandling. Loggar och mätvärden hjälper inte om de försvinner tillsammans med den drabbade regionen. Samtidigt ska loggar inte felaktigt behandlas som fullständiga affärsregister.

## 12.5 Arkitekturbeslut som kan granskas

Ett konkret arkitekturbeslut kan formuleras så här:

> **ADR-014: Återställning av expediering.** Beslutstjänsten äger beslutens status. Varje expedieringsbegäran har en oföränderlig operation-ID. Extern integration lagrar begäran och mottagningsresultat beständigt. Efter återställning får ett osäkert utfall inte skickas om förrän det har stämts av med mottagarens statusfunktion eller hanterats manuellt. Kravet verifieras med ett test där processen avbryts efter externt anrop men före lokal resultatlagring.

Beslutet anger vem som vet vad, vilken risk som accepteras och vilket test som visar om lösningen håller. Exakta tekniker varierar; principen är densamma även om tjänsterna körs på virtuella maskiner, Kubernetes eller hanterade molntjänster.

## 12.6 Från applikationsdesign till plattformsförutsättningar

Arkitekturen kan kräva bevarade händelser, isolerad återuppbyggnad och återställbara hemligheter. Då måste driftsplattformen faktiskt erbjuda förmågan: tillräcklig lagringstid, rätt backup av varaktigt tillstånd, nyckelhantering, åtkomst till images och konfiguration samt en separat återställningsmiljö.

Det är länken till nästa kapitel. Ingen plattform kan reparera en verksamhetsprocess som saknar återupptagningskontrakt. Men en välkonstruerad applikation kan inte räddas om den underliggande plattformens beständiga resurser, identiteter eller nätverksberoenden inte går att återskapa.

## 12.6 Exempel på ett granskningsbart arkitekturbeslut

**ADR-014 – Återställning av handläggning efter partiell dataförlust (illustrativt).** Utgångsläge: handläggningstjänsten äger arbetsuppgifter och får registreringshändelser via en förmedlare. Krav: ingen registrering får tyst hoppas över efter återställning och upprepad leverans får inte skapa en andra arbetsuppgift.

Tre alternativ jämförs: (A) enbart nattlig databasbackup, (B) backup plus manuell jämförelse med ärendekällan eller (C) backup med beständiga mottagarmarkörer, styrd återleverans och automatiserad avvikelselista. Alternativ A är billigast att driva men saknar skydd mot glapp mellan backup och brokerposition. B kan minska risken men ger lång och personberoende återhämtning. C kräver kod, retentionskontrakt och testning men möjliggör kontrollerad återstart. Vi väljer C för kritiska ärenden och behåller B som reservrutin när källhistoriken är ofullständig.

**Konsekvenser:** Tjänsteägaren ansvarar för atomär ändring av arbetsuppgift och behandlingsmarkör; plattformsteamet dokumenterar brokerretention och återställningsmetod; verksamhetsägaren fastställer vilka avvikelser som måste granskas manuellt. Beslutet är inte godkänt enbart för att komponenterna finns. **Verifiering:** återställ databasen till en tidpunkt före tre dokumenterade händelser, sätt konsumentpositionen medvetet efter dem och bekräfta att kontrollen upptäcker glappet; genomför därefter säker återleverans och kontrollera att antalet arbetsuppgifter blir exakt det förväntade.

Detta exempel gör arkitekturprincipen granskbar: ett dokumenterat val, ett accepterat driftåtagande och ett mätbart beteende efter fel.
