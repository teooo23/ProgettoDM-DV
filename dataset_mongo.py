import json
import pymongo
import pprint
from bson.son import SON
from tqdm import tqdm #sbarra dei tempi
from pymongo import MongoClient, errors
from collections import Counter

class DatasetMongo:

    def __init__(self):
        DOMAIN = 'localhost:'
        PORT = 27017
        self.client = MongoClient(
        host = [ str(DOMAIN) + str(PORT) ],
        serverSelectionTimeoutMS = 3000)
        self.db = self.client.Football
        self.stagione_1819 = self.db.Stagione1819

    #FUNIONE CHE RITORNA DIZIONARIO CON NUMERO DI PARTITE DA TITOLARE PER OGNI GIOCATORE (ID)
    # I TITOLTALI SONO I PRIMI 11 ELEMENTI DELLA LISTA, QUINDI PRENDO DIRETTAMENTE GLI ID DI QUESTI
    def titolari(slf):
    ids = []
    results = self.stagione_1819.find({})  ## return cursor
    for result in results:
        players = result["away"]["players"]
        players2 = result["home"]["players"]
        for player in players[0:11]:
            ids.append(player["playerId"])
        for player in players2[0:11]:
            ids.append(player["playerId"])
    return Counter(ids)

    # FUNZIONE CHE RITORNA DUE DIZIONARI:
    # IL PRIMO CONTA IL NUMERO DI PARTITE DA SUBENTRATO PER OGNI GIOCATORE (ID)
    # IL SECONOD IL NUMERO DI PARTITE IN CUI È STATO SOSTITUITO
    def nonTitolari(self):
    ids_nontit = []
    ids2_nontit = []
    results = self.stagione_1819.find({})  ## return cursor
    for result in results:
        players = result["away"]["players"][11:14]
        players2 = result["home"]["players"][11:14]
        for player in players:
            if "subbedInExpandedMinute" in player:
                    ids_nontit.append(player["playerId"])
                    ids2_nontit.append(player["subbedOutPlayerId"])
        for player in players2:
            if "subbedInExpandedMinute" in player:
                    ids_nontit.append(player["playerId"])
                    ids2_nontit.append(player["subbedOutPlayerId"])
    return Counter(ids_nontit), Counter(ids2_nontit)

    # FUNZIONE CHE RITORNA TRE DIZIONARI PER CONTARE NUMERO DI CARTELLINI
    def Cartellini(self):
        ls = [] #lista giocatori che hanno preso un cartellino giallo
        ls1 = [] # doppio cartellino giallo nella stessa partita
        ls2 = [] #lista cartellini rossi
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            events = result["home"]["incidentEvents"]
            events1 = result["away"]["incidentEvents"]
            for event in events:
                if ("cardType" in event) and (event["cardType"]["displayName"] == "Yellow"):
                    ls.append(event["playerId"])
                elif ("cardType" in event) and (event["cardType"]["displayName"] == "SecondYellow"):
                    ls1.append(event["playerId"])
                elif ("cardType" in event) and (event["cardType"]["displayName"] == "Red"):
                #in alcuni casi non è presente l'id del giocatore perché è stato espulso l'allenatore
                    if "playerId" in event:
                        ls2.append(event["playerId"])
            for event in events1:
                if ("cardType" in event) and (event["cardType"]["displayName"] == "Yellow"):
                    ls.append(event["playerId"])
                elif ("cardType" in event) and (event["cardType"]["displayName"] == "SecondYellow"):
                    ls1.append(event["playerId"])
                elif ("cardType" in event) and (event["cardType"]["displayName"] == "Red"):
                #in alcuni casi non è presente l'id del giocatore perché è stato espulso l'allenatore
                    if "playerId" in event:
                        ls2.append(event["playerId"])
        return Counter(ls), Counter(ls1), Counter(ls2)

    #NUMERO GOL OPEN PLAY
    def GiocatoriOpenPlay(self):
        ls = []
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            events = result["events"]
            for event in events:
                for types in event["satisfiedEventsTypes"]:
                    if types == 18:
                        ls.append(event["playerId"])
        return Counter(ls)

    #AUTOGOL
    def Autogol(self):
        ls = []
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            events = result["events"]
            for event in events:
                for types in event["satisfiedEventsTypes"]:
                    if types == 22:
                         ls.append(event["playerId"])
        return Counter(ls)

    #NUMERO DI TRIPLETTE
    ## FUNZIONE CHE RITORNA I MARCATORI DI UNA DATA PARTITA
    def getGoals(self, match):
    scorers = []
    home = match["home"]["incidentEvents"]
    away = match ["away"]["incidentEvents"]
    for event in home:
        if event["type"]["value"] == 16:
            scorers.append(event["playerId"])
    for event in away:
        if event["type"]["value"] == 16:
            scorers.append(event["playerId"])
    return scorers

    ## FUNZIONE CHE DATA UNA PARTITA SALVA SOLO I GIOCATORI CHE HANNO FATTO UNA TRIPLETTA
    def getTriplets(self, match):
        scorers = self.getGoals(match)
        scorers = Counter(scorers)
        result = [x for x in scorers if scorers[x] > 2]
        return result

    #FUNZIONE CHE RITONA DIZONARIO CON NUMERO DI TRIPLETTE FATTE NEL CAMPIONATO
    def getAllTriplets(self):
            ls = []
            results = self.stagione_1819.find({})  ## return cursor
            for result in results:
                triplets = self.getTriplets(result)
                for x in triplets:
                    ls.append(x)
            return Counter(ls)

    def GiocatoriPallaFerma(self):
        ls = []
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            events = result["events"]
            for event in events:
                for types in event["satisfiedEventsTypes"]:
                    if types == 20:
                         ls.append(event["playerId"])
        return Counter(ls)

    #NUMERO DI ASSIST
    def GiocatoriAssists(self):
        ls = []
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            events = result["events"]
            for event in events:
                for types in event["satisfiedEventsTypes"]:
                    if types == 91:
                         ls.append(event["playerId"])
        return Counter(ls)

    # NUMERO DI RIGORI SEGNATI
    def GiocatoriRigori(self):
        ls = []
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            events = result["events"]
            for event in events:
                for types in event["satisfiedEventsTypes"]:
                    if types == 21:
                         ls.append(event["playerId"])
        return Counter(ls)

    # DIZIONARIO CON NUMERO DI CLEAN SHEET PER OGNI PORTIERE
    def PortieriInviolati(self):
        ls = []
        results = self.stagione_1819.find({})  ## return cursor
        for result in results:
            partita = result["home"]
            partita1 = result["away"]
            if partita["scores"]["fulltime"] == 0:
                ls.append(partita["players"][0]["playerId"])
                if partita1["scores"]["fulltime"] == 0:
                    ls.append(partita["players"][0]["playerId"])
        return Counter(ls)

    # RESTITUISCE DIZIOANRIO CON LE 4 POSIZIONI: PORTIERE, DIFENSORE, CENTROCAMPISTA, ATTACCANTE
    def roles(self):
        role = {}
        for pos in ['GK', 'DR', 'DC', 'DL', 'MR', 'MC', 'ML', 'FW', 'FWR', 'FWL', 'DMR', 'DML', 'AMC', 'DMC', 'AMR', 'AML']:
            if pos == 'GK':
                role[pos] = 'Goalkeeper'
            elif pos in ('DR', 'DC', 'DL'):
                role[pos] = 'Defender'
            elif pos in ('FWR', 'FW', 'FWL', 'AMC', 'AMR', 'AML'):
                role[pos] = 'Forward'
            else:
                role[pos] = 'Midfielder'
        return role

    # DIZIOANRIO CON CHIAVE ID GIOCATORE E COME VALORE STRINGA CON I RUOLI GIOCATI IN OGNI PARTITA
    def player_pos(self):
        d = {}
        results = self.stagione_1819.find({})
        for result in results:
            for player in result['home']['players'][:11]:
                if player['playerId'] not in d:
                    d[player['playerId']] = []
                position = player['position']
                d[player['playerId']].append(position)
            for player in result['away']['players'][:11]:
                if player['playerId'] not in d:
                    d[player['playerId']] = []
                position = player['position']
                d[player['playerId']].append(position)
        return d

    def most_frequent(self, List):
        return max(set(List), key = List.count)

    # TRADUZIONE DELLE SIGLE IN POSIZIONE, TORNA LA POSIZIONE PIÙ GIOCATA PER OGNI GIOCATORE
    def to_roles(self):
        roles_word = {}
        for key in self.player_pos().keys():
            roles_word[key] = self.roles()[self.most_frequent(self.player_pos()[key])]
        return roles_word

        def build_dataset(self):
            stats = {}
            for id_ in self.player.keys():
                stats[id_] = {
                'Name' : self.player[id_]['Name'],
                'Team' : self.player[id_]['Team'],
                'League' : self.player[id_]['League'],
                'Apperances' : {
                    'TotalApperances' : self.giocatoriTitolari()[int(id_)] + self.giocatoriNonTitolari()[0][int(id_)],
                    'Started' : self.giocatoriTitolari()[int(id_)],
                    'CameOn' : self.giocatoriNonTitolari()[0][int(id_)],
                    'TakenOff' : self.giocatoriNonTitolari()[1][int(id_)]
                },
                 'Goal' : {
                     'TotalGoals' : self.GiocatoriGoalTotali()[int(id_)],
                     'HatTrick' : self.getAllTriplets()[int(id_)],
                     'Penalty' : self.GiocatoriRigori()[int(id_)],
                     'OpenPlay' : self.GiocatoriOpenPlay()[int(id_)],
                     'GoalSetPiece' : self.GiocatoriPallaFerma()[int(id_)],
                     'OwnGoal' : self.Autogol()[int(id_)]
                 },
                 'Assist' : self.GiocatoriAssists()[int(id_)],
                 'Card' : {
                    'Yellow' : self.Cartellini()[0][int(id_)] - self.Cartellini()[1][int(id_)],
                    'DoubleYellow' : self.Cartellini()[1][int(id_)],
                    'Red' : self.Cartellini()[2][int(id_)]
                 }
                }
                if 'Team2' in self.player[id_]:
                    stats[id_]['Team2'] = self.player[id_]['Team2']
                if int(id_) in self.to_roles():
                    stats[id_]['Position'] = self.to_roles()[int(id_)]
                    if stats[id_]['Position'] in ('Goalkeeper', 'Defender'):
                        stats[id_]['CleanSheet'] = self.PortieriInviolati()[int(id_)]

            return stats

        def create(self):
            with open('Dataset-mongo.json', 'w') as f:
                f.write(json.dumps(self.build_dataset()))
            print("Dataset created")
