# Telegram BSC Sniper

This project is a Python script that listens to Telegram channels for messages containing Binance Smart Chain (BSC) token addresses, and automatically snipes them by buying them with Binance Coin (BNB) and managing the position with take profit, stop loss, and trailing stop loss strategies. It also performs some checks on the token, such as checking if it's a honeypot or if it has excessive buy/sell taxes, and avoids blacklisted tokens. 

## Prerequisites

To use this script, you will need to install the following dependencies:

- Python 3
- Telethon
- Web3
- eth-abi
- numpy

You can install these dependencies by running `pip install telethon web3 eth-abi numpy`.

You will also need to provide a `Settings.json` file with your Telegram app ID and hash, your Metamask address and private key, and some other configuration options. Additionally, you may need to update the `blacklist.json` file with any tokens that you want to exclude from the sniper.

## Usage

To use this script, follow these steps:

1. Clone this repository or download the ZIP file.
2. Install the required dependencies using `pip`.
3. Create a `Settings.json` file in the root directory of the project with your Telegram app ID and hash, your Metamask address and private key, and other configuration options. An example `Settings.json` file is provided in this repository.
4. Update the `blacklist.json` file with any tokens that you want to exclude from the sniper.
5. Open a terminal or command prompt window and navigate to the directory where the script is located.
6. Run the script by executing the command `python <script_name>.py`.
7. The script will start listening to the configured Telegram channels, and will automatically buy and manage positions for any BSC tokens that are mentioned in the messages.

Note that this script is provided for educational purposes only, and should not be used for actual trading without proper testing and due diligence. The script may contain bugs or errors that could result in financial loss. Use at your own risk.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
