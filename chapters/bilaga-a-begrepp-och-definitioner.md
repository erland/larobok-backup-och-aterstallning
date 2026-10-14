# Bilaga A. Begrepp och definitioner

Denna ordlista ger korta arbetsdefinitioner. Definitionerna ska läsas tillsammans med den konkreta garanti som respektive plattform och tillämpning faktiskt erbjuder.

| Begrepp | Betydelse för återställning |
|---|---|
| Auktoritativ källa | Den källa som enligt arkitekturen avgör vilket affärstillstånd som gäller; den är inte nödvändigtvis den som uppdaterades senast. |
| Backup | Bevarad kopia eller återställningsunderlag med kontrollerade möjligheter att återskapa information. Replikering är inte i sig backup. |
| Checkpoint | Beständig uppgift om hur långt en bearbetning kommit, kopplad till definierad indata och behandlingsversion. |
| CQRS | Separata modeller för skrivning och läsning. Läsprojektioner kan ibland byggas om från auktoritativa data. |
| Dead-letter queue (DLQ) | Plats för meddelanden som inte kunnat behandlas enligt avsett felhanteringsförfarande. Kräver ägarskap, retention och åtgärdsrutin. |
| Deduplicering | Mekanism som identifierar redan behandlade operationer, vanligen med beständiga identiteter. |
| Disaster Recovery (DR) | Förmågan att återuppta en godtagbar verksamhet efter omfattande avbrott. |
| Event sourcing | Design där en ordnad händelsehistorik utgör auktoritativ källa till ett domäntillstånd. |
| Eventual consistency | Flera vyer eller tjänster kan tillfälligt skilja sig åt men kan konvergera enligt givna förutsättningar. |
| Händelse | Uppgift om något som inträffat; skiljer sig från ett kommando om att göra något. |
| Idempotens | Upprepning av samma identifierade operation ger ingen extra avsedd verksamhetseffekt. |
| Inbox | Beständig mottagarregistrering som gör det möjligt att känna igen och hantera återleveranser. |
| Kompensation | Ny verksamhetsåtgärd som motverkar en tidigare åtgärds effekt; inte liktydigt med teknisk rollback. |
| Konsumentposition / offset | Position eller kvittens som visar vad konsumenten har läst eller behandlat, beroende på systemets semantik. |
| Kausal konsistens | Ordningskrav mellan orsak och följd, till exempel att ett mottaget beslut inte kan föregå ärendets registrering. |
| PITR | Point-in-time recovery: återställning av datalager till en vald tidpunkt med erforderlig basbackup och logghistorik. |
| Projektion | Härlett lästillstånd eller annan representation som kan beräknas från en källa. |
| Recovery point objective (RPO) | Högsta accepterade förlust av data eller framsteg uttryckt i tid; fördelas och preciseras per informationsmängd. |
| Recovery time objective (RTO) | Mål för hur snabbt avsedd funktion ska vara återställd; definiera både start och slut för mätningen. |
| Replay / återspelning | Ny behandling av bevarade händelser; kan återbygga projektioner men får inte oavsiktligt upprepa externa effekter. |
| Retention | Den tid information, loggar eller meddelanden finns kvar; kan begränsa möjligheten till replay och deduplicering. |
| Saga | En långlivad process med lokala steg och eventuell framåtriktad återhämtning eller kompensation. |
| Snapshot | Ögonblicksbild av ett specificerat tillstånd; måste kunna kopplas till rätt logg-/sekvensposition för vidare återspelning. |
| Transactional Outbox | Affärsändring och publiceringsavsikt sparas atomärt i samma databas, därefter publiceras händelsen separat. |
| Verksamhetsmässig återställning | Återgång till kontrollerat, begripligt och godtagbart tillstånd för verksamhetsflödet, inte bara startade komponenter. |

Begreppet *exactly once* behöver alltid avgränsas: garanti inom en brokertransaktion omfattar inte automatiskt en extern databas eller ett tredjeparts-API.
