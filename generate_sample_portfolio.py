#!/usr/bin/env python3
# Copyright 2026 InvestorClaw Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Generate comprehensive sample portfolio covering all CDM asset types.
Anonymized $100M portfolio for open-source demo.

Output: portfolios/sample_$100M.csv (usable with ic-holdings)
"""

import csv
import random
from datetime import datetime
from pathlib import Path

# Asset class definitions with realistic ranges
EQUITIES = {
    "AAPL": ("Apple", 175.32, 1.15, 2021),
    "MSFT": ("Microsoft", 420.87, 1.08, 2020),
    "GOOGL": ("Alphabet", 140.50, 1.20, 2019),
    "AMZN": ("Amazon", 180.42, 0.95, 2018),
    "NVDA": ("NVIDIA", 850.00, 1.50, 2021),
    "TSM": ("Taiwan Semiconductor", 110.25, 1.10, 2020),
    "META": ("Meta", 480.00, 1.25, 2021),
    "TSLA": ("Tesla", 242.84, 0.85, 2020),
    "JNJ": ("Johnson & Johnson", 155.30, 1.02, 2010),
    "WMT": ("Walmart", 82.45, 0.90, 2015),
    "PG": ("Procter & Gamble", 165.50, 1.05, 2005),
    "KO": ("Coca-Cola", 61.20, 0.92, 2010),
    "JPM": ("JPMorgan Chase", 195.75, 1.08, 2015),
    "GS": ("Goldman Sachs", 410.20, 1.12, 2018),
    "XOM": ("Exxon Mobil", 105.30, 0.88, 2012),
    "CVX": ("Chevron", 155.60, 0.95, 2015),
    "MRK": ("Merck", 330.10, 1.10, 2015),
    "LLY": ("Eli Lilly", 755.40, 1.35, 2020),
    "UNH": ("UnitedHealth", 485.20, 1.18, 2018),
    "AZN": ("AstraZeneca", 80.50, 1.08, 2015),
    "PEP": ("PepsiCo", 182.75, 0.98, 2012),
    "MCD": ("McDonald's", 295.50, 1.05, 2015),
    "V": ("Visa", 267.40, 1.15, 2018),
    "MA": ("Mastercard", 515.20, 1.20, 2018),
    "DIS": ("Disney", 92.35, 0.85, 2015),
    "NFLX": ("Netflix", 415.00, 1.30, 2018),
    "INTC": ("Intel", 42.50, 0.70, 2015),
    "AMD": ("Advanced Micro Devices", 185.00, 1.25, 2018),
    "QCOM": ("Qualcomm", 175.30, 1.10, 2015),
    "AVGO": ("Broadcom", 755.00, 1.15, 2018),
    "CSCO": ("Cisco", 53.20, 0.92, 2010),
    "CRM": ("Salesforce", 245.00, 1.08, 2015),
    "NOW": ("ServiceNow", 620.00, 1.30, 2018),
    "ADBE": ("Adobe", 585.00, 1.18, 2015),
    "PYPL": ("PayPal", 60.50, 0.95, 2015),
    "SQ": ("Square", 70.25, 1.10, 2015),
    "UBER": ("Uber", 75.80, 1.05, 2019),
    "COIN": ("Coinbase", 120.50, 1.40, 2021),
    "ARM": ("Arm Holdings", 128.75, 1.45, 2023),
}

BONDS = {
    "MUNI_CA": ("California State Muni 2051", 102.50, 4.5, 100000, 2051),
    "MUNI_NY": ("New York State Muni 2050", 101.20, 4.3, 75000, 2050),
    "MUNI_TX": ("Texas Muni 2049", 103.10, 4.1, 50000, 2049),
    "CORP_IBM": ("IBM Corporate Bond 2035", 98.50, 5.2, 100000, 2035),
    "CORP_GE": ("General Electric Bond 2040", 95.80, 5.5, 75000, 2040),
    "CORP_MS": ("Morgan Stanley Bond 2045", 96.20, 5.3, 50000, 2045),
    "CORP_JPM": ("JPMorgan Bond 2038", 99.50, 4.8, 100000, 2038),
    "TREAS_10Y": ("US Treasury 10Y Note", 99.75, 4.2, 200000, 2034),
    "TREAS_20Y": ("US Treasury 20Y Bond", 95.50, 4.5, 150000, 2044),
}

CRYPTO = {
    "BTC-USD": ("Bitcoin", 42500.00, 0.50),
    "ETH-USD": ("Ethereum", 2250.00, 5.00),
    "SOL-USD": ("Solana", 85.50, 20.00),
    "ADA-USD": ("Cardano", 0.85, 1000.00),
    "DOGE-USD": ("Dogecoin", 0.12, 5000.00),
}

FUTURES = {
    "/ESU24": ("E-mini S&P 500 Sept 2024", 5285.50, 50),
    "/NQU24": ("E-mini NASDAQ Sept 2024", 18750.00, 25),
    "/CLU24": ("WTI Crude Oil Aug 2024", 82.50, 10),
    "/GCU24": ("Gold Futures Aug 2024", 2050.00, 5),
    "/ZBU24": ("30Y US Bond Futures Aug 2024", 126.00, 3),
}

METALS = {
    "GLD": ("SPDR Gold Shares", 195.30, 5000),
    "SLV": ("iShares Silver Trust", 28.75, 2000),
    "GDX": ("VanEck Gold Miners ETF", 35.20, 1500),
}


def random_date(start_year=2015, end_year=2024):
    """Generate random acquisition date."""
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe day for all months
    return f"{year}-{month:02d}-{day:02d}"


def generate_portfolio(portfolio_value=100_000_000):
    """Generate $100M sample portfolio with all CDM asset types."""
    rows = []

    # Allocation percentages by asset class
    alloc = {
        "equity": 0.58,
        "bond": 0.28,
        "crypto": 0.04,
        "metals": 0.02,
        "futures": 0.05,  # notional, backed by cash
        "cash": 0.03,
    }

    # EQUITIES (~58% = $58M)
    equity_value = portfolio_value * alloc["equity"]
    equity_syms = list(EQUITIES.keys())
    random.shuffle(equity_syms)
    equity_per_position = equity_value / len(equity_syms)

    for i, sym in enumerate(equity_syms):
        name, price, volatility, buy_year = EQUITIES[sym]
        qty = int(equity_per_position / price)
        cost_basis = price * (0.8 + random.random() * 0.4)  # 80%-120% of current
        rows.append(
            {
                "Account": f"Brokerage-{i % 3 + 1}",
                "Type": "Stock",
                "Symbol": sym,
                "Name": name,
                "Shares": str(qty),
                "Price": f"{price:.2f}",
                "Value": f"{qty * price:.2f}",
                "Cost Basis": f"{qty * cost_basis:.2f}",
                "Date Acquired": random_date(buy_year),
            }
        )

    # BONDS (~28% = $28M)
    bond_value = portfolio_value * alloc["bond"]
    bond_syms = list(BONDS.keys())
    bond_per_position = bond_value / len(bond_syms)

    for i, sym in enumerate(bond_syms):
        name, price, coupon_rate, par, maturity_year = BONDS[sym]
        qty = int(bond_per_position / (price * 1000))  # Bonds in $1000 par units
        rows.append(
            {
                "Account": f"Brokerage-{i % 3 + 1}",
                "Type": "Bond",
                "Symbol": sym,
                "Name": name,
                "Shares": str(qty),
                "Price": f"{price:.2f}",
                "Value": f"{qty * price * 1000:.2f}",
                "Cost Basis": f"{qty * 1000:.2f}",
                "Date Acquired": random_date(2015),
            }
        )

    # CRYPTO (~4% = $4M)
    crypto_value = portfolio_value * alloc["crypto"]
    crypto_syms = list(CRYPTO.keys())
    crypto_value / len(crypto_syms)

    for i, sym in enumerate(crypto_syms):
        name, price, qty = CRYPTO[sym]
        value = price * qty
        cost_basis = price * (0.5 + random.random() * 1.0)  # Wide range for crypto
        rows.append(
            {
                "Account": "Crypto-Exchange",
                "Type": "Crypto",
                "Symbol": sym,
                "Name": name,
                "Shares": f"{qty:.4f}",
                "Price": f"{price:.2f}",
                "Value": f"{value:.2f}",
                "Cost Basis": f"{qty * cost_basis:.2f}",
                "Date Acquired": random_date(2020),
            }
        )

    # METALS (~2% = $2M)
    metals_value = portfolio_value * alloc["metals"]
    metals_syms = list(METALS.keys())
    metals_value / len(metals_syms)

    for i, sym in enumerate(metals_syms):
        name, price, qty = METALS[sym]
        value = price * qty
        cost_basis = price * (0.7 + random.random() * 0.6)
        rows.append(
            {
                "Account": "Brokerage-1",
                "Type": "Metal ETF",
                "Symbol": sym,
                "Name": name,
                "Shares": str(qty),
                "Price": f"{price:.2f}",
                "Value": f"{value:.2f}",
                "Cost Basis": f"{qty * cost_basis:.2f}",
                "Date Acquired": random_date(2018),
            }
        )

    # FUTURES (~5% notional = $5M)
    # Note: Futures are leveraged, so smaller actual positions
    futures_syms = list(FUTURES.keys())

    for sym in futures_syms:
        name, price, qty = FUTURES[sym]
        value = price * qty * 50  # Contract multiplier (ES=50, NQ=20, etc)
        cost_basis = price  # Futures are marked-to-market
        rows.append(
            {
                "Account": "Futures-Account",
                "Type": "Futures",
                "Symbol": sym,
                "Name": name,
                "Shares": str(qty),
                "Price": f"{price:.2f}",
                "Value": f"{value:.2f}",
                "Cost Basis": f"{value:.2f}",
                "Date Acquired": random_date(2023),
            }
        )

    # CASH (~3% = $3M)
    cash_value = portfolio_value * alloc["cash"]
    rows.append(
        {
            "Account": "Brokerage-1",
            "Type": "Cash",
            "Ticker": "USD",
            "Name": "US Dollar",
            "Shares": str(cash_value),
            "Price": "1.00",
            "Value": f"{cash_value:.2f}",
            "Cost Basis": f"{cash_value:.2f}",
            "Date Acquired": datetime.now().strftime("%Y-%m-%d"),
        }
    )

    return rows


def main():
    # Create portfolios directory
    portfolio_dir = Path(__file__).parent / "portfolios"
    portfolio_dir.mkdir(exist_ok=True)

    # Generate sample portfolio
    rows = generate_portfolio()

    # Write CSV
    csv_file = portfolio_dir / "sample_$100M.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Account",
                "Type",
                "Symbol",
                "Name",
                "Shares",
                "Price",
                "Value",
                "Cost Basis",
                "Date Acquired",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Generated sample portfolio: {csv_file}")
    print(f"   • {len(rows)} positions total")
    print(f"   • {len([r for r in rows if r['Type'] == 'Stock'])} equities")
    print(f"   • {len([r for r in rows if r['Type'] == 'Bond'])} bonds")
    print(f"   • {len([r for r in rows if r['Type'] == 'Crypto'])} crypto")
    print(f"   • {len([r for r in rows if r['Type'] == 'Metal ETF'])} metals")
    print(f"   • {len([r for r in rows if r['Type'] == 'Futures'])} futures")
    print("   • 1 cash position")
    print("\nUsage: ic-holdings portfolios/sample_\\$100M.csv")


if __name__ == "__main__":
    main()
