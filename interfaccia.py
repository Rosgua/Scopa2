import streamlit as st
import os
import random

from gestione_mazzo import Deck, Card, GameBoard
from gestione_giocatori import HumanPlayer, PlayerAI, str_to_card
from gs import GameSystem, TurnManager 

# Questo è fondamentale perché Streamlit riesegue lo script ad ogni interazione
# e dobbiamo mantenere lo stato del gioco.
if 'game_system' not in st.session_state:
    st.session_state.game_system = GameSystem()
    st.session_state.game_started = False
    st.session_state.username = ""
    st.session_state.messages = [] # Per i messaggi di stato del gioco
    st.session_state.player_card_choice = None # Non più usato per selectbox, ma può essere utile per altro
    st.session_state.current_turn_player_name = "Human" # Imposta il giocatore umano come iniziale
    st.session_state.current_player_object = None # Sarà impostato in start_game_logic
    st.session_state.game_over = False # NUOVO STATO: per indicare che la partita è finita e mostrare i risultati
    #st.session_state.final_results_message = "" # NUOVO STATO: per salvare il messaggio dei risultati

# Funzione per aggiungere messaggi alla UI
def add_message(message):
    st.session_state.messages.append(message)

# Classe UserInterface per Streamlit (Adattata)
class StreamlitUI:
    def __init__(self, gs_instance):
        self.gs = gs_instance

    def display_game_board(self):
        if self.gs.gameboard.GBcards:
            return self.gs.gameboard.GBcards
        else:
            return []

    def _on_card_button_click(self, card_str_choice):
        if handle_player_turn(card_str_choice):
            # 2. Se la mossa è valida, controlla se le carte devono essere ridistribuite o la partita è finita
            if not check_and_redistribute_cards():
                end_game_logic()
                st.rerun() 
            else:
                # 3. Avanza il turno nel TurnManager
                self.gs.TurnManager.nextTurn()
                # 4. Aggiorna lo stato della sessione per indicare che è il turno dell'AI
                st.session_state.current_turn_player_name = "AI"
                st.session_state.current_player_object = self.gs.playerAI
                # 5. Forza il ricaricamento dell'interfaccia per mostrare il turno dell'AI
                st.rerun() 
        else:
            # Se la mossa non è valida, il messaggio è già stato aggiunto in handle_player_turn
            pass # Non fare nulla, l'interfaccia rimarrà invariata in attesa di una mossa valida

    def display_player_hand(self):
        if self.gs.Hplayer.handCard:
            return self.gs.Hplayer.handCard
        else:
            return []

    def display_messages(self):
        for msg in st.session_state.messages:
            st.info(msg)
        st.session_state.messages = []

# --- Funzioni del Gioco ---

def start_game_logic():
    st.session_state.game_system = GameSystem() # Re-inizializza il sistema di gioco
    gs = st.session_state.game_system
    
    # Inizializza il gioco con l'username e un'istanza "fittizia" di UI per il GameSystem
    gs.startGame(st.session_state.username) # Passiamo un'istanza della UI per Streamlit

    #add_message("Partita iniziata!")
    #add_message(f"Giocatore: {gs.Hplayer.username}, AI: {gs.playerAI.__class__.__name__}")
    
    # Distribuisci le carte iniziali (già fatto in gs.startGame)
    #add_message("Carte distribuite!")
    
    # Imposta il primo turno per il giocatore umano
    st.session_state.game_started = True
    st.session_state.current_turn_player_name = "Human" # Ora inizia l'umano
    st.session_state.current_player_object = gs.Hplayer # Aggiorna l'oggetto giocatore corrente
    st.rerun() 

def handle_player_turn(card_str_choice):
    gs = st.session_state.game_system
    
    try:
        chosen_card = str_to_card(card_str_choice)
        
        # Verifica se la carta è effettivamente nella mano del giocatore prima di giocarla
        if chosen_card not in gs.Hplayer.handCard:
            add_message(f"La carta '{card_str_choice}' non è nella tua mano. Scegli una carta valida.")
            return False # La mossa non è valida

        add_message(f"{gs.Hplayer.username} gioca: {card_str_choice}")
        result = gs.Hplayer.playCard(card_str_choice) # playCard dovrebbe rimuovere la carta dalla mano
        if result =='Scopa':
            add_message(f"Risultato della tua mossa : {result}")
    
        st.session_state.game_system = gs # Aggiorna lo stato in sessione
        return True # Mossa completata con successo
    except Exception as e:
        add_message(f"Errore giocando la tua carta: {e}")
        return False # Mossa fallita


def handle_ai_turn():
    gs = st.session_state.game_system
    add_message("--- Turno AI ---")
    
    card_ai_str = gs.playerAI.chooseMove()
    if not card_ai_str:
        add_message("AI non è riuscita a scegliere una mossa valida e non ha carte per un fallback.")
    # Validazione aggiuntiva per la mossa dell'AI
    chosen_card = str_to_card(card_ai_str)
    if chosen_card not in gs.playerAI.handCard:
        add_message(f"AI ha tentato di giocare una carta non valida o non in mano: {card_ai_str}. Scegliendo una carta valida casuale.")
        if gs.playerAI.handCard:
            fallback_choice = random.choice(gs.playerAI.handCard)
            card_ai_str = f"{fallback_choice.number} di {fallback_choice.suit}"
            add_message(f"AI ripiega su mossa casuale: {card_ai_str}")
        else:
            add_message("AI non ha carte da giocare per il fallback.")
            return True # Continua, anche se non ha giocato
    
    add_message(f"AI gioca: {card_ai_str}")
    result = gs.playerAI.playCard(card_ai_str)
    if result =='Scopa':
        add_message(f"Risultato della mossa dell'AI: {result}")
    
    st.session_state.game_system = gs
    return True


