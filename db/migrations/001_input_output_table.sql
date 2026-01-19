"""file that creates mysql tables for our blackscholes inputs & outputs"""

CREATE TABLE IF NOT EXISTS BlackScholesInputs (
    CalculationId INT NOT NULL AUTO_INCREMENT,
    StockPrice DECIMAL(18,8) NOT NULL,
    StrikePrice DECIMAL(18,6) NOT NULL,
    TimeToExpiry DECIMAL(18,8) NOT NULL,
    RiskFreeRate DECIMAL(18,8) NOT NULL,
    Volatility DECIMAL(18,8) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (CalculationId),
    INDEX idx_bs_inputs_expiry (TimeToExpiry),
    INDEX idx_bs_inputs_vol (Volatility)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS BlackScholesOutputs (
    CalculationOutputId INT NOT NULL AUTO_INCREMENT,
    CalculationId INT NOT NULL,

    VolatilityShock DECIMAL(18,8) NOT NULL,
    StockPriceShock DECIMAL(18,8) NOT NULL,
    OptionPrice DECIMAL(18,6) NOT NULL,
    IsCall TINYINT(1) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (CalculationOutputId),

    INDEX idx_bs_outputs_calcid (CalculationId),
    INDEX idx_bs_outputs_calcid_iscall (CalculationId, IsCall),

    CONSTRAINT FK_BlackScholesInputs_BlackScholesOutputs
        FOREIGN KEY (CalculationId)
        REFERENCES BlackScholesInputs (CalculationId)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
