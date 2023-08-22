import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
import ssl
import sys

class PrivatBankAPI:
    BASE_URL = "https://api.privatbank.ua/p24api/"

    def __init__(self):
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    async def fetch_exchange_rates(self, date):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_ctx)) as session:
            url = f"{self.BASE_URL}exchange_rates?json&date={date}"
            async with session.get(url) as response:
                return await response.json()

    async def get_currency_rates(self, date):
        data = await self.fetch_exchange_rates(date)
        return data

def get_date_range(start_date, end_date, max_days):
    dates = []
    current_date = end_date - timedelta(days=max_days - 1)
    while current_date <= end_date:
        dates.append(current_date.strftime("%d.%m.%Y"))
        current_date += timedelta(days=1)
    return dates

async def get_rates_for_dates(api, dates):
    tasks = [api.get_currency_rates(date) for date in dates]
    return await asyncio.gather(*tasks)

def format_currency_data(data):
    formatted_data = []
    for rates in data:
        formatted_rates = {}
        for rate in rates['exchangeRate']:
            if rate['currency'] in ('EUR', 'USD'):
                formatted_rates[rate['currency']] = {
                    'sale': rate['saleRate'],
                    'purchase': rate['purchaseRate']
                }
        formatted_data.append({rates['date']: formatted_rates})
    return formatted_data

async def main():
    if len(sys.argv) != 2:
        print("Usage: py .\\main.py <number of days>")
        return

    try:
        max_days = int(sys.argv[1])
        if max_days > 10:
            print("Maximum number of days allowed is 10.")
            return
    except ValueError:
        print("Invalid number of days.")
        return

    api = PrivatBankAPI()
    today = datetime.today()
    date_range = get_date_range(today - timedelta(days=max_days), today, max_days)
    currency_data = await get_rates_for_dates(api, date_range)
    formatted_data = format_currency_data(currency_data)

    print(json.dumps(formatted_data, indent=2))

if __name__ == "__main__":
    asyncio.run(main())