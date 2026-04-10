#!/usr/bin/env python3
"""
Fetch portfolio-aware news directly from Yahoo Finance.
Analyzes news for all holdings and correlates to portfolio impact.
"""
import yfinance as yf
import polars as pl
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from rendering.disclaimer_wrapper import DisclaimerWrapper
from rendering.compact_serializers import serialize_news_compact

# Phase 9: Mode and feature enforcement
try:
    from config.feature_manager import FeatureManager, FeatureNotAvailableError
    from config.config_loader import get_deployment_mode
    from config.deployment_modes import DeploymentMode, Feature
    from config.guardrail_enforcer import GuardrailEnforcer
    _features_available = True
except ImportError as e:
    _features_available = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """News article with sentiment and portfolio impact"""
    symbol: str
    title: str
    summary: str
    source: str
    link: str
    publish_date: str
    sentiment: str  # 'positive', 'negative', 'neutral'
    confidence: float  # 0-1
    portfolio_impact: float  # $ impact
    impact_pct: float  # % impact on holding

class PortfolioNewsAnalyzer:
    """Fetch and analyze news for portfolio holdings"""

    # Sentiment keywords for simple classification
    POSITIVE_KEYWORDS = [
        'beat', 'beats', 'surge', 'surges', 'gain', 'gains', 'profit', 'profits',
        'growth', 'grows', 'success', 'strong', 'strength', 'record', 'records',
        'rise', 'rises', 'rising', 'rally', 'rallies', 'upgrade', 'upgrades',
        'outperform', 'outperforms', 'bullish', 'partnership', 'partnerships',
        'acquisition', 'acquires', 'deal', 'deals', 'expansion', 'expands',
        'launch', 'launches', 'innovation', 'innovates', 'earnings', 'revenue',
        'revenues', 'margin', 'margins', 'exceeds', 'exceed', 'tops', 'topped',
        'boosts', 'boost', 'advances', 'advance', 'jumps', 'jump', 'climbs',
        'highest', 'soars', 'soar', 'wins', 'win', 'awarded', 'approved',
        'positive', 'optimistic', 'raised guidance', 'raises guidance', 'dividend',
        'buyback', 'buy back', 'stock split', 'profitable', 'narrowed loss',
    ]

    NEGATIVE_KEYWORDS = [
        'drop', 'drops', 'decline', 'declines', 'declining', 'loss', 'losses',
        'fall', 'falls', 'falling', 'crash', 'crashes', 'weakness', 'weak',
        'downgrade', 'downgrades', 'underperform', 'underperforms', 'bearish',
        'default', 'defaults', 'bankruptcy', 'bankrupt', 'scandal', 'scandals',
        'investigation', 'investigate', 'lawsuit', 'lawsuits', 'recall', 'recalls',
        'warning', 'warns', 'miss', 'misses', 'missed', 'cut guidance',
        'cuts guidance', 'restructuring', 'restructure', 'layoff', 'layoffs',
        'lays off', 'charges', 'writedown', 'write-down', 'impairment',
        'disappoints', 'disappointing', 'disappoints', 'plunges', 'plunge',
        'slumps', 'slump', 'tumbles', 'tumble', 'sinks', 'sink', 'loses',
        'concern', 'concerns', 'risk', 'risks', 'penalty', 'fine', 'fined',
        'fraud', 'probe', 'subpoena', 'negative', 'pessimistic', 'shortfall',
        'below expectations', 'missed estimates', 'wider loss',
    ]

    def __init__(self):
        self.portfolio_holdings = {}
        self.all_news = {}
        self.errors = []

    def load_holdings(self, holdings_file: str) -> None:
        """Load portfolio holdings from JSON"""
        try:
            from pathlib import Path
            path = Path(holdings_file).expanduser()

            with open(path, 'r') as f:
                data = json.load(f)

            # Support both schemas; handle wrapper 'data' key
            if 'data' in data:
                data = data['data']   # unwrap disclaimer wrapper

            if 'holdings' in data:
                holdings = data.get('holdings', [])
            elif 'portfolio' in data:
                # Convert portfolio schema to holdings list
                holdings = []
                portfolio = data['portfolio']
                for asset_type, assets in portfolio.items():
                    if isinstance(assets, dict):
                        for symbol, asset_data in assets.items():
                            entry = {'symbol': symbol, 'asset_type': asset_type}
                            if isinstance(asset_data, dict):
                                entry.update(asset_data)
                            holdings.append(entry)
            else:
                holdings = []

            for holding in holdings:
                symbol = holding.get('symbol', '').strip()
                current_price = holding.get('current_price', 0)
                value = holding.get('value', 0)
                asset_type = holding.get('asset_type', 'equity')

                if symbol and current_price > 0:
                    self.portfolio_holdings[symbol] = {
                        'current_price': current_price,
                        'value': value,
                        'asset_type': asset_type,
                        'shares': holding.get('shares', 1)
                    }

            logger.info(f"Loaded {len(self.portfolio_holdings)} holdings")

        except Exception as e:
            logger.error(f"Error loading holdings: {e}")
            raise

    def simple_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Simple sentiment analysis based on keywords.
        Returns: (sentiment, confidence)
        """
        if not text:
            return 'neutral', 0.0

        text_lower = text.lower()

        # Count keyword occurrences with word boundaries for better matching
        positive_count = 0
        negative_count = 0

        for kw in self.POSITIVE_KEYWORDS:
            # Count occurrences (can have multiple per text)
            positive_count += text_lower.count(kw)

        for kw in self.NEGATIVE_KEYWORDS:
            negative_count += text_lower.count(kw)

        total = positive_count + negative_count

        if total == 0:
            return 'neutral', 0.3  # Low confidence neutral

        if positive_count > negative_count:
            # Scale confidence: more keywords = higher confidence
            confidence = min(1.0, positive_count / max(10, total))
            return 'positive', confidence
        elif negative_count > positive_count:
            confidence = min(1.0, negative_count / max(10, total))
            return 'negative', confidence
        else:
            return 'neutral', 0.5

    @staticmethod
    def _articles_for_weight(weight_pct: float) -> int:
        """Return how many articles to fetch based on portfolio weight.

        Returns article count based on portfolio weight.
        More articles for larger positions improve sentiment quality.
        """
        if weight_pct >= 5.0:
            return 20
        elif weight_pct >= 2.0:
            return 15
        elif weight_pct >= 0.5:
            return 10
        else:
            return 5

    def fetch_symbol_news(self, symbol: str, max_articles: int = 10) -> List[Dict]:
        """Fetch news for a single symbol from Yahoo Finance"""
        try:
            logger.info(f"Fetching news for {symbol} (max {max_articles} articles)")
            ticker = yf.Ticker(symbol)

            # Get news from yfinance
            news = ticker.news

            if not news:
                logger.warning(f"No news found for {symbol}")
                return []

            processed_news = []

            for item in news[:max_articles]:  # adaptive depth
                try:
                    # Modern yfinance returns {'id': ..., 'content': {'title': ..., 'summary': ...}}
                    # Legacy format returns {'title': ..., 'summary': ...} at top level
                    _content = item.get('content', {})
                    if isinstance(_content, dict):
                        title = _content.get('title', '') or item.get('title', '')
                        summary = _content.get('summary', '') or _content.get('description', '') or item.get('summary', '')
                    else:
                        title = item.get('title', '')
                        summary = item.get('summary', '') or str(_content)
                    source = item.get('source', 'Unknown')
                    link = item.get('link', '')

                    # Try to parse publish date
                    pub_timestamp = item.get('providerPublishTime', 0)
                    if pub_timestamp:
                        pub_date = datetime.fromtimestamp(pub_timestamp).isoformat()
                    else:
                        pub_date = datetime.now().isoformat()

                    # Analyze sentiment from title + summary
                    combined_text = f"{title} {summary}"
                    sentiment, confidence = self.simple_sentiment(combined_text)

                    # Calculate portfolio impact
                    holding_value = self.portfolio_holdings[symbol]['value']

                    # Impact multiplier based on sentiment confidence
                    # Positive news could lift stock ~1-2%, negative could drop 1-3%
                    impact_multiplier = {
                        'positive': 0.015,  # 1.5% potential upside
                        'negative': -0.025,  # 2.5% potential downside
                        'neutral': 0.0
                    }

                    impact_pct = impact_multiplier.get(sentiment, 0.0) * confidence
                    portfolio_impact = holding_value * impact_pct

                    processed_news.append({
                        'symbol': symbol,
                        'title': title,
                        'summary': summary,
                        'source': source,
                        'link': link,
                        'publish_date': pub_date,
                        'sentiment': sentiment,
                        'confidence': float(confidence),
                        'portfolio_impact': float(portfolio_impact),
                        'impact_pct': float(impact_pct * 100)
                    })

                except Exception as e:
                    logger.warning(f"Error processing news item for {symbol}: {e}")
                    continue

            return processed_news

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            self.errors.append(f"Failed to fetch news for {symbol}: {e}")
            return []

    def fetch_all_news(self, holdings_file: str, output_file: str = None,
                       top_n: int = 30, cache_file: str = None) -> Dict:
        """Fetch news for top N holdings by portfolio weight.

        Only the top_n holdings (by $ value) are fetched.  Full article data
        is written to cache_file (separate from the agent-facing output) so
        on-demand per-symbol lookups work without re-fetching.  The agent-facing
        output (output_file / return value) is a compact digest — ~3K tokens
        instead of 300K+ for the full all_news array.
        """

        # Phase 9: Check feature availability
        if _features_available:
            try:
                mode_str = get_deployment_mode()
                mode = DeploymentMode(mode_str)
                fm = FeatureManager(mode)
                fm.require_feature(Feature.NEWS_SENTIMENT)  # Core feature, all modes
                logger.info(f"News sentiment analysis enabled for {mode_str} mode")
            except FeatureNotAvailableError as e:
                logger.error(f"News sentiment not available: {e}")
                raise

        self.load_holdings(holdings_file)

        total_holdings = len(self.portfolio_holdings)

        # Rank by portfolio value; fetch only the top_n
        ranked = sorted(
            self.portfolio_holdings.items(),
            key=lambda kv: kv[1]['value'],
            reverse=True
        )
        fetch_symbols = [sym for sym, _ in ranked[:top_n]]
        skipped_symbols = [sym for sym, _ in ranked[top_n:]]

        total_value = sum(h['value'] for h in self.portfolio_holdings.values()) or 1.0

        logger.info(
            f"Fetching news for top {len(fetch_symbols)} of {total_holdings} holdings "
            f"({len(skipped_symbols)} skipped — available on-demand)"
        )

        all_news_items = []
        positive_news = []
        negative_news = []
        per_symbol_cache: Dict[str, List[Dict]] = {}

        for symbol in fetch_symbols:
            holding_val = self.portfolio_holdings[symbol]['value']
            weight_pct  = holding_val / total_value * 100
            max_art = self._articles_for_weight(weight_pct)
            news_items = self.fetch_symbol_news(symbol, max_articles=max_art)
            per_symbol_cache[symbol] = news_items

            all_news_items.extend(news_items)

            for item in news_items:
                if item['sentiment'] == 'positive':
                    positive_news.append(item)
                elif item['sentiment'] == 'negative':
                    negative_news.append(item)

        # Sort by portfolio impact (absolute value)
        sorted_by_impact = sorted(
            all_news_items,
            key=lambda x: abs(x['portfolio_impact']),
            reverse=True
        )

        # Portfolio-level impact totals
        total_positive_impact = sum(i['portfolio_impact'] for i in positive_news)
        total_negative_impact = sum(i['portfolio_impact'] for i in negative_news)
        net_impact = total_positive_impact + total_negative_impact

        # Top movers (title + truncated summary only — keeps tokens low)
        def _compact_item(item: Dict) -> Dict:
            return {
                'symbol': item['symbol'],
                'title': item['title'],
                'summary': (item.get('summary') or '')[:300],
                'sentiment': item['sentiment'],
                'confidence': item['confidence'],
                'portfolio_impact': item['portfolio_impact'],
                'impact_pct': item['impact_pct'],
                'publish_date': item['publish_date'],
            }

        top_positive = [_compact_item(i) for i in
                        sorted(positive_news, key=lambda x: x['portfolio_impact'], reverse=True)[:5]]
        top_negative = [_compact_item(i) for i in
                        sorted(negative_news, key=lambda x: x['portfolio_impact'])[:5]]

        # Per-symbol digest: one row per fetched symbol — no full article text
        symbol_digest = []
        for symbol in fetch_symbols:
            items = per_symbol_cache.get(symbol, [])
            holding_val = self.portfolio_holdings[symbol]['value']
            if not items:
                continue
            top = sorted(items, key=lambda x: abs(x['portfolio_impact']), reverse=True)
            top_item = top[0] if top else {}
            pos = sum(1 for i in items if i['sentiment'] == 'positive')
            neg = sum(1 for i in items if i['sentiment'] == 'negative')
            overall    = 'positive' if pos > neg else ('negative' if neg > pos else 'neutral')
            confidence = max((i.get('confidence', 0.5) for i in items), default=0.5)
            article_digest = ''
            symbol_digest.append({
                'symbol':         symbol,
                'weight_pct':     round(holding_val / total_value * 100, 2),
                'article_count':  len(items),
                'sentiment':      overall,
                'confidence':     round(confidence, 2),
                'positive_count': pos,
                'negative_count': neg,
                'top_story':      top_item.get('title', ''),
                'digest':         article_digest,
            })

        macro_themes       = None
        portfolio_narrative = None

        compact_report = {
            'timestamp': datetime.now().isoformat(),
            'symbols_fetched': len(fetch_symbols),
            'symbols_skipped': len(skipped_symbols),
            'skipped_available_on_demand': True,
            'total_news_items': len(all_news_items),
            'portfolio_impact_summary': {
                'net_impact': float(net_impact),
                'positive_impact': float(total_positive_impact),
                'negative_impact': float(total_negative_impact),
                'impact_pct': float(net_impact / total_value * 100),
            },
            'sentiment_breakdown': {
                'positive_news_count': len(positive_news),
                'negative_news_count': len(negative_news),
                'neutral_news_count': len(all_news_items) - len(positive_news) - len(negative_news),
            },
            'top_positive_movers': top_positive,
            'top_negative_movers': top_negative,
            'symbol_digest': symbol_digest,
            'macro_themes':        macro_themes,
            'portfolio_narrative': portfolio_narrative,
            # NOTE: full article text is NOT included here — see cache file
            'errors': self.errors if self.errors else None,
        }

        # Write full article cache (agent never loads this directly)
        if cache_file:
            cache_data = {
                'timestamp': compact_report['timestamp'],
                'symbols': list(per_symbol_cache.keys()),
                'skipped_symbols': skipped_symbols,
                'all_news': sorted_by_impact,
                'per_symbol': per_symbol_cache,
            }
            from pathlib import Path
            Path(cache_file).parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            logger.info(f"Full news cache saved to {cache_file}")

        # Phase 9: Apply guardrails based on deployment mode
        if _features_available:
            try:
                mode_str = get_deployment_mode()
                mode = DeploymentMode(mode_str)
                enforcer = GuardrailEnforcer(mode)

                # Apply appropriate disclaimer based on mode
                news_text = json.dumps(compact_report, indent=2, default=str)
                enforcer.add_professional_disclaimer(news_text)
                logger.info(f"Applied {mode_str} guardrails and disclaimers")
            except Exception as e:
                logger.warning(f"Could not apply mode-specific guardrails: {e}")

        if output_file:
            result = DisclaimerWrapper.wrap_output(compact_report, "Portfolio News Analysis")
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Compact news digest saved to {output_file}")

        return compact_report

    def fetch_symbol_news_detail(self, symbol: str, cache_file: str) -> Optional[List[Dict]]:
        """Return full article list for a single symbol from the news cache.

        Used for on-demand per-symbol lookups without re-fetching everything.
        Returns None if symbol not in cache (caller should re-fetch).
        """
        from pathlib import Path
        path = Path(cache_file).expanduser()
        if not path.exists():
            return None
        try:
            with open(path) as f:
                cache = json.load(f)
            per_symbol = cache.get('per_symbol', {})
            if symbol in per_symbol:
                return per_symbol[symbol]
            # Symbol was in skipped_symbols — not in cache
            if symbol in cache.get('skipped_symbols', []):
                logger.info(f"{symbol} was skipped at fetch time — fetching now")
                # Load holdings to get portfolio context for impact calculation
                return None  # Caller must do a live fetch
            return None
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

if __name__ == '__main__':
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Fetch portfolio news')
    parser.add_argument('holdings_file', help='Path to holdings.json')
    parser.add_argument('output_file', nargs='?', help='Path for compact digest output (default: portfolio_news.json alongside holdings)')
    parser.add_argument('--symbol', '-s', help='On-demand: fetch full articles for this symbol only')
    parser.add_argument('--top-n', type=int, default=None,
                        help='Fetch news for top N holdings by value. '
                             'If omitted, the adaptive planner chooses automatically.')
    parser.add_argument('--model', '-m', default=None,
                        help='Model ID for adaptive planning (default: OPENCLAW_MODEL env)')
    parser.add_argument('--cache', help='Path for full article cache (default: portfolio_news_cache.json alongside output)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print narrative, macro themes, and top movers (default: compact summary only)')
    args = parser.parse_args()

    holdings_path = Path(args.holdings_file).expanduser()
    reports_dir = holdings_path.parent

    output_file = args.output_file or str(reports_dir / 'portfolio_news.json')
    cache_file = args.cache or str(reports_dir / 'portfolio_news_cache.json')

    # Auto-plan: if --top-n not given, run the adaptive planner
    top_n = args.top_n
    if top_n is None:
        try:
            from news_fetch_planner import NewsFetchPlanner
            plan = NewsFetchPlanner.make_plan_from_holdings_file(
                str(holdings_path), model_id=args.model
            )
            top_n = plan.recommended_top_n
            logger.info(
                f"Adaptive plan: top_n={top_n}, coverage={plan.coverage_pct}%, "
                f"~{plan.estimated_news_tokens:,} tokens — {plan.reason}"
            )
            # Save plan alongside digest for agent visibility
            plan_file = str(reports_dir / 'portfolio_news_plan.json')
            with open(plan_file, 'w') as _pf:
                json.dump(plan.to_dict(), _pf, indent=2)
        except Exception as e:
            logger.warning(f"Adaptive planner unavailable ({e}), using default top_n=30")
            top_n = 30

    analyzer = PortfolioNewsAnalyzer()

    # On-demand single-symbol mode
    if args.symbol:
        symbol = args.symbol.upper()
        items = analyzer.fetch_symbol_news_detail(symbol, cache_file)
        if items is None:
            # Not in cache — live fetch (load holdings for impact calculation)
            analyzer.load_holdings(str(holdings_path))
            if symbol not in analyzer.portfolio_holdings:
                print(f"⚠️  {symbol} not found in portfolio holdings.")
                sys.exit(1)
            items = analyzer.fetch_symbol_news(symbol)
        print(f"\n{'='*60}")
        print(f"NEWS FOR {symbol} ({len(items)} articles)")
        print('='*60)
        for item in items:
            print(f"\n📰 {item['title']}")
            if item.get('summary'):
                print(f"   {item['summary'][:300]}")
            print(f"   Sentiment: {item['sentiment']} ({item['confidence']:.0%}) | "
                  f"Impact: ${item['portfolio_impact']:+,.0f}")
        sys.exit(0)

    report = analyzer.fetch_all_news(
        str(holdings_path),
        output_file=output_file,
        top_n=top_n,
        cache_file=cache_file,
    )

    # Emit compact JSON to stdout for LLM (full digest is in portfolio_news.json — do not read it)
    report['output_file'] = output_file or ""
    print(json.dumps(serialize_news_compact(report), separators=(',', ':'), default=str))

    if args.verbose:
        # Narrative
        if narr:
            print(f"\nPortfolio Posture: {posture}")
            print(f"  {narr.get('narrative', '')}")
            for tw in narr.get('key_tailwinds', []):
                print(f"  + {tw}")
            for risk in narr.get('key_risks', []):
                print(f"  - {risk}")

        # Macro themes
        themes_data = report.get('macro_themes')
        if themes_data and themes_data.get('themes'):
            print("\nMACRO THEMES")
            for t in themes_data['themes']:
                arrow = "^" if t['direction'] == 'bullish' else ("v" if t['direction'] == 'bearish' else "-")
                syms = ", ".join(t['affected_symbols'][:6])
                print(f"  {arrow} {t['theme']} ({t['portfolio_weight_pct']:.1f}%) — {syms}")

        # Top movers
        print("\nTOP POSITIVE NEWS")
        for item in report['top_positive_movers'][:3]:
            print(f"  {item['symbol']}: {item['title'][:70]} | +${item['portfolio_impact']:,.0f}")
        print("TOP NEGATIVE NEWS")
        for item in report['top_negative_movers'][:3]:
            print(f"  {item['symbol']}: {item['title'][:70]} | ${item['portfolio_impact']:,.0f}")
