class Dataset:
    def __init__(self,dataset_path):
        file = open(dataset_path,"r")
        self.dataset = json.loads(file.read())
        file.close()

    def getEventsById(self,id_partita):
        return self.dataset[id_partita]["events"]

    def getMatchById(self,id_partita):
        return self.dataset[id_partita]

    def getAllEvents(self):
        eventi = []
        for id_partita in self.dataset:
            eventi += append(self.dataset[id_partita]["events"])
        return eventi

    def getScoreById(self,id_partita):
        score = self.dataset[id_partita]["score"]
        home, away = score.split(":")
        return (home.strip(),away.strip())

    def getHomeTeamId(self,id_partita):
        return self.dataset[id_partita]["home"]["teamId"]

    def getAwayTeamId(self,id_partita):
        return self.dataset[id_partita]["away"]["teamId"]

    def getEventsByType(self,id_partita,type):
        return [evento for evento in self.dataset[id_partita]["events"] if evento["type"]["value"] == type]

    def getEventsByTypeIfSuccesful(self,id_partita,type):
        return [evento for evento in self.dataset[id_partita]["events"] if evento["type"]["value"] == type and evento["outcomeType"]["value"] == 1]        