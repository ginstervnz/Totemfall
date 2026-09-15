import random
import settings
from src.entities.cards.DamageCard import DamageCard
from src.entities.cards.SpeedUpCard import SpeedUpCard
from src.entities.cards.AtkSpeedUp import AtkSpeedUP
from src.entities.cards.ManaUp import ManaUP
from src.entities.cards.ManaReduce import ManaReduce
from src.entities.cards.ShootSpeed import ShootSpeed
from src.entities.cards.MoreMana import MoreMana
from src.entities.cards.HealTotem import HealTotem
from src.entities.cards.XPBoost import XPBoost
from src.entities.cards.SummonUnlockCard import SummonUnlockCard
from src.entities.cards.SummonSlotCard import SummonSlotCard
from src.entities.cards.AllyDamageCard import AllyDamageCard
# Import your other cards here as you create them


class CardManager:
    def __init__(self):
        # Pool of all possible upgrades in the game
        self.available_cards = [DamageCard,SpeedUpCard,AtkSpeedUP,
                                ManaUP,ManaReduce,ShootSpeed,
                                MoreMana,HealTotem,XPBoost,
                                SummonUnlockCard
                                ] 
        # When you add more, just put them in the list:
        # self.available_cards = [DamageCard, ManaCard, SpeedCard]


    def unlock_summon_upgrades(self) -> None:
        """Removes the base unlock card and adds the slot upgrade card."""
        if SummonUnlockCard in self.available_cards:
            self.available_cards.remove(SummonUnlockCard)

        if SummonSlotCard not in self.available_cards:
            self.available_cards.append(SummonSlotCard)

        if AllyDamageCard not in self.available_cards:
            self.available_cards.append(AllyDamageCard)

    def get_random_hand(self, amount: int = 3) -> list:
        """Picks random cards and positions them evenly on the screen."""
        hand = []
        
        # Safety check in case we request more cards than available classes
        if amount > len(self.available_cards):
            amount = len(self.available_cards)
            
        # Pick unique cards (so you don't get 3 identical Damage cards)
        chosen_classes = random.sample(self.available_cards, amount)
        
        # Math to center the cards nicely on the screen
        card_width = 72
        card_height = 96
        spacing = 20
        total_width = (card_width * amount) + (spacing * (amount - 1))
        
        start_x = (settings.VIRTUAL_WIDTH / 2) - (total_width / 2)
        # Start far below the screen so they can tween upwards
        start_y = settings.VIRTUAL_HEIGHT + 150
        
        # Instantiate them with their calculated X and Y positions
        for i, card_class in enumerate(chosen_classes):
            card_x = start_x + (i * (card_width + spacing))
            new_card = card_class(card_x, start_y)
            hand.append(new_card)
            
        return hand