class InMemoryDB:
    def __init__(self):
        self.previous_gold_price = None

    def get_previous_gold_price(self) -> float | None:
        return self.previous_gold_price

    def set_gold_price(self, price: float):
        self.previous_gold_price = price

# Global instance to hold state during the app lifecycle
db = InMemoryDB()
