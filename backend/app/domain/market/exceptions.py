class MarketError(Exception):
    """Base exception for Kunora market domain."""

class InstrumentNotFoundError(MarketError):
    def __init__(self, instrument_id: str) -> None:
        self.instrument_id = instrument_id

        super().__init__(
            f"Instrument '{instrument_id}' was not found."
        )

class MarketDataUnavailableError(MarketError):
    def __init__(
        self, 
        message: str = "Market data is temporarily unavailable.",
    ) -> None:

        super().__init__(message)

class MarketDataValidationError(MarketError):
    """Raised when external market data cannot be normalized safely."""