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

        # TODO: Aggiungere eventuali altri attributi

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

        # TODO
        tour_attrazioni = TourDAO.get_tour_attrazioni()  # get da DB della relazione tour - attrazioni

        for relazione in tour_attrazioni:
            id_tour = relazione["id_tour"]
            id_attr = relazione["id_attrazione"]

            tour = self.tour_map.get(id_tour)
            attr = self.attrazioni_map.get(id_attr)

            tour.attrazioni.add(attr)
            attr.tour.add(tour)

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
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self.max_giorni = max_giorni
        self.max_budget = max_budget  # valori inseriti dall'utente nella UI

        self.tour_regione = [tour for tour in self.tour_map.values() if tour.id_regione == id_regione]
        # creo una lista con oggetti tour che abbiano la regione richiesta in modo da non iterare su tutti quanti

        self._ricorsione(0, [], 0, 0.0, 0, set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = list(pacchetto_parziale)
            self._costo = costo_corrente

        for i in range(start_index, len(self.tour_regione)):
            tour = self.tour_regione[i]

            durata_nuova = durata_corrente + tour.durata_giorni
            costo_nuovo = costo_corrente + float(tour.costo)

            if self.max_giorni is not None and durata_nuova > self.max_giorni:
                continue

            if self.max_budget is not None and costo_nuovo > self.max_budget:
                continue
            nuove_attr = tour.attrazioni - attrazioni_usate  # Calcolo attrazioni non ancora viste
            valore_nuovo = valore_corrente + sum(
                attrazione.valore_culturale for attrazione in nuove_attr)  # Valore culturale aggiunto

            pacchetto_parziale.append(tour)
            attrazioni_usate.update(
                nuove_attr)

            self._ricorsione(i + 1, pacchetto_parziale, durata_nuova, costo_nuovo, valore_nuovo, attrazioni_usate)

            pacchetto_parziale.pop()
            attrazioni_usate.difference_update(nuove_attr)
