# bitcoinbot
Quantitative Cryptocurrency Trading Platform (Bitcoin)

🎯 What Is This?

A beginner-friendly Bitcoin trading bot that combines three powerful technical indicators (RSI, MACD, Supertrend) to make automated buy/sell decisions. Unlike typical trading bots, this platform teaches you by showing exactly why each trade was executed.
​
Perfect for learning algorithmic trading without risking real money.

✨ Key Features

🤖 Smart Trading Logic — When 2 out of 3 indicators agree, the bot trades
​
📚 Educational Feedback — See RSI values, MACD crossovers, and Supertrend signals after every trade
​
⚖️ 3 Risk Levels — Adjust trading aggressiveness and indicator sensitivity
​
📈 Live Charts — Real-time visualization of all indicators and price action

🕐 Historical Backtesting — Test strategies on past data before going live
​
💾 Trade History — Complete database of past trades with profit/loss tracking


🧮 How It Works
The platform uses quantitative analysis with three technical indicators:

​
Indicator	What It Does	Buy Signal	Sell Signal
RSI	Measures momentum	< 30 (oversold)	> 70 (overbought)
MACD	Detects trend changes	Line crosses above signal	Line crosses below signal
Supertrend	Volatility-based trends	Price above band	Price below band
Decision Rule: Trades execute when at least 2 indicators agree.

​
Example Trade Breakdown
text
✅ BUY Signal Triggered
├─ RSI: 28.4 (Oversold ✓)
├─ MACD: Bullish crossover ✓
├─ Supertrend: Neutral ✗
└─ Result: 2/3 indicators agree → EXECUTE BUY

🎓 Why Use This?

Problem: 95% of traders lose money because they trade emotionally without understanding technical analysis.

Solution: This platform automates trading while showing you the "why" behind each decision. After 10-20 trades, you'll understand RSI oversold conditions, MACD crossovers, and trend following.

Educational Focus: Built from interviews with beginner traders who wanted to learn, not just earn.

📁 Project Structure
text
├── main.py              # Launch application
├── ui.py                # Tkinter GUI (login, dashboard, charts, history)
├── activate_bot.py      # Core trading engine
├── bot_indicators.py    # RSI, MACD, Supertrend calculations
├── api.py               # Binance API integration
├── database.py          # SQLite database operations
├── auth.py              # User authentication & password hashing
└── btccschart.py        # Matplotlib chart generation
Database: 6 tables including user profiles, trade history, application logs, and risk configurations.


⚙️ Configuration
Risk Levels
Each level adjusts 5+ parameters:
Level 1 (Low): 10% investment per trade, conservative RSI thresholds (30/70)
Level 2 (Medium): 20% investment, moderate sensitivity (40/60)
Level 3 (High): 40% investment, aggressive signals (45/55)
Trading Modes
Live: Uses current Binance API data for real-time decisions
Historical: Backtests on past 100+ days of Bitcoin price history
​

🛡️ Disclaimer

⚠️ Educational Use Only — This is a paper trading platform (no real money involved)
​
⚠️ Not Financial Advice — Technical indicators can fail; past performance ≠ future results
​
⚠️ API Limitations — Subject to Binance rate limits and potential downtime

