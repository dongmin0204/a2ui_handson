import json
import urllib.request
import urllib.error

# 실시간 API가 실패할 때 사용할 모의 데이터
MOCK_MARKET = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "price_usd": 107250.42,
        "change_24h_pct": 2.35,
        "market_cap_usd": 2_130_000_000_000,
        "volume_24h_usd": 38_500_000_000,
        "high_24h": 108_900.00,
        "low_24h": 104_100.00,
    },
    # ... (나머지 코인은 solution 참고)
]

COIN_IDS = "bitcoin,ethereum,solana,ripple,cardano"
SYMBOL_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "cardano": "ADA",
}


def get_prices() -> list[dict]:
    """Get current cryptocurrency market data for top 5 coins.

    Returns a list of coins, each with:
    - symbol: ticker (BTC, ETH, etc.)
    - name: full name
    - price_usd: current price in USD
    - change_24h_pct: 24-hour price change percentage
    - market_cap_usd: market capitalization in USD
    - volume_24h_usd: 24-hour trading volume in USD
    - high_24h / low_24h: 24-hour price range

    Fetches live data from CoinGecko API. Falls back to mock data on failure.
    """
    # TODO: CoinGecko API를 호출하여 실시간 데이터를 가져오세요.
    # 힌트:
    #   url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={COIN_IDS}&order=market_cap_desc"
    #   urllib.request.urlopen(req, timeout=5) 로 호출
    #   실패 시 MOCK_MARKET 반환
    return MOCK_MARKET
