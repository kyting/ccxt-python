# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import hashlib
import json
from ccxt.base.errors import ArgumentsRequired


class southxchange(Exchange):

    def describe(self):
        return self.deep_extend(super(southxchange, self).describe(), {
            'id': 'southxchange',
            'name': 'SouthXchange',
            'countries': ['AR'],  # Argentina
            'rateLimit': 1000,
            'has': {
                'cancelOrder': True,
                'CORS': True,
                'createDepositAddress': True,
                'createOrder': True,
                'fetchBalance': True,
                'fetchDeposits': True,
                'fetchLedger': True,
                'fetchMarkets': True,
                'fetchOpenOrders': True,
                'fetchOrderBook': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchTrades': True,
                'fetchTransactions': True,
                'fetchWithdrawals': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27838912-4f94ec8a-60f6-11e7-9e5d-bbf9bd50a559.jpg',
                'api': 'https://www.southxchange.com/api',
                'www': 'https://www.southxchange.com',
                'doc': 'https://www.southxchange.com/Home/Api',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',
                        'price/{symbol}',
                        'prices',
                        'book/{symbol}',
                        'trades/{symbol}',
                    ],
                },
                'private': {
                    'post': [
                        'cancelMarketOrders',
                        'cancelOrder',
                        'getOrder',
                        'generatenewaddress',
                        'listOrders',
                        'listBalances',
                        'listTransactions',
                        'placeOrder',
                        'withdraw',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'maker': 0.1 / 100,
                    'taker': 0.3 / 100,
                },
            },
            'commonCurrencies': {
                'SMT': 'SmartNode',
                'MTC': 'Marinecoin',
                'BHD': 'Bithold',
            },
        })

    async def fetch_markets(self, params={}):
        markets = await self.publicGetMarkets(params)
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            baseId = market[0]
            quoteId = market[1]
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            id = baseId + '/' + quoteId
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': None,
                'info': market,
                'precision': self.precision,
                'limits': self.limits,
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostListBalances(params)
        result = {'info': response}
        for i in range(0, len(response)):
            balance = response[i]
            currencyId = self.safe_string(balance, 'Currency')
            code = self.safe_currency_code(currencyId)
            deposited = self.safe_float(balance, 'Deposited')
            unconfirmed = self.safe_float(balance, 'Unconfirmed')
            account = self.account()
            account['free'] = self.safe_float(balance, 'Available')
            account['total'] = self.sum(deposited, unconfirmed)
            result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        request = {
            'symbol': self.market_id(symbol),
        }
        response = await self.publicGetBookSymbol(self.extend(request, params))
        return self.parse_order_book(response, None, 'BuyOrders', 'SellOrders', 'Price', 'Amount')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'Last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'Bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'Ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': self.safe_float(ticker, 'Variation24Hr'),
            'average': None,
            'baseVolume': self.safe_float(ticker, 'Volume24Hr'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        response = await self.publicGetPrices(params)
        tickers = self.index_by(response, 'Market')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            symbol = id
            market = None
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        response = await self.publicGetPriceSymbol(self.extend(request, params))
        return self.parse_ticker(response, market)

    def parse_trade(self, trade, market):
        timestamp = self.safe_timestamp(trade, 'At')
        price = self.safe_float(trade, 'Price')
        amount = self.safe_float(trade, 'Amount')
        cost = None
        if price is not None:
            if amount is not None:
                cost = price * amount
        side = self.safe_string(trade, 'Type')
        symbol = None
        if market is not None:
            symbol = market['symbol']
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': None,
            'order': None,
            'type': None,
            'side': side,
            'price': price,
            'takerOrMaker': None,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        response = await self.publicGetTradesSymbol(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def parse_order(self, order, market=None):
        status = 'open'
        baseId = self.safe_string(order, 'ListingCurrency')
        quoteId = self.safe_string(order, 'ReferenceCurrency')
        base = self.safe_currency_code(baseId)
        quote = self.safe_currency_code(quoteId)
        symbol = base + '/' + quote
        timestamp = None
        price = self.safe_float(order, 'LimitPrice')
        amount = self.safe_float(order, 'OriginalAmount')
        remaining = self.safe_float(order, 'Amount')
        filled = None
        cost = None
        if amount is not None:
            cost = price * amount
            if remaining is not None:
                filled = amount - remaining
        type = 'limit'
        side = self.safe_string_lower(order, 'Type')
        id = self.safe_string(order, 'Code')
        result = {
            'info': order,
            'id': id,
            'clientOrderId': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': cost,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': None,
            'average': None,
            'trades': None,
        }
        return result

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        response = await self.privatePostListOrders(params)
        return self.parse_orders(response, market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'listingCurrency': market['base'],
            'referenceCurrency': market['quote'],
            'type': side,
            'amount': amount,
        }
        if type == 'limit':
            request['limitPrice'] = price
        response = await self.privatePostPlaceOrder(self.extend(request, params))
        return {
            'info': response,
            'id': str(response),
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        request = {
            'orderCode': id,
        }
        return await self.privatePostCancelOrder(self.extend(request, params))

    async def create_deposit_address(self, code, params={}):
        await self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
        }
        response = await self.privatePostGeneratenewaddress(self.extend(request, params))
        #
        # the exchange API returns a quoted-quoted-string
        #
        #     "\"0x4d43674209fcb66cc21469a6e5e52de7dd5bcd93\""
        #
        address = response
        if address[0] == '"':
            address = json.loads(address)
            if address[0] == '"':
                address = json.loads(address)
        parts = address.split('|')
        numParts = len(parts)
        address = parts[0]
        self.check_address(address)
        tag = None
        if numParts > 1:
            tag = parts[1]
        return {
            'currency': code,
            'address': address,
            'tag': tag,
            'info': response,
        }

    async def withdraw(self, code, amount, address, tag=None, params={}):
        self.check_address(address)
        await self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
            'address': address,
            'amount': amount,
        }
        if tag is not None:
            request['address'] = address + '|' + tag
        response = await self.privatePostWithdraw(self.extend(request, params))
        return {
            'info': response,
            'id': None,
        }

    def parse_ledger_entry_type(self, type):
        types = {
            'trade': 'trade',
            'tradefee': 'fee',
            'withdraw': 'transaction',
            'deposit': 'transaction',
        }
        return self.safe_string(types, type, type)

    def parse_ledger_entry(self, item, currency=None):
        #
        #     {
        #         "Date":"2020-08-07T12:36:52.72",
        #         "CurrencyCode":"USDT",
        #         "Amount":27.614678000000000000,
        #         "TotalBalance":27.614678000000000000,
        #         "Type":"deposit",
        #         "Status":"confirmed",
        #         "Address":"0x4d43674209fcb66cc21469a6e5e52de7dd5bcd93",
        #         "Hash":"0x1809f1950c51a2f64fd2c4a27d4b06450fd249883fd91c852b79a99a124837f3",
        #         "Price":0.0,
        #         "OtherAmount":0.0,
        #         "OtherCurrency":null,
        #         "OrderCode":null,
        #         "TradeId":null,
        #         "MovementId":2732259
        #     }
        #
        id = self.safe_string(item, 'MovementId')
        direction = None
        account = None
        referenceId = self.safe_string_2(item, 'TradeId', 'OrderCode')
        referenceId = self.safe_string(item, 'Hash', referenceId)
        referenceAccount = self.safe_string(item, 'Address')
        type = self.safe_string(item, 'Type')
        ledgerEntryType = self.parse_ledger_entry_type(type)
        code = self.safe_currency_code(self.safe_string(item, 'CurrencyCode'), currency)
        amount = self.safe_float(item, 'Amount')
        after = self.safe_float(item, 'TotalBalance')
        before = None
        if amount is not None:
            if after is not None:
                before = after - amount
            if type == 'withdrawal':
                direction = 'out'
            elif type == 'deposit':
                direction = 'in'
            elif (type == 'trade') or (type == 'tradefee'):
                direction = 'out' if (amount < 0) else 'in'
                amount = abs(amount)
        timestamp = self.parse8601(self.safe_string(item, 'Date'))
        fee = None
        status = self.safe_string(item, 'Status')
        return {
            'info': item,
            'id': id,
            'direction': direction,
            'account': account,
            'referenceId': referenceId,
            'referenceAccount': referenceAccount,
            'type': ledgerEntryType,
            'currency': code,
            'amount': amount,
            'before': before,
            'after': after,
            'status': status,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'fee': fee,
        }

    async def fetch_ledger(self, code=None, since=None, limit=None, params={}):
        if code is None:
            raise ArgumentsRequired(self.id + ' fetchLedger() requires a code argument')
        await self.load_markets()
        currency = self.currency(code)
        limit = 50 if (limit is None) else limit
        request = {
            'Currency': currency['id'],
            # 'TransactionType': 'transactions',  # deposits, withdrawals, depositswithdrawals, transactions
            # 'PageIndex': 0,
            'PageSize': limit,  # max 50
            'SortField': 'Date',
            # 'Descending': True,
        }
        pageIndex = self.safe_integer(params, 'PageIndex')
        if pageIndex is None:
            request['Descending'] = True
        response = await self.privatePostListTransactions(self.extend(request, params))
        #
        # fetchLedger('BTC')
        #
        #     {
        #         "TotalElements":2,
        #         "Result":[
        #             {
        #                 "Date":"2020-08-07T13:06:22.117",
        #                 "CurrencyCode":"BTC",
        #                 "Amount":-0.000000301000000000,
        #                 "TotalBalance":0.000100099000000000,
        #                 "Type":"tradefee",
        #                 "Status":"confirmed",
        #                 "Address":null,
        #                 "Hash":null,
        #                 "Price":0.0,
        #                 "OtherAmount":0.0,
        #                 "OtherCurrency":null,
        #                 "OrderCode":null,
        #                 "TradeId":5298215,
        #                 "MovementId":null
        #             },
        #             {
        #                 "Date":"2020-08-07T13:06:22.117",
        #                 "CurrencyCode":"BTC",
        #                 "Amount":0.000100400000000000,
        #                 "TotalBalance":0.000100400000000000,
        #                 "Type":"trade",
        #                 "Status":"confirmed",
        #                 "Address":null,
        #                 "Hash":null,
        #                 "Price":11811.474849000000000000,
        #                 "OtherAmount":1.185872,
        #                 "OtherCurrency":"USDT",
        #                 "OrderCode":"78389610",
        #                 "TradeId":5298215,
        #                 "MovementId":null
        #             }
        #         ]
        #     }
        #
        # fetchLedger('BTC'), same trade, other side
        #
        #     {
        #         "TotalElements":2,
        #         "Result":[
        #             {
        #                 "Date":"2020-08-07T13:06:22.133",
        #                 "CurrencyCode":"USDT",
        #                 "Amount":-1.185872000000000000,
        #                 "TotalBalance":26.428806000000000000,
        #                 "Type":"trade",
        #                 "Status":"confirmed",
        #                 "Address":null,
        #                 "Hash":null,
        #                 "Price":11811.474849000000000000,
        #                 "OtherAmount":0.000100400,
        #                 "OtherCurrency":"BTC",
        #                 "OrderCode":"78389610",
        #                 "TradeId":5298215,
        #                 "MovementId":null
        #             },
        #             {
        #                 "Date":"2020-08-07T12:36:52.72",
        #                 "CurrencyCode":"USDT",
        #                 "Amount":27.614678000000000000,
        #                 "TotalBalance":27.614678000000000000,
        #                 "Type":"deposit",
        #                 "Status":"confirmed",
        #                 "Address":"0x4d43674209fcb66cc21469a6e5e52de7dd5bcd93",
        #                 "Hash":"0x1809f1950c51a2f64fd2c4a27d4b06450fd249883fd91c852b79a99a124837f3",
        #                 "Price":0.0,
        #                 "OtherAmount":0.0,
        #                 "OtherCurrency":null,
        #                 "OrderCode":null,
        #                 "TradeId":null,
        #                 "MovementId":2732259
        #             }
        #         ]
        #     }
        #
        result = self.safe_value(response, 'Result', [])
        return self.parse_ledger(result, currency, since, limit)

    def parse_transaction_status(self, status):
        statuses = {
            'pending': 'pending',
            'processed': 'pending',
            'confirmed': 'ok',
        }
        return self.safe_string(statuses, status, status)

    def parse_transaction(self, transaction, currency=None):
        #
        #     {
        #         "Date":"2020-08-07T12:36:52.72",
        #         "CurrencyCode":"USDT",
        #         "Amount":27.614678000000000000,
        #         "TotalBalance":27.614678000000000000,
        #         "Type":"deposit",
        #         "Status":"confirmed",
        #         "Address":"0x4d43674209fcb66cc21469a6e5e52de7dd5bcd93",
        #         "Hash":"0x1809f1950c51a2f64fd2c4a27d4b06450fd249883fd91c852b79a99a124837f3",
        #         "Price":0.0,
        #         "OtherAmount":0.0,
        #         "OtherCurrency":null,
        #         "OrderCode":null,
        #         "TradeId":null,
        #         "MovementId":2732259
        #     }
        #
        id = self.safe_string(transaction, 'MovementId')
        amount = self.safe_float(transaction, 'Amount')
        address = self.safe_string(transaction, 'Address')
        addressTo = address
        addressFrom = None
        tag = None
        tagTo = tag
        tagFrom = None
        txid = self.safe_string(transaction, 'Hash')
        type = self.safe_string(transaction, 'Type')
        timestamp = self.parse8601(self.safe_string(transaction, 'Date'))
        status = self.parse_transaction_status(self.safe_string(transaction, 'Status'))
        currencyId = self.safe_string(transaction, 'CurrencyCode')
        code = self.safe_currency_code(currencyId, currency)
        return {
            'info': transaction,
            'id': id,
            'currency': code,
            'amount': amount,
            'address': address,
            'addressTo': addressTo,
            'addressFrom': addressFrom,
            'tag': tag,
            'tagTo': tagTo,
            'tagFrom': tagFrom,
            'status': status,
            'type': type,
            'updated': None,
            'txid': txid,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'fee': None,
        }

    async def fetch_transactions(self, code=None, since=None, limit=None, params={}):
        if code is None:
            raise ArgumentsRequired(self.id + ' fetchTransactions() requires a code argument')
        await self.load_markets()
        currency = self.currency(code)
        limit = 50 if (limit is None) else limit
        request = {
            'Currency': currency['id'],
            'TransactionType': 'depositswithdrawals',  # deposits, withdrawals, depositswithdrawals, transactions
            # 'PageIndex': 0,
            'PageSize': limit,  # max 50
            'SortField': 'Date',
            # 'Descending': True,
        }
        pageIndex = self.safe_integer(params, 'PageIndex')
        if pageIndex is None:
            request['Descending'] = True
        response = await self.privatePostListTransactions(self.extend(request, params))
        #
        #     {
        #         "TotalElements":2,
        #         "Result":[
        #             {
        #                 "Date":"2020-08-07T12:36:52.72",
        #                 "CurrencyCode":"USDT",
        #                 "Amount":27.614678000000000000,
        #                 "TotalBalance":27.614678000000000000,
        #                 "Type":"deposit",
        #                 "Status":"confirmed",
        #                 "Address":"0x4d43674209fcb66cc21469a6e5e52de7dd5bcd93",
        #                 "Hash":"0x1809f1950c51a2f64fd2c4a27d4b06450fd249883fd91c852b79a99a124837f3",
        #                 "Price":0.0,
        #                 "OtherAmount":0.0,
        #                 "OtherCurrency":null,
        #                 "OrderCode":null,
        #                 "TradeId":null,
        #                 "MovementId":2732259
        #             }
        #         ]
        #     }
        #
        result = self.safe_value(response, 'Result', [])
        return self.parse_transactions(result, currency, since, limit)

    async def fetch_deposits(self, code=None, since=None, limit=None, params={}):
        request = {
            'TransactionType': 'deposits',
        }
        return await self.fetch_transactions(code, since, limit, self.extend(request, params))

    async def fetch_withdrawals(self, code=None, since=None, limit=None, params={}):
        request = {
            'TransactionType': 'withdrawals',
        }
        return await self.fetch_transactions(code, since, limit, self.extend(request, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            self.check_required_credentials()
            nonce = self.nonce()
            query = self.extend({
                'key': self.apiKey,
                'nonce': nonce,
            }, query)
            body = self.json(query)
            headers = {
                'Content-Type': 'application/json',
                'Hash': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
