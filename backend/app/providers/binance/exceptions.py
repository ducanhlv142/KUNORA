class BinanceError(Exception):
    """Base exception for Binance provider failures."""

class BinanceNetworkError(BinanceError):
    """Network, connection or timeout failure."""

class BinanceRateLimitError(BinanceError):
    """Binance rate limit was exceeded."""

class BinanceResponseError(BinanceError):
    """Binance returned an unexpected or invalid response."""