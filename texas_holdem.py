import random
from enum import Enum

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.name} of {self.suit.value}"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
    
    def receive_card(self, card):
        self.hand.append(card)
    
    def bet(self, amount):
        if amount > self.chips:
            amount = self.chips
        self.chips -= amount
        return amount

class GTOStrategy:
    @staticmethod
    def evaluate_hand_strength(hole_cards, community_cards):
        """评估手牌强度(0-1)"""
        # 简化版手牌强度评估
        high_card = max(card.rank.value for card in hole_cards)
        return high_card / 14
        
    @staticmethod
    def calculate_equity(hole_cards, community_cards, pot_odds):
        """计算权益与赔率"""
        hand_strength = GTOStrategy.evaluate_hand_strength(hole_cards, community_cards)
        return hand_strength > pot_odds
        
    @staticmethod
    def get_position_adjustment(position, total_players):
        """根据位置调整策略"""
        return (total_players - position) / total_players

class TexasHoldem:
    def __init__(self, player_names):
        self.players = [Player(name) for name in player_names]
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_round = 0
    
    def deal_hole_cards(self):
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.deal())
    
    def deal_flop(self):
        # Burn one card
        self.deck.deal()
        # Deal 3 community cards
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
    
    def deal_turn_or_river(self):
        # Burn one card
        self.deck.deal()
        # Deal 1 community card
        self.community_cards.append(self.deck.deal())
    
    def betting_round(self):
        for player in self.players:
            self.display_game_state(player)
            if player.name == "Player1":  # Human player
                while True:
                    try:
                        print("\nOptions: 1) Check 2) Bet 3) Fold")
                        choice = int(input("Enter your choice: "))
                        if choice == 1:  # Check
                            bet_amount = 0
                            print("\nGTO提示: 检查是当前回合的合理选择")
                            break
                        elif choice == 2:  # Bet
                            bet_amount = int(input("Enter bet amount: "))
                            # 简化版GTO评估逻辑
                            position = self.players.index(player)
                            pot_odds = bet_amount / (bet_amount + self.pot) if self.pot > 0 else 0
                            hand_strength = GTOStrategy.evaluate_hand_strength(player.hand, self.community_cards)
                            position_adjustment = GTOStrategy.get_position_adjustment(position, len(self.players))
                            
                            if GTOStrategy.calculate_equity(player.hand, self.community_cards, pot_odds):
                                if bet_amount >= 50 * (1 + position_adjustment) and len(self.community_cards) < 3:
                                    print("\nGTO提示: 强牌+有利位置，下注金额符合GTO策略")
                                elif bet_amount < 50 * (1 + position_adjustment) and len(self.community_cards) >= 3:
                                    print(f"\nGTO提示: 建议下注{int(50 * (1 + position_adjustment))}以上")
                                else:
                                    print("\nGTO提示: 下注金额在合理范围内")
                            else:
                                print("\nGTO提示: 权益不足，建议弃牌或控制下注")
                            break
                        elif choice == 3:  # Fold
                            print("\nGTO提示: 弃牌可能是正确的选择")
                            return False
                        else:
                            print("Invalid choice")
                    except ValueError:
                        print("Please enter a valid number")
            else:  # AI player
                position = self.players.index(player)
                pot_odds = 0.3  # 默认赔率
                hand_strength = GTOStrategy.evaluate_hand_strength(player.hand, self.community_cards)
                position_adjustment = GTOStrategy.get_position_adjustment(position, len(self.players))
                
                if GTOStrategy.calculate_equity(player.hand, self.community_cards, pot_odds):
                    bet_amount = int(50 * (1 + position_adjustment) * hand_strength)
                else:
                    bet_amount = 0 if random.random() < 0.7 else int(30 * hand_strength)
            
            self.pot += player.bet(bet_amount)
        return True
    
    def determine_winner(self):
        # Simplified winner determination
        if len(self.players) == 0:
            return None
        return random.choice(self.players)
    
    def display_game_state(self, player):
        print("\n=== Current Game State ===")
        print(f"Player: {player.name}")
        print(f"Chips: {player.chips}")
        print("\nYour Hand:")
        for card in player.hand:
            print(f"  {card}")
        print("\nCommunity Cards:")
        for card in self.community_cards:
            print(f"  {card}")
        print(f"\nPot: {self.pot}")
    
    def play_round(self):
        self.deal_hole_cards()
        if not self.betting_round():
            return
        
        self.deal_flop()
        if not self.betting_round():
            return
        
        self.deal_turn_or_river()  # Turn
        if not self.betting_round():
            return
        
        self.deal_turn_or_river()  # River
        if not self.betting_round():
            return
        
        winner = self.determine_winner()
        winner.chips += self.pot
        self.pot = 0
        
        # Reset for next round
        self.deck = Deck()
        self.community_cards = []
        for player in self.players:
            player.hand = []
        
        return winner

if __name__ == "__main__":
    game = TexasHoldem(["Player1", "Player2"])
    winner = game.play_round()
    if winner:
        print(f"The winner is {winner.name} with {winner.chips} chips!")
    else:
        print("Game ended early with no winner.")