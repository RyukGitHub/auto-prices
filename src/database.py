"""In-memory state store for tracking the previous Gold price between runs."""


class InMemoryDB:
    """Simple in-memory database that stores the last-seen Gold price."""

    def __init__(self):
        """Initialise with no prior price data."""
        self.previous_gold_price = None

    def get_previous_gold_price(self) -> float | None:
        """Return the stored Gold price, or None if not yet set."""
        return self.previous_gold_price

    def set_gold_price(self, price: float):
        """Store the latest Gold price, overwriting any previous value."""
        self.previous_gold_price = price


# Global singleton to hold state during the app lifecycle
db = InMemoryDB()
