from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import time
import json

class DownloadHelper:

    def __init__(self):
        self.months_trad = [["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],["Jan","Feb","Mac","Apr","Mei","Jun","Jul","Aug","Sep","Okt","Nov","Des"]]
        self.competitions = {
                                "SerieA": "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A",
                                "PremierLeague": "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League",
                                "LaLiga": "https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga",
                                "Ligue1": "https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1",
                                "Bundesliga": "https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga",
                            }
        self.sources_list = []
        self.dataset = {}
        self.timeout = 10
        self.max_iter = 5
        self.last_match = 0
        self.start_match = 0
        self.competition = ""
        self.comp_years = ""
        self.year = ""
        self.month = ""
        self.filename = "dataset.json"

    def openChrome(self):
        # LANCIO TOR CON IL COMANDO POPEN
        tor = os.popen("tor")
        # ASPETTO CHE TOR SI APRA
        time.sleep(5)
        # APRO SELENIUM IN MODO ANONIMO
        options = webdriver.ChromeOptions()
        PROXY = "socks5://localhost:9050"
        options.add_argument('--proxy-server=%s' % PROXY)
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.chrome = webdriver.Chrome(options=options)
        self.chrome.get("https://check.torproject.org/")
        # CONTROLLO CHE TOR SIA ATTIVO E FUNZIONI CORRETTAMENTE
        if "Congratulations. This browser is configured to use Tor." in self.chrome.page_source:
            print("Chrome è stato avviato correttamente.")
            return
        else:
            # ALTRIMENTI CHIEDO SE RIPROVARE
            self.closeChrome()
            print("Si è verificato un problema con l'avvio di Tor e Chrome. Riprovare?")
            retry = input("[S/N]: ")
            if retry == "S" or retry == "s":
                self.openChrome()
            else:
                print("DownloadHelper terminato")
                exit()

    # FUNZIONE CHE CHIUDE CHROME
    def closeChrome(self):
        try:
            self.chrome.close()
        except:
            return

    # FUNZIONE CHE CHIUDE, SE C'E, IL BANNER DEI COOKIE
    def closeCookies(self):
        try:
            self.chrome.execute_script('window.__cmpui("setAndSaveAllConsent",!0)')
            time.sleep(0.5)
        except:
            return

    # FUNZIONE CHE ASPETTA UNA CONDIZIONE SULLA PAGINA
    def waitCondition(self,condition,*args,iter_count=0):
        try:
            WebDriverWait(self.chrome, self.timeout).until(
                condition(
                    *args
                )
            )
        except TimeoutException as e:
            # SE DOPO timeout SECONDI LA CONDIZIONE NON SI E ANCORA VERIFICATA RIPROVO FINO AL RAGGIUNGIMENTO
            # DI max_iter TENTATIVI
            if iter_count < self.max_iter:
                print("Timeout di caricamento, tentativo numero "+str(iter_count+1)+" di "+str(self.max_iter))
                self.waitCondition(condition,*args,iter_count=iter_count+1)
            else:
                self.closeChrome()
                print("Errore di Timeout. Riprovare?")
                retry = input("[S/N]: ")
                if retry == "S" or retry == "s":
                    self.download()
                else:
                    self.datiBySources()
                    self.saveDataset()
                    # FACCIO IL LOG DELL'ERRORE E DELL'ULTIMA PARTITA SCARICATA
                    self.log(time.ctime()+" --> "+"Errore di Timeout")
                    self.log(time.ctime()+" --> "+str(e))
                    self.log(time.ctime()+" --> "+"Ultima partita scaricata: "+str(self.last_match))
                    print("Dati già scaricati salvati correttamente")
                    print("DownloadHelper terminato")
                    exit()

    # FUNZIONE CHE CALCOLA, DATA LA SITUAZIONE DELLA PAGINA, QUANTI CAMBI DI MESI (IN MODO ASSOLUTO) BISOGNA FARE
    def calcMonthDiff(self):
        # CONVERTO IN NUMERO IL MESE DESIDERATO (ES Gen --> 0, ... , Dic --> 11)
        index_desired_month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(self.month)
        # PRENDO LA DATA DELLA PAGINA ATTUALE
        actual_date = self.chrome.find_element_by_css_selector("#date-config-toggle-button > .text").get_attribute('innerHTML')
        try:
            # PRENDO IL SET DI MESI DELLA TRADUZIONE CORRETTA
            correct_months = self.calcCorrectTrad(actual_date[0:3])
        except  Exception as e:
            # SE IL TENTATIVO FALLISCE AVVISO CHE SERVE UN NUOVO SET DI TRADUZIONI DEI MESI
            self.closeChrome()
            print("Nuova traduzione dei mesi da aggiungere (mese sconosciuto "+actual_date[0:3]+")! Riprovare comunque?")
            retry = input("[S/N]: ")
            if retry == "S" or retry == "s":
                self.download()
            else:
                self.datiBySources()
                self.saveDataset()
                # FACCIO IL LOG DELL'ERRORE E DELL'ULTIMA PARTITA SCARICATA
                self.log(time.ctime()+" --> "+"Nuova traduzione dei mesi da aggiungere (mese sconosciuto "+actual_date[0:3]+")")
                self.log(time.ctime()+" --> "+str(e))
                self.log(time.ctime()+" --> "+"Ultima partita scaricata: "+str(self.last_match))
                print("Dati già scaricati salvati correttamente")
                print("DownloadHelper terminato")
                exit()
        # CONVERTO IN NUMERO IL MESE ATTUALE (ES. 0 --> GENNAIO, ... , 11 --> DICEMBRE)
        index_actual_month = correct_months.index(actual_date[0:3])
        # PRENDO L'ANNO DELLA PAGIN ATTUALE
        actual_year = actual_date[-4:]
        #CALCOLO I PASSI DA FARE RELATIVI AI MESI...
        i = index_actual_month - index_desired_month
        # E AGGIUNGO 12 O -12 PASSI SE L'ANNO E DIVERSO
        if actual_year > self.year:
            i += 12
        elif actual_year < self.year:
            i -= 12
        return i

    # FUNZIONE CHE TORNA IL GIUSTO SET DI TRADUZIONE DEI MESI
    def calcCorrectTrad(self,actual_date):
        for months in self.months_trad:
            try:
                index_actual_month = months.index(actual_date)
                return months
                break
            except:
                continue

    # FUNZIONE CHE SI SPOSTA NEL MESE DESIDERATO
    def selectMonth(self):
        # CONVERTO IN NUMERO IL MESE DESIDERATO (ES Gen --> 0, ... , Dic --> 11)
        index_desired_month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(self.month)
        # ASPETTO CHE IL WIDGET CON LA DATA SIA PRESENTE NELLA PAGINA
        self.waitCondition(expected_conditions.text_to_be_present_in_element,(By.CSS_SELECTOR,"#date-config-toggle-button > .text"),self.year[0:2])
        # CALCOLO IL NUMERO DI PASSI DA FARE PER ARRIVARE AL MESE RICHIESTO
        i = self.calcMonthDiff()
        # SE I > 0 DEVO CLICCARE SUL BOTTONE PRECEDENTE
        if i > 0:
            previous_button = self.chrome.find_element_by_css_selector(".previous.button.ui-state-default.rc-l.is-default")
            while i > 0:
                # PER OGNI CLIC ASPETTO CHE LA PAGINA SI AGGIORNI
                table = self.chrome.find_element_by_id("tournament-fixture")
                self.waitCondition(expected_conditions.element_to_be_clickable,(By.CSS_SELECTOR,".previous.button.ui-state-default.rc-l.is-default"))
                previous_button.click()
                self.waitCondition(expected_conditions.staleness_of,table)
                self.waitCondition(expected_conditions.presence_of_element_located,(By.ID,"tournament-fixture-wrapper"))
                i -= 1
        # SE I > 0 DEVO CLICCARE SUL BOTTONE PRECEDENTE
        elif i < 0:
            i = -i
            next_button = self.chrome.find_element_by_css_selector(".next.button.ui-state-default.rc-r.is-default")
            while i > 0:
                # PER OGNI CLIC ASPETTO CHE LA PAGINA SI AGGIORNI
                table = self.chrome.find_element_by_id("tournament-fixture")
                self.waitCondition(expected_conditions.element_to_be_clickable,(By.CSS_SELECTOR,".next.button.ui-state-default.rc-r.is-default"))
                next_button.click()
                self.waitCondition(expected_conditions.staleness_of,table)
                self.waitCondition(expected_conditions.presence_of_element_located,(By.ID,"tournament-fixture-wrapper"))
                i -= 1

    # FUNZIONE CHE DATA UNA COMPETIZIONE, ANNATA (ES. 2018/2019), ANNO E MESE RITORNA LE SORGENTI DELLE PAGINE DELLE PARTITE
    def getPageSources(self):
        self.sources_list = []
        url_competition = self.competitions[self.competition]
        # APRO CHROME
        self.openChrome()
        # VADO ALLA PAGINA DELLA COMPETIZIONE
        self.chrome.get(url_competition)
        print("Pagina della competizione aperta")
        self.closeCookies()
        actual_url = self.chrome.current_url
        # VADO ALLA PAGINA DELL'ANNATA
        select_comp_years = Select(self.chrome.find_element_by_id('seasons'))
        select_comp_years.select_by_visible_text(self.comp_years)
        print("Anno selezionato")
        self.closeCookies()
        # ASPETTO CHE LA PAGINA VENGA CAMBIATA
        self.waitCondition(expected_conditions.url_changes,actual_url)
        # ASPETTO CHE IL LINK DELLE PARTITE SIA CLICCABILE
        self.waitCondition(expected_conditions.element_to_be_clickable,(By.ID,"link-fixtures"))
        # VADO ALLA PAGINA DELLE PARTITE
        actual_url = self.chrome.current_url
        link_fixtures = self.chrome.find_element_by_id("link-fixtures")
        link_fixtures.click()
        # ASPETTO CHE LE PARTITE SIANO CARICATE
        self.waitCondition(expected_conditions.url_changes,actual_url)
        self.waitCondition(expected_conditions.text_to_be_present_in_element,(By.CSS_SELECTOR,"#sub-navigation ul li a.selected"),"Fixtures")
        print("Pagina delle partite aperta")
        self.closeCookies()
        # VADO AL MESE SELEZIONATO
        self.selectMonth()
        print("Mese selezionato")
        j = self.start_match
        # PRENDO L'ELENCO DELLE PARTITE
        match_reports = self.chrome.find_elements_by_css_selector(".match-link.match-report.rc")
        while j < len(match_reports):
            # ASPETTO CHE IL REPORT DELLA PARTITA SIA CLICCABILE
            self.waitCondition(expected_conditions.element_to_be_clickable,(By.CSS_SELECTOR,".match-link.match-report.rc"))
            match_reports[j].click()
            # ASPETTO CHE IL MATCH REPORT SI CARICHI E CHE SIA CLICCABILE
            self.waitCondition(expected_conditions.text_to_be_present_in_element,(By.CSS_SELECTOR,"#sub-navigation ul li a.selected"),"Match Report")
            self.waitCondition(expected_conditions.element_to_be_clickable,(By.CSS_SELECTOR,"#sub-navigation ul li a.selected"))
            self.closeCookies()
            # SCORRO TRA LE VOCI DEL MENU FINO A TROVARE MATCH CENTRE E CI CLICCO
            menu_buttons = self.chrome.find_elements_by_css_selector("#sub-navigation a")
            for element in menu_buttons:
                if "Match Centre" in element.get_attribute('innerHTML'):
                    # VADO AL MATCH CENTRE
                    element.click()
                    print("Match Centre Aperto")
                    # ASPETTO CHELA SORGENTE DELLA PAGINA CONTENGA I DATI
                    actual_time = time.time()
                    while "matchCentreData = " not in self.chrome.page_source:
                        if time.time() < actual_time + self.timeout*self.max_iter:
                            time.sleep(0.1)
                        else:
                            raise Exception("Match Centre non caricato correttamente")
                    break
            # SALVO LA SORGENTE DELLA PAGINA
            source = self.chrome.page_source
            self.sources_list.append(source)
            print("Sorgente della partita "+str(j+1)+" scaricata, mancanti "+str(len(match_reports)-j-1))
            # TORNO ALLA PAGINA DELLE PARTITE
            self.chrome.back()
            self.chrome.back()
            self.closeCookies()
            # TORNO AL MESE DESIDERATO
            self.selectMonth()
            print("Mese selezionato")
            # RICARICO LA LISTA DELLE PARTITE E PASSO A QUELLA SUCCESSIVA
            match_reports = self.chrome.find_elements_by_css_selector(".match-link.match-report.rc")
            self.last_match = j
            j += 1
        # CHIUDO CHROME
        self.closeChrome()

    # FUNZIONE CHE DATA UNA SORGENTE TORNA L'ID DELLA PARTITA E I DATI IN UNA LISTA
    def dizionarioStats(self,source_file):
        # PRENDO I DATI DEL MATCHCENTRE
        i = source_file.find('matchCentreData = ') + 17
        j = i + 1
        matchCentreData = str()
        while str(source_file[j])!=';':
            matchCentreData += str(source_file[j])
            j += 1
        # PRENDO L'ID DELLA PARTITA
        matchId = str()
        while str(source_file[j])!=';':
            matchId += str(source_file[j])
            j += 1
        # CONVERTO I DATI IN DATATYPE DI PYTHON
        matchCentreData = json.loads(matchCentreData)
        # METTO I DATI IN UNA LISTA E RITORNO I DATI IN COPPIA CON L'ID DELLA PARTITA
        return matchId, matchCentreData

    # FUNZIONE CHE DATE LE SORGENTI TROVATE AGGIUNGE I DATIAL DATASET USANDO COME CHIAVE L'ID DELLA PARTITA
    def datiBySources(self):
        for source in self.sources_list:
            id,dati = self.dizionarioStats(source)
            self.dataset[id] = dati

    # FUNZIONE CHE SALVA IL DATASET
    def saveDataset(self):
        try:
            # SE IL DATASET ESISTE GIA LO AGGIORNA...
            file = open(self.filename,"r")
            actual_dataset = json.loads(file.read())
            file.close()
            actual_dataset.update(self.dataset)
        except:
            actual_dataset = self.dataset
        file = open(self.filename,"w")
        file.write(json.dumps(actual_dataset))
        file.close()
        print("Dataset Salvato")

    # FUNZIONE CHE EFFETTIVAMENTE ESEGUE IL DOWNLOAD
    def download(self):
        try:
            self.getPageSources()
            self.datiBySources()
            self.saveDataset()
        except Exception as e:
            self.closeChrome()
            print("Si è verificato un problema sconosciuto. Riprovare?")
            retry = input("[S/N]: ")
            if retry == "S" or retry == "s":
                self.download()
            else:
                self.datiBySources()
                self.saveDataset()
                # FACCIO IL LOG DELL'ERRORE E DELL'ULTIMA PARTITA SCARICATA
                self.log(time.ctime()+" --> "+"Errore sconosciuto")
                self.log(time.ctime()+" --> "+str(e))
                self.log(time.ctime()+" --> "+"Ultima partita scaricata: "+str(self.last_match))
                print("DownloadHelper terminato")
                exit()

    # FUNZIONE CHE LOGGA GLI ERRORI IN UN FILE log.txt
    def log(self,text):
        file = open("log.txt","a")
        file.write(text+"\n")
        file.close()