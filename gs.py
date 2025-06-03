from gestione_mazzo import Deck, GameBoard
from gestione_giocatori import HumanPlayer, PlayerAI
from pattern_observer import Subject,Observer
import abc
  

class GameSystem:
   
    def __init__(self):
        self.Hplayer= None
        #self.ui = None
        self.deck = None
        self.playerAI= None
        self.gameboard = None #modifica class diagram
        self.TurnManager = TurnManager() #modifica class diagram

    def startGame(self, username):#,ui):
        self.deck = Deck()
        self.Hplayer= HumanPlayer(username)
        self.playerAI= PlayerAI()
        self.gameboard = GameBoard()
        #self.ui  = ui

        self.Hplayer.setGameBoard(self.gameboard)
        self.playerAI.setGameBoard(self.gameboard)


        self.deck.distribute(self.gameboard )
        self.deck.distribute(self.Hplayer)
        self.deck.distribute(self.playerAI )


        #self.TurnManager.register(self.ui)
        self.TurnManager.register(self.Hplayer)
        self.TurnManager.register(self.playerAI)

        #self.TurnManager.currentPlayerIndex = 2
        #self.TurnManager.nextTurn()

    def calculateScores(self): 
        #Numero totale di carte raccolte.
        if len(self.Hplayer.collectedCard) > len(self.playerAI.collectedCard):
           self.Hplayer.score +=1
        elif len(self.Hplayer.collectedCard) < len(self.playerAI.collectedCard):
            self.playerAI.score +=1 
        #numero carte d'oro
        num_oro_p1 = sum(1 for c in self.Hplayer.collectedCard if c.suit == 'Oro')
        num_oro_p2 = sum(1 for c in self.playerAI.collectedCard if c.suit == 'Oro')

        if num_oro_p1 > num_oro_p2:
           self.Hplayer.score +=1
        elif num_oro_p1 < num_oro_p2:
            self.playerAI.score +=1

        #settebello
        settebello_p1 = any(c.number == 7 and c.suit == 'Oro' for c in self.Hplayer.collectedCard)
        settebello_p2 = any(c.number == 7 and c.suit == 'Oro' for c in self.playerAI.collectedCard)

        if settebello_p1:
            self.Hplayer.score += 1  # Aggiungi 1 punto al giocatore se ha il settebello
        if settebello_p2:
            self.playerAI.score += 1

        #primiera
        primiera_p1 = self.calculate_primiera(self.Hplayer)
        primiera_p2 = self.calculate_primiera(self.playerAI)
        if primiera_p1> primiera_p2:
           self.Hplayer.score +=1
        elif primiera_p2 > primiera_p1:
            self.playerAI.score +=1

        
    
    
    def calculate_primiera(self,player):
        primiera_values = {7: 21, 6: 18, 1: 16, 5: 15, 4: 14, 3: 13, 2: 12, 10: 10, 9: 9, 8: 8}
        best_by_suit = {'Oro':None, 'Bastoni':None, 'Spade':None, 'Coppe':None}
    
        for card in player.collectedCard:
            current_best = best_by_suit[card.suit]
            if current_best is None or primiera_values[card.number]> primiera_values[current_best.number]: #se non c'è una carta per questo seme l'aggiunge
                best_by_suit[card.suit] = card
            #altrimenti la confronta
            #elif primiera_values.get(card.number, 0) > primiera_values.get(best_by_suit[card.suit].number, 0):
            #restituisce il punteggio associato al numeor della carta che troviamo in primeria_values
            #la confronta con il valore associato alla carta nel best_by_suiti
                

        # Somma dei valori delle 4 migliori carte, una per seme
        #if len(best_by_suit) < 4:
         #   return 

        punteggio_tot= sum(primiera_values[c.number] for c in best_by_suit.values()if c is not None)
        return punteggio_tot
        
    
    def getWinner(self): #modofica class diagramm
        if self.Hplayer.score > self.playerAI.score :
            return f"{self.Hplayer.username} Win"
        elif self.Hplayer.score == self.playerAI.score :
            return f"It's a Tie"
        else:
            return f"{self.playerAI.__class__.__name__} Wins"

    def endGame(self):

        self.calculateScores()
        winner = self.getWinner()
        return f"""
        Il tuo punteggio: {self.Hplayer.score}<br>
        Punteggio AI: {self.playerAI.score}<br>
        Vincitore: <strong>{winner}</strong>!
    """

class TurnManager(Subject):

    def __init__(self):
        self.observers = list()
        self.currentPlayerIndex = 1
    
    def register(self, ob:Observer):
        self.observers.append(ob)

    def notifyAll(self):
        #if len(self.observers) > 0:
         #   self.observers[0].notify()  # UI
    
        # Notifica SOLO il giocatore corrente
        if self.currentPlayerIndex == 1 and len(self.observers) > 1:
            self.observers[1].notify()  # HumanPlayer
        elif len(self.observers) > 2:
            self.observers[2].notify()  # PlayerAI
        
        
    def nextTurn(self):
        self.currentPlayerIndex = 2 if self.currentPlayerIndex == 1 else 1
        self.notifyAll()
    
    

