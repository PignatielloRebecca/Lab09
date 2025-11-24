import copy

from flet.core import row

from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0
        self._max_giorni = None
        self._max_budget =None
        self._tour_regione=[]

        # TODO:  Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        relazioni=TourDAO.get_tour_attrazioni()

        for relazione in relazioni:
            id_tour=relazione["id_tour"]# qua prendiamo l'id del tour
            id_attrazione=relazione["id_attrazione"] # qua prendiamo l'id dell'attrazione

            tour=self.tour_map[id_tour]
            attrazione=self.attrazioni_map[id_attrazione]
            if tour and attrazione:

                tour.attrazioni.add(attrazione)
                attrazione.tour.add(tour)

        # TODO

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        # seleziono i vincoli

        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self._max_giorni=max_giorni
        self._max_budget=max_budget

        # seleziono solo i tour di una regione
        self._tour_regione=[tour for tour in self.tour_map.values() if str(tour.id_regione) == str(id_regione)]

        # calcolo il valore culturale del tour
        #for tour in self._tour_regione:
            #tour.valore_culturale = sum(attrazione.valore_culturale for attrazione in tour.attrazioni) # per ogni attrazione ho il valore

        self._ricorsione(0, [], 0,0, 0)

        # TODO


        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _attrazioni_duplicate(self,tour, attrazioni_usate:set):
        for attrazione in tour.attrazioni:
            if attrazione.id in attrazioni_usate:
                return True
        return False


    #def _aggiorna_attrazioni(self, tour, attrazioni_usate):
        nuove=set(attrazioni_usate)
        for attrazione in tour.attrazioni:
            nuove.add(attrazione)
        return nuove


    def tour_validi(self, tour, durata_corrente, costo_corrente, attrazioni_usate):
        if self._max_giorni is not None and durata_corrente + tour.durata_giorni > self._max_giorni:
            return False # costo accumuato fino ad ora e costo dei tour che si aggiungono
        if self._max_budget is not None and costo_corrente + tour.costo > self._max_budget:
           return False
        if self._attrazioni_duplicate(tour, attrazioni_usate):
            return False
        return True

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        # condizione terminale


        if start_index==len(self._tour_regione): # finisco quando ho analizzato tutti i tour
            #if valore_corrente>self._valore_ottimo:# i
            #valore_culturale=0
            #for tour in pacchetto_parziale:
                #for attrazioni in tour.attrazioni:
                    #valore_culturale+=attrazioni.valore_culturale

            if valore_corrente> self._valore_ottimo: # quando il valore corrente è maggiore del valore culturale massimo
                self._valore_ottimo = valore_corrente
                self._costo = costo_corrente
                self._pacchetto_ottimo=pacchetto_parziale.copy()
            return
        else:
            for i in range(start_index, len(self._tour_regione)):
                tour=self._tour_regione[i] # prendo il primo tour
                attrazioni_usate = []
                for tour_pacchetto in pacchetto_parziale:
                    attrazioni_usate= attrazioni_usate + list(tour_pacchetto.attrazioni)



                if self.tour_validi(tour, durata_corrente, costo_corrente, attrazioni_usate):
                    incremento=0
                    for attrazione in tour.attrazioni:
                        incremento += attrazione.valore_culturale

                    nuovo_valore = valore_corrente + incremento
                    pacchetto_parziale.append(tour)



                    self._ricorsione(i + 1,pacchetto_parziale,durata_corrente + tour.durata_giorni,costo_corrente + tour.costo, nuovo_valore)
                    pacchetto_parziale.pop()
        






        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
