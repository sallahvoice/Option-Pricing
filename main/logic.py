from exceptions import (FailedToFetchData, TickerNotFound, QueryError)
from db.migrate import run_migration
from repositories.input_repo import InputRepository
from repositories.output_repo import OutputRepository
from logger import get_logger
from typing import Dict
from numpy import exp, sqrt, log
from scipy.stats import norm

logger = get_logger(__file__)
run_migration()

def input_table_entry(inputs: Dict[str, float]): #includes stock price, vol..
    if not InputRepository:
        logger.error("failed to import class InputRepository")
    input_repo = InputRepository()
    if not input_repo:
        logger.error("failed to initialize object from class InputRepository")
    input_repo.create_input(inputs)

def price_option(inputs: Dict[str, float]):
    #shock?, sentivize
    stock_price = inputs["StockPrice"]
    strike_price = inputs["StrikePrice"]
    time = inputs["TimeToExpiry"]
    rf = inputs["RiskFreeRate"]
    vol = inputs["Volatility"] #std

    d1 = (log(stock_price / strike_price) 
        + (rf + 0.5 * vol**2) * time) / (vol * sqrt(time))

    d2 = d1 - vol * sqrt(time)

    call_price = (
        stock_price * norm.cdf(d1)
        - strike_price * exp(-rf * time) * norm.cdf(d2)
    )

    put_price = (
        strike_price * exp(-rf * time) * norm.cdf(-d2)
        - stock_price * norm.cdf(-d1)
    )

    call_delta = norm.cdf(d1)
    put_delta = norm.cdf(d1) - 1

    call_gamma = norm.pdf(d1)/(stock_price*vol*sqrt(time_to_expiry))
    put_gamma = call_gamma

if __name__ == "__main__":
    inputs = {"StockPrice": 50,
            "StrikePrice": 40,
            "TimeToExpiry": 2.5,
            "RiskFreeRate": 0.04,
            "Volatility": 0.4}
    price_option(inputs)
    