def check_and_redistribute_cards():
    gs = st.session_state.game_system
    if not gs.Hplayer.handCard and not gs.playerAI.handCard:
        if gs.deck.cards:
            add_message("=== Nuova distribuzione di carte ===")
            gs.deck.distribute(gs.Hplayer)
            gs.deck.distribute(gs.playerAI)
            st.session_state.game_system = gs
        else:
            return False
    return True


def end_game_logic():
    gs = st.session_state.game_system
    add_message("Partita terminata!")
    
    gs.calculateScores()
    results = gs.endGame()
    st.session_state.final_results_message = results # Salva i risultati nello stato
    st.session_state.game_started = False # Imposta lo stato di gioco a finito
    st.session_state.game_over = True # Imposta lo stato di fine partita

    

# --- Layout dell'interfaccia Streamlit ---

st.set_page_config(layout="wide")
st.title("🃏 Gioco della Scopa 🌿")


if not st.session_state.game_started:
    st.session_state.username = st.text_input("Inserisci il tuo username:", value=st.session_state.username, key="username_input")
    
    if st.button("Inizia Partita", key="start_game_button"):
        if st.session_state.username:
            #add_message(f"Preparazione partita per {st.session_state.username}...")
            start_game_logic()
        else:
            st.warning("Per favore, inserisci un username.")

else:
    gs = st.session_state.game_system
    ui = StreamlitUI(gs) # L'istanza di UI viene creata ad ogni rerun

   # 1. Area per i messaggi (in alto)
    st.subheader("📢")
    ui.display_messages() # Questa funzione ora svuota anche la lista dei messaggi
    st.write("---")

    # 2. Carte sul tavolo (al centro)
    st.subheader("🃍 Carte sul tavolo:")
    board_cards = ui.display_game_board() # Ottieni le carte dal game board
    if board_cards:
        col_left_space, col_board_cards, col_right_space = st.columns([1, 2, 1])
        with col_board_cards: 
            board_cols = st.columns(4)
            for i, card in enumerate(board_cards):
                with board_cols[i % 4]:
                    st.markdown(f"<div class='card-box'>{card.number} di {card.suit}</div>", unsafe_allow_html=True)
    else:
        st.write("🕳️ [Tavolo vuoto]")
    st.write("---")

    # 3. Informazioni sul turno e logica di gioco (sotto il tavolo)
    st.subheader(f"🎯 Turno di: {st.session_state.game_system.Hplayer.username}")

    if st.session_state.current_turn_player_name == "Human":
        st.write("👇 Scegli una carta dalla tua mano:")
        # 4. Carte del player (sotto le informazioni sul turno)
        player_hand_cards = ui.display_player_hand()
        if player_hand_cards:
            player_hand_cols = st.columns(3) 
            for i, card in enumerate(player_hand_cards):
                with player_hand_cols[i %3]:
                    st.button(
                        f"{card.number} di {card.suit}",
                        key=f"player_card_{card.number}_{card.suit}_{i}",
                        on_click=ui._on_card_button_click,
                        args=(f"{card.number} di {card.suit}",)
                    )
        else:
            st.write("🚫 [La tua mano è vuota]")

    else: # Turno AI
        st.write("🤖 L'AI sta pensando alla sua mossa...")
        
        # Esegui la logica dell'AI
        if handle_ai_turn():
            # Dopo la mossa, controlla e ridistribuisci se necessario
            if not check_and_redistribute_cards():
                end_game_logic()
                st.rerun()
            else:
                gs.TurnManager.nextTurn()
                st.session_state.current_turn_player_name = "Human"
                st.session_state.current_player_object = gs.Hplayer
                st.rerun()
        else:
            pass # Non fare nulla se la mossa dell'AI ha avuto problemi
    
    
if st.session_state.game_over:
    # Mostra i risultati finali se la partita è finita
    st.subheader("🎉 Partita Terminata!")
    st.subheader("Risultati Finali:")
    
    st.markdown(
    f"<div style='color: orange; font-size: 20px;'>{st.session_state.final_results_message}</div>",
    unsafe_allow_html=True
)
    st.rerun()




st.markdown("""
    <style>
        /* Sfondo principale verde scuro */
        body, [data-testid="stAppViewContainer"] {
            background-color: #0b3d0b;
            color: #f0f0f0;  /* testo bianco sporco */
        }

        /* Titoli */
        .stTitle, .stHeader, .stSubheader {
            color: #f0f0f0;
        }/* Sezioni con bordo */
        .section {
            border: 2px solid #228b22;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            background-color: #124d12;
        }

        /* Messaggi */
        .stAlert > div {
            background-color: #1e6f1e !important;
            color: white !important;
            border-radius: 8px;
        }

        /* --- BOTTONI GENERICI (funziona per st.button) --- */
        button {
            background-color: #34c759 !important;
            color: black !important;
            border: 2px solid #0a4d0a !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            font-size: 16px !important;
            padding: 0.5rem 1rem !important;
        }

        button:hover {
            background-color: #ccffcc !important;
            color: #0f3d0f !important;
        }

        /* Riquadri carte */
        .card-box {
            border: 2px solid #81c784;
            background-color: #1e4d1e;
            border-radius: 10px;
            padding: 8px;
            margin: 5px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

