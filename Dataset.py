import json
import csv
from collections import Counter

class Dataset:

    def __init__(self, dataset_path, csv_path):
        file = open(dataset_path,"r")
        self.data1 = json.load(file)
        file.close()

        self.player = {}
        with open(csv_path, encoding='utf-8') as csvfile:
            csvReader = csv.DictReader(csvfile)
            for row in csvReader:
                key = row['playerId']
                del row['playerId']
                if key not in self.player:
                    self.player[key] = row
                else:
                    self.player[key]['Team2'] = row['Team']

    #FUNIONE CHE RITOENA DIZIONARIO CON NUMERO DI PARTITE DA TITOLARE PER OGNI GIOCATORE (ID)
    # I TITOLTALI SONO I PRIMI 11 ELEMENTI DELLA LISTA, QUINDI PRENDO DIRETTAMENTE GLI ID DI QUESTI
    def giocatoriTitolari(self):
        ls = []
        for match in self.data1.keys():
            lista = self.data1[match]["home"]["players"][0:11]
            lista1 = self.data1[match]["away"]["players"][0:11]
            for i in range(len(lista)):
                ls.append(lista[i]["playerId"])
            for i in range(len(lista1)):
                ls.append(lista1[i]["playerId"])
        return Counter(ls)

    # FUNZIONE CHE RITORNA DUE DIZIONARI:
    # IL PRIMO CONTA IL NUMERO DI PARTITE DA SUBENTRATO PER OGNI GIOCATORE (ID)
    # IL SECONOD IL NUMERO DI PARTITE IN CUI È STATO SOSTITUITO
    def giocatoriNonTitolari(self): ### idea basta fare la differenza tra il set intero e quelli titolari senza iterare di nuovo
        ls = [] #lista giocatori subentrati
        ls1 = [] #lista dei giocatori sostituiti
        for match in self.data1.keys():
            lista = self.data1[match]["home"]["players"][11:14]
            lista1 = self.data1[match]["away"]["players"][11:14]
            for i in range(len(lista)):
                if "subbedInExpandedMinute" in lista[i]:
                    ls.append(lista[i]["playerId"])
                    ls1.append(lista[i]["subbedOutPlayerId"])
            for i in range(len(lista1)):
                if "subbedInExpandedMinute" in lista1[i]:
                    ls.append(lista1[i]["playerId"])
                    ls1.append(lista1[i]["subbedOutPlayerId"])
        return Counter(ls), Counter(ls1)

    # FUNZIONE CHE RITORNA TRE DIZIONARI PER CONTARE NUMERO DI CARTELLINI
    def Cartellini(self):
        ls = [] #lista giocatori che hanno preso un cartellino giallo
        ls1 = [] # doppio cartellino giallo nella stessa partita
        ls2 = [] #lista cartellini rossi
        for match in self.data1.keys():
            events = self.data1[match]["home"]["incidentEvents"]
            events1 = self.data1[match]["away"]["incidentEvents"]
        for i in range(len(events)):
            if ("cardType" in events[i]) and (events[i]["cardType"]["displayName"] == "Yellow"):
                ls.append(events[i]["playerId"])
            elif ("cardType" in events[i]) and (events[i]["cardType"]["displayName"] == "SecondYellow"):
                ls1.append(events[i]["playerId"])
            elif ("cardType" in events[i]) and (events[i]["cardType"]["displayName"] == "Red"):
                #in alcuni casi non è presente l'id del giocatore perché è stato espulso l'allenatore
                if "playerId" in events[i]:
                    ls2.append(events[i]["playerId"])
        for i in range(len(events1)):
            if ("cardType" in events1[i]) and (events1[i]["cardType"]["displayName"] == "Yellow"):
                ls.append(events1[i]["playerId"])
            elif ("cardType" in events1[i]) and (events1[i]["cardType"]["displayName"] == "SecondYellow"):
                ls1.append(events1[i]["playerId"])
            elif ("cardType" in events1[i]) and (events1[i]["cardType"]["displayName"] == "Red"):
                #in alcuni casi non è presente l'id del giocatore perché è stato espulso l'allenatore
                if "playerId" in events1[i]:
                    ls2.append(events1[i]["playerId"])
        return Counter(ls), Counter(ls1), Counter(ls2)

    #NUMERO GOL OPEN PLAY
    def GiocatoriOpenPlay(self):
        ls = []
        for match in self.data1.keys():
            events = self.data1[match]["events"]
            for i in range(len(events)):
                for j in range(len(events[i]["satisfiedEventsTypes"])):
                    if events[i]["satisfiedEventsTypes"][j] == 18:
                        ls.append(events[i]["playerId"])
        return Counter(ls)

    #AUTOGOL
    def Autogol(self):
        ls = []
        for match in self.data1.keys():
            events = self.data1[match]["events"]
            for i in range(len(events)):
                for j in range(len(events[i]["satisfiedEventsTypes"])):
                    if events[i]["satisfiedEventsTypes"][j] == 22:
                        ls.append(events[i]["playerId"])
        return Counter(ls)

    # NUMERO GOAL TOTALI
    def GiocatoriGoalTotali(self):
        ls = []
        for match in self.data1.keys():
            events = self.data1[match]["events"]
            for i in range(len(events)):
                if events[i]["type"]["value"] == 16:
                    ls.append(events[i]["playerId"])
        return Counter(ls)

    #NUMERO DI TRIPLETTE
    ## FUNZIONE CHE RITORNA I MARCATORI DI UNA DATA PARTITA
    def getGoals(self, match): #goal una partita
        scorers = []
        home = match["home"]["incidentEvents"]
        away = match["away"]["incidentEvents"]
        for i in range(len(home)):
            if home[i]["type"]["value"] == 16:
                scorers.append(home[i]["playerId"])
        for i in range(len(away)):
            if away[i]["type"]["value"] == 16:
                scorers.append(away[i]["playerId"])
        return scorers

    ## FUNZIONE CHE DATA UNA PARTITA SALVA SOLO I GIOCATORI CHE HANNO FATTO UNA TRIPLETTA
    def getTriplets(self, match):
        scorers = self.getGoals(match)
        scorers = Counter(scorers)
        result = [x for x in scorers if scorers[x] > 2]
        return result

    #FUNZIONE CHE RITONA DIZONARIO CON NUMERO DI TRIPLETTE FATTE NEL CAMPIONATO
    def getAllTriplets(self):
        result = []
        for match in self.data1.keys(): ## volendo da fare in main
            triplets = self.getTriplets(self.data1[match])
            for x in triplets:
                result.append(x)
        return Counter(result)

    def GiocatoriPallaFerma(self):
        ls = []
        for match in self.data1.keys():
            events = self.data1[match]["events"]
            for i in range(len(events)):
                for j in range(len(events[i]["satisfiedEventsTypes"])):
                    if events[i]["satisfiedEventsTypes"][j] == 20:
                        ls.append(events[i]["playerId"])
        return Counter(ls)

    # NUMERO DI ASSIST
    def GiocatoriAssists(self):
        ls = []
        for match in self.data1.keys():
            events = self.data1[match]["events"]
            for i in range(len(events)):
                for j in range(len(events[i]["satisfiedEventsTypes"])):
                    if events[i]["satisfiedEventsTypes"][j] == 91:
                        ls.append(events[i]["playerId"])
        return Counter(ls)

    # NUMERO DI RIGORI SEGNATI
    def GiocatoriRigori(self):
        ls = []
        for j in self.data1.keys():
            events = self.data1[j]["events"]
            for i in range(len(events)):
                for j in range(len(events[i]["satisfiedEventsTypes"])):
                    if events[i]["satisfiedEventsTypes"][j] == 21:
                        ls.append(events[i]["playerId"])
        return Counter(ls)

    # DIZIONARIO CON NUMERO DI CLEAN SHEET PER OGNI PORTIERE
    def PortieriInviolati(self): ### fai con meno accessi al database ls stringa è una lista di caratteri
        ls = []
        for match in self.data1.keys():
            partita = self.data1[match]["home"]
            partita1 = self.data1[match]["away"]
            if partita["scores"]["fulltime"] == 0:
                ls.append(partita["players"][0]["playerId"]) #id del portiere
                if partita1["scores"]["fulltime"] == 0:
                    ls.append(partita["players"][0]["playerId"])
        return Counter(ls)

    def build_dataset(self):
        stats = {}
        for id_ in self.player.keys():
            stats[id_] = {
            'Name' : self.player[id_]['Name'],
            'Team' : self.player[id_]['Team'],
            'League' : self.player[id_]['League'],
            'Apperances' : {
                'TotalApperances' : self.giocatoriTitolari()[id_] + self.giocatoriNonTitolari()[0][id_],
                'Started' : self.giocatoriTitolari()[id_],
                'CameOn' : self.giocatoriNonTitolari()[0][id_],
                'TakenOff' : self.giocatoriNonTitolari()[1][id_]
            },
             'Goal' : {
                 'TotalGoals' : self.GiocatoriGoalTotali()[id_],
                 'HatTrick' : self.getAllTriplets()[id_],
                 'Penalty' : self.GiocatoriRigori()[id_],
                 'OpenPlay' : self.GiocatoriOpenPlay()[id_],
                 'GoalSetPiece' : self.GiocatoriPallaFerma()[id_],
                 'OwnGoal' : self.Autogol()[id_]
             },
             'Assist' : self.GiocatoriAssists()[id_],
             'CleanSheet' : self.PortieriInviolati()[id_],
             'Card' : {
                'Yellow' : self.Cartellini()[0][id_] - self.Cartellini()[1][id_],
                'DoubleYellow' : self.Cartellini()[1][id_],
                'Red' : self.Cartellini()[2][id_]
             }
            }
            if 'Team2' in self.player[id_]:
                stats['Team2'] : self.player[id_]['Team2']

        return stats

    def create(self):
        with open('Dataset.json', 'w') as f:
            f.write(json.dumps(self.build_dataset()))
        print("Dataset created")
