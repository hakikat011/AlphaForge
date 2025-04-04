"""
Basic Template Algorithm for QuantConnect LEAN
This is a simple moving average crossover strategy for demonstration purposes.
"""

from AlgorithmImports import *

class BasicTemplateAlgorithm(QCAlgorithm):
    def Initialize(self):
        """Initialize the algorithm with basic settings."""
        self.SetStartDate(2020, 1, 1)  # Set Start Date
        self.SetEndDate(2023, 12, 31)  # Set End Date
        self.SetCash(100000)  # Set Strategy Cash
        
        # Add SPY as a default symbol
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        # Define the moving average periods
        self.fast_period = 50
        self.slow_period = 200
        
        # Create the moving average indicators
        self.fast_ma = self.SMA(self.symbol, self.fast_period, Resolution.Daily)
        self.slow_ma = self.SMA(self.symbol, self.slow_period, Resolution.Daily)
        
        # Set the benchmark to SPY
        self.SetBenchmark("SPY")
        
        # Set the brokerage model
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
        # Set the risk management
        self.Settings.MaximumOrderQuantity = 10000
        
        # Set the warm-up period
        self.SetWarmUp(self.slow_period)
        
    def OnData(self, data):
        """Event handler for market data updates."""
        # Skip if we're still in the warm-up period
        if self.IsWarmingUp:
            return
        
        # Skip if we don't have data for our symbol
        if not data.ContainsKey(self.symbol):
            return
        
        # Skip if the moving averages aren't ready
        if not self.fast_ma.IsReady or not self.slow_ma.IsReady:
            return
        
        # Get the current holdings
        holdings = self.Portfolio[self.symbol].Quantity
        
        # Check for a buy signal: fast MA crosses above slow MA
        if self.fast_ma.Current.Value > self.slow_ma.Current.Value and holdings <= 0:
            # Calculate the quantity to buy
            price = data[self.symbol].Close
            quantity = self.CalculateOrderQuantity(self.symbol, 0.95)  # Use 95% of portfolio
            
            # Place the buy order
            self.MarketOrder(self.symbol, quantity)
            self.Log(f"BUY {quantity} shares of {self.symbol} at {price}")
        
        # Check for a sell signal: fast MA crosses below slow MA
        elif self.fast_ma.Current.Value < self.slow_ma.Current.Value and holdings > 0:
            # Place the sell order
            self.Liquidate(self.symbol)
            self.Log(f"SELL {holdings} shares of {self.symbol}")
    
    def OnOrderEvent(self, orderEvent):
        """Event handler for order status updates."""
        self.Log(f"Order event: {orderEvent}")
