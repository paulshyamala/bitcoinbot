# 📊 Quantitative Cryptocurrency Trading Platform (Bitcoin)

> Learn technical analysis while an AI bot trades Bitcoin for you — and explains every decision.

  

***

## 🎯 What Is This?

A **beginner-friendly Bitcoin trading bot** that combines three powerful technical indicators (RSI, MACD, Supertrend) to make automated buy/sell decisions. Unlike typical trading bots, this platform **teaches you** by showing exactly why each trade was executed.[1]

Perfect for learning algorithmic trading without risking real money.

![App Screenshot - Add your main dashboard screenshot here]

***

## ✨ Key Features

🤖 **Smart Trading Logic** — When 2 out of 3 indicators agree, the bot trades[1]
📚 **Educational Feedback** — See RSI values, MACD crossovers, and Supertrend signals after every trade[1]
⚖️ **3 Risk Levels** — Adjust trading aggressiveness and indicator sensitivity[1]
📈 **Live Charts** — Real-time visualization of all indicators and price action  
🕐 **Historical Backtesting** — Test strategies on past data before going live[1]
💾 **Trade History** — Complete database of past trades with profit/loss tracking[1]

***

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/quant-crypto-platform.git
cd quant-crypto-platform
pip install tkinter matplotlib pandas requests
python main.py
```

### First Steps

1. **Create Account** — Register with username and password
2. **Choose Risk Level** — Select 1 (Conservative), 2 (Moderate), or 3 (Aggressive)
3. **Pick Trading Mode** — Live (real-time) or Historical (backtesting)
4. **Activate Bot** — Watch it analyze Bitcoin and make trades
5. **Review Trades** — Learn from detailed breakdowns of each decision

![Trading Flow GIF - Add animated demo here]

***

## 🧮 How It Works

The platform uses **quantitative analysis** with three technical indicators:[1]

| Indicator | What It Does | Buy Signal | Sell Signal |
|-----------|--------------|------------|-------------|
| **RSI** | Measures momentum | < 30 (oversold) | > 70 (overbought) |
| **MACD** | Detects trend changes | Line crosses above signal | Line crosses below signal |
| **Supertrend** | Volatility-based trends | Price above band | Price below band |

**Decision Rule**: Trades execute when at least 2 indicators agree.[1]

### Example Trade Breakdown

```
✅ BUY Signal Triggered
├─ RSI: 28.4 (Oversold ✓)
├─ MACD: Bullish crossover ✓
├─ Supertrend: Neutral ✗
└─ Result: 2/3 indicators agree → EXECUTE BUY
```

![Indicator Charts - Add screenshot of the 4-panel visualization]

***

## 🎓 Why Use This?

**Problem**: 95% of traders lose money because they trade emotionally without understanding technical analysis.[1]

**Solution**: This platform automates trading while showing you the "why" behind each decision. After 10-20 trades, you'll understand RSI oversold conditions, MACD crossovers, and trend following.[1]

**Educational Focus**: Built from interviews with beginner traders who wanted to learn, not just earn.[1]

***

## 📁 Project Structure

```
├── main.py              # Launch application
├── ui.py                # Tkinter GUI (login, dashboard, charts, history)
├── activate_bot.py      # Core trading engine
├── bot_indicators.py    # RSI, MACD, Supertrend calculations
├── api.py               # Binance API integration
├── database.py          # SQLite database operations
├── auth.py              # User authentication & password hashing
└── btccschart.py        # Matplotlib chart generation
```

**Database**: 6 tables including user profiles, trade history, application logs, and risk configurations.[1]

***

## ⚙️ Configuration

### Risk Levels

Each level adjusts 5+ parameters:[1]

- **Level 1 (Low)**: 10% investment per trade, conservative RSI thresholds (30/70)
- **Level 2 (Medium)**: 20% investment, moderate sensitivity (40/60)
- **Level 3 (High)**: 40% investment, aggressive signals (45/55)

### Trading Modes

- **Live**: Uses current Binance API data for real-time decisions
- **Historical**: Backtests on past 100+ days of Bitcoin price history[1]

***

## 🛡️ Disclaimer

⚠️ **Educational Use Only** — This is a paper trading platform (no real money involved)[1]
⚠️ **Not Financial Advice** — Technical indicators can fail; past performance ≠ future results[1]
⚠️ **API Limitations** — Subject to Binance rate limits and potential downtime[1]

***

## 🤝 Contributing

This is an A-Level Computer Science project. Contributions welcome for:[1]
- Additional indicators (Bollinger Bands, Stochastic)
- Multi-asset support (Ethereum, altcoins)
- Improved backtesting engine
- Mobile app version

***

## 📄 License

MIT License — Free to use for educational purposes.

***

## 🙏 Acknowledgments

Built as an AQA Computer Science NEA by Paul Shyamala. Research based on trader interviews and analysis of platforms like Binance.[1]

**Tech**: Python -  Tkinter -  Matplotlib -  Pandas -  SQLite -  Binance API

***

**Questions?** Open an issue or check the [Wiki](link-to-wiki) for detailed documentation.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/69557010/cdc88ba4-d491-48d7-b385-618b2cdddc64/CS-NEA-Crypto-Bot-3.1-Final.docx)
