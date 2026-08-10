from enum import StrEnum

class AssetClass(StrEnum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"
    INDEX = "index"
    BOND = "bond"
    RATE = "rate"
    ETF = "etf"
    FUND = "fund"
    OPTION = "option"
    FUTURE = "future"
    EQUITY = "equity"

class InstrumentType(StrEnum):
    SPOT = "spot"
    FUTURE = "future"
    PERPETUAL = "perpetual"
    OPTION = "option"
    INDEX = "index"
    RATE = "rate"

class MarketStatus(StrEnum):
    ACTIVE = "active"
    HALTED = "halted"
    DELISTED = "delisted"
    UNKNOWN = "unknown"

class TradeSide(StrEnum):
    BUY = "buy"
    SELL = "sell"
    UNKNOWN = "unknown"

class CandleInterval(StrEnum):
    ONE_MINUTE = "1m"
    THREE_MINUTES = "3m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"

    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    TWELVE_HOURS = "12h"

    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"
    ONE_YEAR = "1y"