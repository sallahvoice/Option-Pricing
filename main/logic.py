from exceptions import (FailedToFetchData, TickerNotFound, QueryError)
from db.migrate import run_migration
from repositories.input_repo import InputRepository
from repositories.output_repo import OutputRepository
from logger import get_logger
from typing import Dict

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
    vol = inputs["Volatility"]

    d1 = 
    d2 =
    nd1 = 
    nd2 = 
    call_price = 
    put_price =  



if __name__ == "__main__":
    inputs = {"StockPrice": 50,
            "StrikePrice": 40,
            "TimeToExpiry": 2.5,
            "RiskFreeRate": 0.04,
            "Volatility": 0.4}
    price_option(inputs)
    