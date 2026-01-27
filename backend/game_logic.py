import random
from typing import List, Tuple, Set

class BingoCardGenerator:
    @staticmethod
    def generate_card() -> List[List[int]]:
        """Generate a 5x5 bingo card"""
        card = []
        ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
        
        for min_val, max_val in ranges:
            column = random.sample(range(min_val, max_val + 1), 5)
            card.append(column)
        
        # Transpose to make it row-major
        card = [[card[col][row] for col in range(5)] for row in range(5)]
        
        # Set center as FREE (0)
        card[2][2] = 0
        
        return card
    
    @staticmethod
    def generate_multiple_cards(count: int) -> List[List[List[int]]]:
        """Generate multiple unique bingo cards"""
        return [BingoCardGenerator.generate_card() for _ in range(count)]


class BingoGameLogic:
    def __init__(self):
        self.called_numbers: Set[int] = set()
        self.all_numbers: List[int] = list(range(1, 76))
        random.shuffle(self.all_numbers)
    
    def call_next_number(self) -> Tuple[int, str]:
        """Get next number to call"""
        if len(self.called_numbers) >= 75:
            return -1, ""
        
        number = self.all_numbers[len(self.called_numbers)]
        self.called_numbers.add(number)
        
        letter = self._get_letter(number)
        return number, letter
    
    def _get_letter(self, number: int) -> str:
        """Get bingo letter for a number"""
        if 1 <= number <= 15:
            return "B"
        elif 16 <= number <= 30:
            return "I"
        elif 31 <= number <= 45:
            return "N"
        elif 46 <= number <= 60:
            return "G"
        else:
            return "O"
    
    def check_win(self, card: List[List[int]], marked_positions: List[List[bool]]) -> Tuple[bool, str]:
        """Check if card has a winning pattern"""
        # Check rows
        for i in range(5):
            if all(marked_positions[i]):
                return True, f"Row {i+1}"
        
        # Check columns
        for j in range(5):
            if all(marked_positions[i][j] for i in range(5)):
                return True, f"Column {j+1}"
        
        # Check diagonals
        if all(marked_positions[i][i] for i in range(5)):
            return True, "Diagonal \\"
        
        if all(marked_positions[i][4-i] for i in range(5)):
            return True, "Diagonal /"
        
        return False, ""
    
    def find_number_on_card(self, card: List[List[int]], number: int) -> Tuple[int, int]:
        """Find position of number on card"""
        for i in range(5):
            for j in range(5):
                if card[i][j] == number:
                    return i, j
        return -1, -1
