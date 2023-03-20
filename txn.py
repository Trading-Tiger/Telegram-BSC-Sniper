
from __init__ import *


zero = '0x0000000000000000000000000000000000000000'
dead = '0x000000000000000000000000000000000000dEaD'


class TXN():
    def __init__(self, token_address, quantity):
        self.w3 = self.connect()
        self.address, self.private_key = self.setup_address()
        self.token_address = Web3.toChecksumAddress(token_address)
        self.token_contract = self.setup_token()
        self.swapper_address, self.swapper = self.setup_swapperV3()
        self.swapperV2, self.swapperV2 = self.setup_swapperV2()
        self.slippage = self.setupSlippage()
        self.quantity = quantity
        self.MaxGasInBNB, self.gas_price = self.setupGas()
        self.initSettings()

    def connect(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        if keys["RPC"][:2].lower() == "ws":
            w3 = Web3(Web3.WebsocketProvider(keys["RPC"]))
        else:
            w3 = Web3(Web3.HTTPProvider(keys["RPC"]))
        return w3

    def initSettings(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        self.timeout = keys["timeout"]
        self.safeGas = keys["SaveGasCost"]

    def checkOwnership(self):
        contract_abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}]
        try:
            owner = self.w3.eth.contract(address=self.token_address, abi=contract_abi).functions.owner().call()
        except:
            return True
        if owner.lower() == zero or owner.lower() == dead.lower():
            return True
        else:
            return False

    def setupGas(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        return keys['MaxTXFeeBNB'], int(keys['GWEI_GAS'] * (10**9))

    def format_float(self, num):
        return np.format_float_positional(num, trim='-')

    def setup_address(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        if len(keys["metamask_address"]) <= 41:
            print(style.RED + "Set your Address in the keys.json file!" + style.RESET)
            raise SystemExit
        if len(keys["metamask_private_key"]) <= 42:
            print(style.RED + "Set your PrivateKey in the keys.json file!" + style.RESET)
            raise SystemExit
        return keys["metamask_address"], keys["metamask_private_key"]

    def setupSlippage(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        return keys['Slippage']

    def get_token_decimals(self):
        return self.token_contract.functions.decimals().call()

    def get_token_Name(self):
        return self.token_contract.functions.name().call()

    def get_token_Symbol(self):
        return self.token_contract.functions.symbol().call()

    def getBlockHigh(self):
        return self.w3.eth.block_number

    def setup_swapperV3(self):
        swapper_address = Web3.toChecksumAddress(
            "0x2D4e39B07117937b2CB51b8a7ab8189b50D41184")
        with open("./abis/BSC_SwapperV3.json") as f:
            contract_abi = json.load(f)
        swapper = self.w3.eth.contract(
            address=swapper_address, abi=contract_abi)
        return swapper_address, swapper

    def setup_swapperV2(self):
        swapper_address = Web3.toChecksumAddress(
            "0x18be7f977Ec1217B71D0C134FBCFF36Ea4366fCD")
        with open("./abis/BSC_SwapperV2.json") as f:
            contract_abi = json.load(f)
        swapper = self.w3.eth.contract(
            address=swapper_address, abi=contract_abi)
        return swapper_address, swapper

    def setup_token(self):
        with open("./abis/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        token_contract = self.w3.eth.contract(
            address=self.token_address, abi=contract_abi)
        return token_contract

    def get_token_balance(self):
        return self.token_contract.functions.balanceOf(self.address).call() / (10 ** self.token_contract.functions.decimals().call())

    def checkToken(self):
        # uint256 BuyEstimateOutput,
        # uint256 BuyRealOutput,
        # uint256 SellEstimateOutput,
        # uint256 SellRealOutput,
        # bool Buy,
        # bool Approve,
        # bool Sell,
        # bool SellOutputArrive
        call = self.swapperV2.functions.getTokenInformations(
            self.token_address).call()
        buy_tax = round(
            ((call[0] - call[1]) / (call[0]) * 100))
        sell_tax = round(
            ((call[2] - call[3]) / (call[2]) * 100))

        if call[4] and call[5] and call[6] == True:
            honeypot = False
        else:
            honeypot = True
        return buy_tax, sell_tax, honeypot

    def estimateGas(self, txn):
        gas = self.w3.eth.estimateGas({
            "from": txn['from'],
            "to": txn['to'],
            "value": txn['value'],
            "data": txn['data']})
        gas = gas + (gas / 10)  # Adding 1/10 from gas to gas!
        maxGasBNB = Web3.fromWei(gas * self.gas_price, "ether")
        print(style.GREEN + "\nMax Transaction cost " +
              str(maxGasBNB) + " BNB" + style.RESET)
        if maxGasBNB > self.MaxGasInBNB:
            print(style.RED + "\nTx cost exceeds your settings, exiting!")
            raise SystemExit
        return gas

    def getOutputTokenToBNB(self, percent: int = 100):
        TokenBalance = int(
            self.token_contract.functions.balanceOf(self.address).call())
        if TokenBalance > 0:
            AmountForInput = int((TokenBalance / 100) * percent)
            if percent == 100:
                AmountForInput = TokenBalance
        Amount, Way, DexWay = self.fetchOutputTokentoBNB(AmountForInput)
        return Amount, Way, DexWay

    def getTokenPrice(self):
        call = self.swapper.functions.fetchOutputTokentoToken(
            self.token_address,
            "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
            10*10**self.get_token_decimals()
        ).call()
        return self.format_float(float(call[0] / 10**19))

    def fetchOutputBNBtoToken(self):
        call = self.swapper.functions.fetchOutputETHtoToken(
            self.token_address,
            int(self.quantity * (10**18)),
        ).call()
        Amount = call[0]
        Way = call[1]
        DexWay = call[2]
        return Amount, Way, DexWay

    def fetchOutputTokentoBNB(self, quantity: int):
        call = self.swapper.functions.fetchOutputTokentoETH(
            self.token_address,
            quantity
        ).call()
        Amount = call[0]
        Way = call[1]
        DexWay = call[2]
        return Amount, Way, DexWay

    def getLiquidityUSD(self):
        raw_call = self.swapper.functions.getLiquidityUSD(
            self.token_address).call()
        real = round(raw_call[-1] / (10**18), 2)
        return raw_call, real

    def is_approve(self):
        Approve = self.token_contract.functions.allowance(
            self.address, self.swapper_address).call()
        Aproved_quantity = self.token_contract.functions.balanceOf(
            self.address).call()
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True

    def approve(self):
        if self.is_approve() == False:
            txn = self.token_contract.functions.approve(
                self.swapper_address,
                Web3.toInt(hexstr=constants.MAX_INT)
            ).buildTransaction(
                {'from': self.address,
                 'gasPrice': self.gas_price,
                 'nonce': self.w3.eth.getTransactionCount(self.address),
                 'value': 0}
            )

            txn.update({'gas': int(self.estimateGas(txn))})
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.GREEN + "\nApprove Hash:", txn.hex()+style.RESET)
            txn_receipt = self.w3.eth.waitForTransactionReceipt(
                txn, timeout=self.timeout)
            if txn_receipt["status"] == 1:
                return True, style.GREEN + "\nApprove Successfull!" + style.RESET
            else:
                return False, style.RED + "\nApprove Transaction Faild!" + style.RESET
        else:
            return True, style.GREEN + "\nAllready approved!" + style.RESET

    def buy_token(self, retry: int = 1):
        if self.safeGas != True:
            return self.buy_token_fast(retry)
        else:
            return self.buy_token_cheap(retry)

    def buy_token_fast(self, trys):
        while trys:
            try:
                txn = self.swapper.functions.snipeETHtoToken(
                    self.token_address,
                    self.slippage * 10,
                    self.address
                ).buildTransaction(
                    {'from': self.address,
                     'gasPrice': self.gas_price,
                     'nonce': self.w3.eth.getTransactionCount(self.address),
                     'value': int(self.quantity * (10**18))}
                )
                gas = int(self.estimateGas(txn))

                txn.update({'gas': int(self.estimateGas(txn))})
                signed_txn = self.w3.eth.account.sign_transaction(
                    txn,
                    self.private_key
                )
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(
                    txn, timeout=self.timeout)
                if txn_receipt["status"] == 1:
                    return True, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)
                else:
                    return False, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)
            except Exception as e:
                print(e)
                trys -= 1
                print(style.RED + "\nBUY Transaction Faild!" + style.RESET)
                time.sleep(3)

    def buy_token_cheap(self, trys):
        while trys:
            try:
                Amount, TokenWay, DexWay = self.fetchOutputBNBtoToken()
                minAmount = int(Amount - ((Amount / 100) * self.slippage))
                txn = self.swapper.functions.fromETHtoToken(
                    minAmount,
                    TokenWay,
                    DexWay,
                    self.address
                ).buildTransaction(
                    {'from': self.address,
                     'gasPrice': self.gas_price,
                     'nonce': self.w3.eth.getTransactionCount(self.address),
                     'value': int(self.quantity * (10**18))}
                )
                gas = int(self.estimateGas(txn))
                txn.update({'gas': gas})
                signed_txn = self.w3.eth.account.sign_transaction(
                    txn,
                    self.private_key
                )
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

                txn_receipt = self.w3.eth.waitForTransactionReceipt(
                    txn, timeout=self.timeout)
                if txn_receipt["status"] == 1:
                    return True, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)
                else:
                    return False, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)

            except Exception as e:
                print(e)
                trys -= 1
                print(style.RED + "\nBUY Transaction Faild!" + style.RESET)
                time.sleep(3)

    def sell_tokens(self, percent: int = 100):
        self.approve()
        TokenBalance = int(
            self.token_contract.functions.balanceOf(self.address).call())
        if TokenBalance > 0:
            AmountForSell = int((TokenBalance / 100) * percent)
            if percent == 100:
                AmountForSell = TokenBalance
            if self.safeGas != True:
                return self.sell_tokens_fast(AmountForSell)
            else:
                return self.sell_tokens_cheap(AmountForSell)
        else:
            print(style.RED + "\nYou dont have any tokens to sell!" + style.RESET)

    def sell_tokens_fast(self, Amount: int):
        txn = self.swapper.functions.snipeTokentoETH(
            Amount,
            self.token_address,
            self.slippage * 10,
            self.address
        ).buildTransaction(
            {'from': self.address,
             'gasPrice': self.gas_price,
             'nonce': self.w3.eth.getTransactionCount(self.address)}
        )
        gas = int(self.estimateGas(txn))
        txn.update({'gas': gas})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )

        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        txn_receipt = self.w3.eth.waitForTransactionReceipt(
            txn, timeout=self.timeout)

        if txn_receipt["status"] == 1:
            return True, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)
        else:
            return False, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)

    def sell_tokens_cheap(self, Amount: int):
        AmountOut, TokenWay, DexWay = self.fetchOutputTokentoBNB(Amount)
        minAmount = int(AmountOut - ((AmountOut / 100) * self.slippage))
        txn = self.swapper.functions.fromTokentoETH(
            Amount,
            minAmount,
            TokenWay,
            DexWay,
            self.address
        ).buildTransaction(
            {
                'from': self.address,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address)
            }
        )
        gas = int(self.estimateGas(txn))
        txn.update({'gas': gas})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(
            txn, timeout=self.timeout)

        if txn_receipt["status"] == 1:
            return True, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)
        else:
            return False, txn.hex(), round(float(Web3.fromWei(gas * self.gas_price, "ether")), 5)
