import abc
from gestione_mazzo import Deck,Card,GameBoard
from pattern_observer import Observer
#import ollama
from itertools import combinations
import random
import openai
import os
openai.api_key= os.getenv("OPENAI_API_KEY")
print(os.getenv("OPENAI_API_KEY"))


def str_to_card(card_str: str) -> Card:
    try:
        number_str, suit = card_str.strip().split(" di ")
        number = int(number_str)
        suit = suit.capitalize()  # trasforma "oro" in "Oro", ecc.
        return Card(number, suit)
    except Exception as e:
        print(f"[ERROR] str_to_card: {e}")
        return None


class Player(Observer):
    
    def __init__(self):
        self.handCard= list()
        self.collectedCard= list()
        self.score = 0 #modifica class diagramm
        self.gameboard= None
        
    
    def addCard(self,new_cards):
        self.handCard.extend(new_cards)
    
    def removeHandCard(self, card):
        """Rimuove una carta dalla mano del giocatore"""
        if isinstance(card, str):
            card = str_to_card(card)
        if card is None:
            return False
    
        if card in self.handCard:
            self.handCard.remove(card)
            return True
        return False
               
    
    def collectCards(self,new_cards):
        self.collectedCard.extend(new_cards)
        
    
    def setGameBoard(self, board:GameBoard):
        self.gameboard = board
    
    def verify_card(self, card:Card):
        try:
            if card  in self.handCard:
                return card
        except Exception as e:
            print(f'Carta inserita non valida, riprova: {e}')


    def playCard(self,card:str):
        cards_on_board = self.gameboard.GBcards
        card= str_to_card(card)
        self.verify_card(card)
        self.removeHandCard(card)

        #scopa
        if  sum(c.number for c in cards_on_board) == card.number:
                self.collectCards([card]+ cards_on_board)
                self.gameboard.removeAll()
                self.score +=1
                return "Scopa"
        
        #presa diretta
        for c in cards_on_board:
            if card.number == c.number:
                self.collectCards([card,c])
                self.gameboard.removeCard(c)
                return "Presa diretta"
            
        #presa per somma
        for i in range(2, len(cards_on_board)+1):
            for combo in combinations(cards_on_board,i):
                if sum(c.number for c in combo ) == card.number:
                    self.collectCards([card]+ list(combo))
                    self.gameboard.removeCard(list(combo))
                    return "Presa per somma"
        
        self.gameboard.addCard(card)
        return "nessuna presa"  

    def notify(self):
        pass

class HumanPlayer(Player):

    def __init__(self,username:str):
        super().__init__()
        self.username= username
    
    def notify(self):
        print('\n=== Tuo Turno ===')
    
   
class PlayerAI(Player):
    def __init__(self):
        super().__init__()
        
    
    def notify(self):
        print('\n===  Turno AI ===')

    
    def chooseMove(self):

        cards_on_board = self.gameboard.GBcards

        # Costruisci il prompt come fai già
        cardP_str = [f"{card.number} di {card.suit}" for card in self.handCard]
        cardGB_str = [f"{card.number} di {card.suit}" for card in cards_on_board]
        prompt = f"""
Stiamo giocando a Scopa. Tu sei il giocatore AI.
Devi scegliere una delle carte in tuo possesso per giocare.

### Tuo obiettivo:
- Prendere più carte totali possibile.
- Prendere più di cinque carte del seme 'Oro'.
- Prendere il Settebello (cioè il 7 di 'Oro').
- Ottenere la "Primiera": una combinazione di carte con i valori più alti in ogni seme.

## Stato attuale del tavolo da gioco: {cardP_str}
## Stato attuale delle tue carte possedute: {cardP_str}

### Regole per la scelta della mossa:
1. Se una delle tue carte ha lo stesso valore della somma di tutte le carte sul tavolo, giocala: è una Scopa.
2. Se una delle tue carte ha lo stesso valore della somma di una combinazione di carte sul tavolo, gioca quella carta. Scegli la combinazione che:
   - prende più carte totali
   - contiene più carte del seme 'Oro'
   - include il 7 di 'Oro'
3. Se una delle tue carte ha lo stesso valore di una **singola** carta sul tavolo, devi prendere **obbligatoriamente** quella carta.
4. Se non puoi fare prese:
   - Gioca una carta a tua scelta tra le {cardP_str}.
   - Evita di lasciare sul tavolo carte pericolose (es. 7).
   - Se possibile, scegli una carta che mantenga il totale delle carte sul tavolo **sopra 10** (per limitare le possibilità di Scopa dell'avversario).

Rispondi indicando SOLO la carta che vuoi giocare, nel formato: "<valore> di <seme>". Ad esempio: "3 di Coppe"
"""
        try:
         response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "Sei un giocatore esperto di Scopa. Rispondi solo con la carta da giocare, senza spiegazioni."},
                {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=50
            )

         mossa_testo = response.choices[0].message.content.strip()
         print(f"L'AI ha risposto: {mossa_testo}")
         if mossa_testo:
            return mossa_testo
         return self.fallback_move()

        except Exception as e:
            print( f"Eccezione per OpenAI usage: {e}")
            return self.fallback_move()
        
    def fallback_move(self):
        if self.handCard:
            scelta = random.choice(self.handCard)
            return f"{scelta.number} di {scelta.suit}"
        
