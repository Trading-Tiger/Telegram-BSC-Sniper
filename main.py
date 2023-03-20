
from __init__ import *


class TG_Scrapp:
    def __init__(self):
        self.reinitConfig()

    def reinitConfig(self):
        self.config = self.initConfig()
        self.tsl = self.config["TrailingStopLoss"]
        self.tp = self.config["TakeProfit"]
        self.sl = self.config["StopLoss"]

    def initConfig(self):
        with open("./Settings.json") as j:
            config = json.load(j)
        return config

    def CheckMarket(self, parsed_response):
        if self.config['BuyOnlyCMC']:
            if "COINMARKETCAP".lower() in parsed_response.lower():
                return True
            else:
                return False
        else:
            return True

    def start(self):
        self.reinitConfig()
        client = TelegramClient(
            self.config["TG_app_name"], self.config["TG_app_id"], self.config["TG_api_hash"])
        client.start()
        channels_entities = []
        for d in client.iter_dialogs():
            if d.entity.id in self.config["TG_Channels"]:
                channels_entities.append(InputChannel(
                    d.entity.id, d.entity.access_hash))
        if not channels_entities:
            print(
                f"[ERROR] Make sure you are inside your Selected Telegram Groups or Channels !!!")
            raise SystemExit
        print(f"[STARTED] Listening on {len(channels_entities)} channels.")

        @client.on(events.NewMessage(chats=channels_entities))
        async def handler(event):
            parsed_response = event.message.message
            msg_splitted = parsed_response.split()
            if "bsc" in parsed_response.lower():
                if self.CheckMarket(parsed_response):
                    for tokenAddress in msg_splitted:
                        if tokenAddress[:2] == "0x":
                            if Web3.isAddress(tokenAddress):
                                Thread(target=self.Sniper, daemon=True,
                                       args=(tokenAddress,)).start()
        client.run_until_disconnected()

    def Sniper(self, tokenAddress):
        TX = TXN(tokenAddress, self.config["bnb_amount"])
        if not self.isBlackList(tokenAddress):
            if self.HoneypotAndTaxTest(TX, tokenAddress):
                if TX.checkOwnership():
                    if self.executeBuy(TX, tokenAddress):
                        if self.tsl != 0 or self.tp != 0 or self.sl != 0:
                            TX.approve()
                            self.awaitMangePosition(TX, tokenAddress)
                        else:
                            pass
                    else:
                        print("[ERROR] BUY Transaction Fail !")
                else:
                    print("[ERROR] Ownership is not renounced")
            else:
                print("[ERROR] Token Blacklisted!")
        else:
            print("[ERROR] Token Blacklisted!")

    def executeBuy(self, TX, tokenAddress):
        tx = TX.buy_token()
        self.save_transaction_to_json(
            tx[1],
            tx[2],
            tokenAddress,
            "BUY",
            self.config["bnb_amount"]
        )
        return tx[0]

    def isBlackList(self, tokenAddress):
        with open("blacklist.json", "r") as b:
            b = json.load(b)
        if tokenAddress.lower() in b["blacklist"]:
            return True
        else:
            with open("blacklist.json", "w") as e:
                b["blacklist"].append(tokenAddress.lower())
                json.dump(b, e)
        return False

    def calcProfit(self, TX):
        self.amountForSnipe = TX.getOutputTokenToBNB(percent=100)[
            0] / (10**18)
        a = ((self.amountForSnipe) * self.tp) / 100
        b = a + (self.amountForSnipe)
        return b

    def calcloss(self, TX):
        self.amountForSnipe = TX.getOutputTokenToBNB(percent=100)[
            0] / (10**18)
        a = ((self.amountForSnipe) * self.sl) / 100
        b = (self.amountForSnipe) - a
        print(b)
        return b

    def calcNewTrailingStop(self, currentPrice):
        a = (currentPrice * self.tsl) / 100
        b = currentPrice - a
        return b

    def awaitMangePosition(self, TX, tokenAddress):
        highestLastPrice = 0
        if self.tp != 0:
            self.takeProfitOutput = self.calcProfit(TX)
        else:
            self.takeProfitOutput = 0
        if self.sl != 0:
            self.stoploss = self.calcloss(TX)
        else:
            self.stoploss = 0
        while True:
            try:
                sleep(0.9)
                LastPrice = float(
                    TX.getOutputTokenToBNB(100)[0] / (10**18))
                if self.tsl != 0:
                    if LastPrice > highestLastPrice:
                        highestLastPrice = LastPrice
                        self.TrailingStopLoss = self.calcNewTrailingStop(
                            LastPrice)

                    if LastPrice < self.TrailingStopLoss:
                        print(style().GREEN +
                              "[TRAILING STOP LOSS Triggert]" + style().RESET + " Send Sell Transaction!")
                        tx = TX.sell_tokens()
                        self.save_transaction_to_json(
                            tx[1],
                            tx[2],
                            tokenAddress,
                            "SELL",
                            LastPrice
                        )
                        break

                if self.takeProfitOutput != 0:
                    if LastPrice >= self.takeProfitOutput:
                        print()
                        print(style().GREEN +
                              "[TAKE PROFIT Triggert]" + style().RESET + " Yay, Send Sell Transaction!")
                        tx = TX.sell_tokens()
                        self.save_transaction_to_json(
                            tx[1],
                            tx[2],
                            tokenAddress,
                            "SELL",
                            LastPrice
                        )

                        break

                if self.sl != 0:
                    if LastPrice <= self.stoploss:
                        print(
                            style().GREEN + "[STOP LOSS Triggert] " + style().RESET + " Send Sell Transaction!")
                        tx = TX.sell_tokens()
                        self.save_transaction_to_json(
                            tx[1],
                            tx[2],
                            tokenAddress,
                            "SELL",
                            LastPrice
                        )
                        break

            except Exception as e:
                print(e)
                if KeyboardInterrupt:
                    raise SystemExit
                print(
                    style().RED + f"[ERROR] {str(e)},\n\nSleeping now 30sec!" + style().RESET)
                sleep(30)

    def save_transaction_to_json(self, tx_hash: str, gas_cost: float, token_address: str, transaction_type: str, BnbAmount):
        # load existing transactions from JSON file
        with open("transactions.json", "r") as f:
            transactions = json.load(f)
        # add new transaction to appropriate array
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        currentPrice = TXN(token_address, 0).getTokenPrice()
        if transaction_type == "BUY":
            transactions["BUYs"].append(
                {"TimeStamp": now, "tx_hash": tx_hash, "gas_cost": gas_cost, "token_address": token_address, "BnbAmount": BnbAmount, "TokenPrice": currentPrice})
        elif transaction_type == "SELL":
            transactions["SELLs"].append(
                {"TimeStamp": now, "tx_hash": tx_hash, "gas_cost": gas_cost, "token_address": token_address, "BnbAmount": BnbAmount, "TokenPrice": currentPrice})
        else:
            raise ValueError(
                "Invalid transaction type. Must be 'BUY' or 'SELL'.")
        # save updated transactions to JSON file
        with open("transactions.json", "w") as f:
            json.dump(transactions, f, indent=2)

    def HoneypotAndTaxTest(self, TX, tokenAddress):
        try:
            print(style().YELLOW + "Checking Token..." + style().RESET)
            honeyTax = TX.checkToken()
            if honeyTax[2] == True:
                print(style.RED + "Token is Honeypot, exiting")
                raise SystemExit
            elif honeyTax[2] == False:
                print(style().GREEN +
                      "[DONE] Token is NOT a Honeypot!" + style().RESET)
            print(style.GREEN + "[TOKENTAX] Current Token BuyTax:",
                  honeyTax[0], "%" + style.RESET)
            print(style.GREEN + "[TOKENTAX] Current Token SellTax:",
                  honeyTax[1], "%" + style.RESET)
            if honeyTax[1] > self.config["MaxSellTax"]:
                print(style.RED+"Token SellTax exceeds Settings.json, exiting!")
                raise SystemExit
            if honeyTax[0] > self.config["MaxBuyTax"]:
                print(style.RED+"Token BuyTax exceeds Settings.json, exiting!")
                raise SystemExit
            return True
        except Exception as e:
            print(e)
            print(f"Skipping {tokenAddress}")
            raise SystemExit


while True:
    try:
        TGS = TG_Scrapp()
        TGS.start()
    except Exception as e:
        print(e)
        if KeyboardInterrupt:
            raise SystemExit
