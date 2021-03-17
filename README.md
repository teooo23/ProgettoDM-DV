# Struttura Dataset
Dizionario con chiave [`ID_PARTITA`](#id-partita)
### ID Partita
Dizionario con chiavi
 - attendance
 - [away](#away-e-home)
 - commonEvents
 - elapsed
 - etScore
 - [events](#events)
 - expandedMaxMinute
 - expandedMinutes
 - ftScore
 - [home](#away-e-home)
 - htScore
 - maxMinute
 - periodCode
 - periodEndMinutes
 - periodMinuteLimits
 - 	pkScore
 - playerIdNameDictionary
 - [referee](#referee)
 - score
 - startDate
 - startTime
 - statusCode
 - timeStamp
 - timeoutInSeconds
 - venueName
 - weatherCode
### Away e Home
Dizionario con chiavi
- averageAge
- countryName
- field
- [formations](#formations)
- [incidentEvents](#events)
- managerName
- name
- [players](#players)
- scores
- [shotZones](#shotzones)
- [stats](#stats)
- teamId
### Events
Lista di Dizionari con chiavi:
-  blockedX
- blockedY
- cardType
	- displayName
	- value
- endX
- endY
- eventId
- expandedMinute
- goalMouthY
- goalMouthZ
- id
- isGoal
- isOwnGoal
- isShot
- isTouch
- minute
- outcomeType
	- displayName
	- value
- period
- playerId
- [qualifiers](#qualfiiers)
- relatedEventId
- relatedPlayerId
- satisfiedEventsTypes
- second
- teamId
- type
	- displayName
	- value
- x
- y
### Referee
Dizionario con chiavi
- firstName
- hasPartecipatedMatches
- lastName
- name
- officialId
### Formations
Lista di Dizionari con chiavi:
- captainPlayerId
- endMinuteExpanded
- formationId
- formationName
- [formationPositions](#formationpositions)
- formationSlots
- jerseyNumbers
- period
- playerIds
- startMinuteExpanded
- subOffPlayerId
- subOnPlayerId
### Players
Lista di Dizionari con chiavi
- age
- field
- height
- isFirstEleven
- isManOfTheMatch
- name
- playerId
- position
- shirtNo
- [stats](#stats)
- subbedInExpandedMinute
- subbedInPeriod
- subbedInPlayerId
- subbedOutExpandedMinute
- subbedOutPeriod
- subbedOutPlayerId
- weight
### ShotZones
- missHighCentre
- missHighLeft
- missHighRight
- missLeft
- missRight
- onTargetHighCentre
- onTargetHighLeft
- onTargetHighRight
- onTargetLowCentre
- onTargetLowLeft
- onTargetLowRight
- postCentre
- postLeft
- postRight

Ognuna di queste chiavi contiene un piccolo dizionario con struttura:
- stats
	- MINUTO
		- count
		- goalCount
### Stats
Dizionario con chiavi:
-  aerialSuccess
- aerialsTotal
- aerialsWon
- clearances
- cornersAccurate
- cornersTotal
- defensiveAerials
- disposessed
- dribbleSuccess
- dribbledPast
- dribblesAttempted
- dribblesLost
- dribblesWon
- errors
- foulsCommitted
- interceptions
- minutesWithStats
- offensiveAerials
- offsidesCaught
- passSuccess
- passesAccurate
- passesKey
- passesTotal
- possession
- ratings
- shotsBlocked
- shotsOffTarget
- shotsOnPost
- shotsOnTarget
- shotsTotal
- tackeSuccess
- tackleSuccesfull
- tackleUnsuccesfull
- tacklesTotal
- throwInAccuracy
- throwInsAccurate
- thowsInsTotal
- touches

Ogni voce è un dizionario con chiave MINUTO
### Qualifiers
Lista di Dizionari con chiavi:
- type
	- value
	- displayName
- value

### FormationPositions
Lista di Dizionari con chiavi:
- horizontal
- vertical

## File di Key-Mapping
### key-to-formations
Associa la chiave numerica al nome della formazione
### key-to-event-type
Associa la chiave numerica al tipo di evento (è quella contenuta nel campo **type** degli [events](#events)
### key-to-event-type-specific
Associa la chiave numerica ad un tipo di evento più specifico (è quello contenuto nel campo **satisfiedEventsTypes** degli [events](#events)
### key-to-qualifiers-type
Associa la chiave **value** al valore **displayName** dei [qualifiers](#qualifiers)
# DownloadHelper DOCS

## Esempio di utilizzo:
```
from DownloadHelper import DownloadHelper
helper = new DownloadHelper()
helper.timeout = 15
helper.max_iter = 2
helper.competition = "SerieA"
helper.comp_years = "2018/2019"
helper.year = "2018"
helper.month = "Sep"
helper.filename = "serie-a-sep-2018.json"
helper.download()
```
`DownloadHelper.download` crea un file `serie-a-sep-2018.json` contenente i dati relativi alla stagione 2018/2019 della Serie A del mese di Settembre. Se non viene specificato nessun `filename` il file creato si chiamerà `dataset.json`. `timeout` sono i secondi massimi che l'helper aspetterà per il caricamento tra un click e l'altro mentre `max_iter` sono i tentativi massimi. Se non specificati valgono rispettivamente `10` e `5`. Questa funzione non sovrascrive. Se per esempio dopo il codice precedente si esegue:
```
helper.competition = "PremierLeague"
helper.comp_years = "2017/2018"
helper.year = "2018"
helper.month = "Feb"
helper.download()
```
il file `serie-a-sep-2018.json` conterrà sia i dati sulla Serie A che sulla Premier League.

### Competizioni

Le possibili competizioni sono:

- "SerieA"
- "Bundesliga"
- "LaLiga"
- "Ligue1"
- "PremierLeague"
- "Eredivise"

### Mesi

I mesi vanno inseriti con la sigla di tre lettere inglese (la prima maiuscola).

### Anno

L'anno deve essere una **stringa**

### Errori
In caso di fallimento l'`helper` chiederà se riprovare o meno. Nel caso in cui alcune partite siano già state scaricate e si decida di non riprovare **verranno comunque salvate** mentre se si decide di riprovare **non verranno salvate!** Nel primo caso verranno salvati dettagli sull'errore e l'indice dell'ultima partita scaricata in un file `log.txt`. Per ripartire dall'ultima partita bisogna settare il valore `helper.start_match` all'indice mostrato nel file di log. Ho notato che non ridurre a tendina la schermata del browser riduce gli errori di timeout.
