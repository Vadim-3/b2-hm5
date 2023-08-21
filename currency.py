import asyncio
import aiohttp
import sys

async def fetch_exchange_rates(session, days):
    url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={days}'

    async with session.get(url) as response:
        data = await response.json()
        return data

async def get_rates(days, currencies):
    async with aiohttp.ClientSession() as session:
        data = await fetch_exchange_rates(session, days)
        exchange_rates = data['exchangeRate']

        result = []
        for rate in exchange_rates:
            if rate['currency'] in currencies:
                date = rate['date']
                currency = rate['currency']
                sale = rate['saleRateNB']
                purchase = rate['purchaseRateNB']

                result.append({
                    date: {
                        currency: {
                            'sale': sale,
                            'purchase': purchase
                        }
                    }
                })

        return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <days> <currency1> <currency2> ...")
        return

    try:
        days = int(sys.argv[1])
        if days > 10:
            print("Error: Days cannot be more than 10.")
            return

        currencies = sys.argv[2:]
        if not currencies:
            print("Error: At least one currency must be provided.")
            return

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(get_rates(days, currencies))
        print(result)

    except ValueError:
        print("Error: Days must be a valid integer.")

if __name__ == "__main__":
    main()