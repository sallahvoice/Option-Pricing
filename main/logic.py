from typing import Dict
from numpy import exp, sqrt, log
from scipy.stats import norm

from exceptions import QueryError
from repositories.input_repo import InputRepository
from db.migrate import run_migration
from logger import get_logger

logger = get_logger(__file__)


def input_table_entry(current_inputs: Dict[str, float]):
    try:
        repo = InputRepository()
        repo.create_input(current_inputs)
    except Exception as e:
        logger.error(f"Failed to insert inputs: {e}")
        raise


def price_option(inputs: Dict[str, float]):
    try:
        S = inputs["StockPrice"]
        K = inputs["StrikePrice"]
        T = inputs["TimeToExpiry"]
        r = inputs["RiskFreeRate"]
        sigma = inputs["Volatility"]
    except KeyError as e:
        raise QueryError(f"Missing input: {e}")

    if T <= 0 or sigma <= 0:
        raise QueryError("TimeToExpiry and Volatility must be positive")

    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    Nd1  = norm.cdf(d1)
    Nd2  = norm.cdf(d2)
    Nmd1 = norm.cdf(-d1)
    Nmd2 = norm.cdf(-d2)
    nd1  = norm.pdf(d1)

    call_price = S * Nd1 - K * exp(-r * T) * Nd2
    put_price  = K * exp(-r * T) * Nmd2 - S * Nmd1

    call_delta = Nd1
    put_delta  = Nd1 - 1

    gamma = nd1 / (S * sigma * sqrt(T))

    return {
        "call_price": call_price,
        "put_price": put_price,
        "call_delta": call_delta,
        "put_delta": put_delta,
        "call_gamma": gamma,
        "put_gamma": gamma,
    }


def entry_price(entry_inputs: Dict[str, float]):
    prices = price_option(entry_inputs)
    return {
        "call_entry": prices["call_price"],
        "put_entry": prices["put_price"],
    }


def pnl(current_inputs: Dict[str, float], entry_inputs: Dict[str, float]):
    entry = entry_price(entry_inputs)
    current = price_option(current_inputs)

    return {
        "call_pnl": current["call_price"] - entry["call_entry"],
        "put_pnl": current["put_price"] - entry["put_entry"],
    }


if __name__ == "__main__":
    run_migration()

    entry_inputs = {
        "StockPrice": 50,
        "StrikePrice": 40,
        "TimeToExpiry": 2.5,
        "RiskFreeRate": 0.04,
        "Volatility": 0.4,
    }

    current_inputs = {
        "StockPrice": 45,
        "StrikePrice": 40,
        "TimeToExpiry": 2.0,
        "RiskFreeRate": 0.04,
        "Volatility": 0.35,
    }

    print(entry_price(entry_inputs))
    print(pnl(current_inputs, entry_inputs))