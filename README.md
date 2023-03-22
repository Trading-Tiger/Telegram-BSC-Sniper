# Telegram BSC Sniper beta

This project is a Python script that listens to Telegram channels for messages containing Binance Smart Chain (BSC) token addresses, and automatically snipes them by buying them with Binance Coin (BNB) and managing the position with take profit, stop loss, and trailing stop loss strategies. It also performs some checks on the token, such as checking if it's a honeypot or if it has excessive buy/sell taxes, and avoids blacklisted tokens. 

## Prerequisites
- Telegram account and API hash.
- In this Telegram channel https://t.me/CMC_CG_listing_alerts
- BSC Address with Private Key.

To use this script, you will need to install the following dependencies:

- Python 3
- Telethon
- Web3
- eth-abi
- numpy

You can install these dependencies by running `pip install telethon web3 numpy`.

You will also need to provide a `Settings.json` file with your Telegram app ID and hash, your Metamask address and private key, and some other configuration options. Additionally, you may need to update the `blacklist.json` file with any tokens that you want to exclude from the sniper.

## Usage

To use this script, follow these steps:

1. Clone this repository or download the ZIP file.
2. Install the required dependencies using `pip`.
3. Edit `Settings.json` file in the root directory of the project with your Telegram app ID and hash, your Metamask address and private key, and other configuration options.
4. Open a terminal or command prompt window and navigate to the directory where the script is located.
5. Run the script by executing the command `python3 main.py`.
6. The script will start listening to the configured Telegram channels, and will automatically buy and manage positions for any BSC tokens that are mentioned in the messages.

## Documentation:
  - [Telegram Setup](https://docs.trading-tigers.com/telegram-bsc-sniper/telegram-setup)
  - [Install](https://docs.trading-tigers.com/telegram-bsc-sniper/installation)
  - [Settings](https://docs.trading-tigers.com/telegram-bsc-sniper/settings)

Note that this script is provided for educational purposes only, and should not be used for actual trading without proper testing and due diligence. The script may contain bugs or errors that could result in financial loss. Use at your own risk.

## Low Tax Rates
There's a 0.7% tax on the swap amount, but if you hold 1k TIGS, your tax rate drops to an incredibly low 0.2%. This means you can keep more of your profits.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments


This project was inspired @bordersize and [coinmarketcap-sniper-bot](https://github.com/Scott-778/coinmarketcap-sniper-bot).
