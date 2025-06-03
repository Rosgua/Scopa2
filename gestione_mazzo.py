import random
class Deck:

    def __init__(self):
       suit = ['Oro','Bastoni','Spade','Coppe']
       number = [x for x in range(1,11)]
       self.cards = [Card(n,s) for n in number for s in suit]
       random.shuffle(self.cards)
    
    
    def __repr__(self):
        return f"{self.cards}"
            
    
    def drawCards(self, n:int):
        drawn = self.cards[:n]# contiene le carte rimosse
        self.cards = self.cards[n:]#aggiorna il mazzo
        return drawn
    
    def distribute(self, object ):
        if isinstance(object, GameBoard):
            cards = self.drawCards(4)
            object.addCard(cards)
        else:
            cards = self.drawCards(3)
            object.addCard(cards)
        
  
class Card:
    
    def __init__(self, number: int, suit:str):
        self.number = number
        self.suit = suit
    
    def __repr__(self):
        return f"({self.number}, {self.suit})"
    
    def __eq__(self,other):
        if not isinstance(other, Card):
            return False
        return self.number == other.number and self.suit == other.suit
      
class GameBoard:

    def __init__(self):
        self.GBcards = list()
    
    def addCard(self,new_cards):
        if isinstance(new_cards,list):
            self.GBcards.extend(new_cards)
        else:
             self.GBcards.append(new_cards)
    
    def removeCard(self, cards):
        if not isinstance(cards, list):
            cards = [cards]
        for c in cards:
            if c in self.GBcards:
             self.GBcards.remove(c)
    
    def removeAll(self):
        self.GBcards.clear() 

