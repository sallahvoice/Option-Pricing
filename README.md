# Option Pricing with Black-Scholes Model

A Python-based option pricing calculator that implements the Black-Scholes model with sensitivity analysis capabilities. The application computes option prices and stores both inputs and outputs in MySQL database tables.

## Overview

This project provides a complete option pricing solution that:
- Calculates European option prices using the Black-Scholes formula
- Performs sensitivity analysis by shocking input parameters (volatility and stock price)
- Stores all calculation inputs in the `BlackScholesInputs` table
- Stores all calculation outputs in the `BlackScholesOutputs` table
- Links inputs and outputs through a relational database structure

## Features

### Black-Scholes Inputs
The model accepts the five standard Black-Scholes parameters:
- **Stock Price (S)**: Current price of the underlying asset
- **Strike Price (K)**: Exercise price of the option
- **Time to Expiry (T)**: Time until option expiration (in years)
- **Risk-Free Rate (r)**: Annualized risk-free interest rate
- **Volatility (σ)**: Annualized volatility of the underlying asset

### Sensitivity Analysis
The application allows you to sensitize/shock input parameters:
- **Volatility Shock**: Test different volatility scenarios
- **Stock Price Shock**: Test different stock price scenarios
- Computes option prices for both **Call** and **Put** options

### Database Integration

#### BlackScholesInputs Table
Stores the base input parameters for each calculation:
- `CalculationId`: Unique identifier for each calculation
- `StockPrice`, `StrikePrice`, `TimeToExpiry`, `RiskFreeRate`, `Volatility`
- Timestamps for creation and updates

#### BlackScholesOutputs Table
Stores the results of each calculation with applied shocks:
- `CalculationOutputId`: Unique identifier for each output
- `CalculationId`: Foreign key linking to the input set
- `VolatilityShock`: Volatility adjustment applied
- `StockPriceShock`: Stock price adjustment applied
- `OptionPrice`: Calculated option price
- `IsCall`: Flag indicating Call (1) or Put (0) option
- Timestamps for creation and updates

**Database Relationship**: The tables are connected via a foreign key constraint, ensuring referential integrity. When an input record is deleted, all associated output records are automatically removed (CASCADE).

## Project Structure

```
Option-Pricing/
├── db/
│   ├── config.py           # Database configuration
│   ├── engine.py           # Database connection engine
│   ├── migrate.py          # Migration runner
│   ├── migrations/         # SQL migration files
│   │   └── 001_input_output_table.sql
│   └── repositories/       # Data access layer
│       ├── base_repo.py    # Base repository with CRUD operations
│       ├── input_repo.py   # BlackScholesInputs repository
│       └── output_repo.py  # BlackScholesOutputs repository
├── decorators.py           # Utility decorators
├── exceptions.py           # Custom exceptions
├── logger.py              # Logging configuration
└── .env                   # Environment variables (database credentials)
```

## Setup

### Prerequisites
- Python 3.x
- MySQL database server
- Required Python packages: `mysql-connector-python`

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install mysql-connector-python
   ```

3. Configure database connection in `.env` file:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=option_pricing
   ```

4. Run migrations to create database tables:
   ```bash
   python db/migrate.py
   ```

## Usage

The repository pattern provides CRUD operations for managing inputs and outputs:

### Creating a Calculation
```python
from db.repositories.input_repo import InputRepo
from db.repositories.output_repo import OutputRepo

# Store input parameters
input_repo = InputRepo("BlackScholesInputs", "CalculationId")
calc_id = input_repo.create({
    "StockPrice": 100.00,
    "StrikePrice": 105.00,
    "TimeToExpiry": 1.0,
    "RiskFreeRate": 0.05,
    "Volatility": 0.20
})

# Store output with sensitivity analysis
output_repo = OutputRepo("BlackScholesOutputs", "CalculationOutputId")
output_repo.create({
    "CalculationId": calc_id,
    "VolatilityShock": 0.05,
    "StockPriceShock": 2.00,
    "OptionPrice": 8.916,
    "IsCall": 1
})
```

### Retrieving Data
```python
# Get all inputs
inputs = input_repo.find_all()

# Get specific calculation outputs
outputs = output_repo.find_by_id(calc_id)
```

## Architecture

- **Repository Pattern**: Abstracted data access through `BaseRepository` with specialized repositories for inputs and outputs
- **Database Engine**: Centralized connection management with context managers for safe cursor handling
- **Migration System**: SQL-based migrations for version-controlled database schema evolution
- **Logging**: Centralized logging for debugging and monitoring



#TODO LIST:
1. Greeks Visualization Dashboard 📈
Difficulty: Medium

Add interactive line charts showing how Greeks (Delta, Gamma, Vega, Theta, Rho) change with:

Varying spot prices
Time to expiration (decay curves)
Volatility changes


Use Plotly for interactive hover tooltips
Impact: Helps users understand option sensitivities visually

2. Option Strategy Builder 🎯
Difficulty: Medium-Hard

Let users combine multiple options (spreads, straddles, butterflies, iron condors)
Show combined PnL profiles
Calculate max profit/loss, breakeven points
Save and compare different strategies
Impact: Transforms from single-option calculator to full strategy tool

3. Historical Volatility Calculator 📊
Difficulty: Medium

Integrate with free API (Yahoo Finance, Alpha Vantage)
Fetch real stock prices
Calculate historical volatility (20-day, 30-day, etc.)
Auto-populate volatility field with real data
Show volatility percentile vs historical range
Impact: Adds real market data integration