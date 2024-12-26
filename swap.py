import requests
from web3 import Web3
from eth_account import Account
import time
import sys
import os
import json
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
NETWORKS = {
    "InitVerse": {
        "rpc_url": os.getenv("INITVERSE_RPC_URL"),
        "chain_id": int(os.getenv("INITVERSE_CHAIN_ID")),
        "contract_address": os.getenv("INITVERSE_CONTRACT_ADDRESS"),
    }
}

TOKENS = {
    "USDT": os.getenv("USDT_TOKEN"),
    "INI": os.getenv("INI_TOKEN"),
}


def load_abi(name):
    with open(f"./{name}.json", "r") as f:
        return json.load(f)


# Load ABIs
ERC20_ABI = load_abi("ERC20")
ROUTER_ABI = load_abi("router_swap")


def print_banner():
    print("\033[96m" + "=" * 57 + "\033[0m")  # Cyan
    print(
        "\033[1;35m" + " INITVERSE | AIRDROP ASC " + "\033[0m".center(57)
    )  # Bold Magenta
    print("\033[96m" + "=" * 57 + "\033[0m")  # Cyan
    print("\033[93m" + "Credit By       : Airdrop ASC" + "\033[0m")  # Yellow
    print("\033[93m" + "Telegram Channel: @airdropasc" + "\033[0m")  # Yellow
    print("\033[93m" + "Telegram Group  : @autosultan_group" + "\033[0m")  # Yellow
    print("\033[96m" + "=" * 57 + "\033[0m")  # Cyan


def get_address(private_key):
    return Account.from_key(f"0x{private_key.lstrip('0x')}").address


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None


def get_user_info(address):
    return fetch_data(
        f"https://candyapi.inichain.com/airdrop/v1/user/userInfo?address={address}"
    )


def verify_user_before_swap(address):
    logger.info(f"\033[96mAddress:\033[0m {address}")  # Cyan

    user_info = get_user_info(address)
    if not user_info:
        print("\033[91mCannot retrieve user info. Exiting.\033[0m")  # Red
        sys.exit(1)

    task_status = fetch_data(
        f"https://candyapi.inichain.com/airdrop/v1/user/UserTaskStatus?address={address}"
    )
    if not task_status:
        print("\033[91mCannot retrieve task status. Exiting.\033[0m")  # Red
        sys.exit(1)

    daily_tasks = task_status.get("data", {}).get("dailyTaskInfo", [])
    if not daily_tasks:
        print("\033[91mNo daily tasks found. Exiting.\033[0m")  # Red
        return False

    swap_task = daily_tasks[0]
    if swap_task.get("flag"):
        logger.info("\033[92mSwap task is available. Proceeding...\033[0m")  # Green
        return True
    else:
        print("\033[91mSwap task is not available. Exiting.\033[0m")  # Red
        return False


def save_tx_hash(tx_hash, source_network, swap_name):
    base_folder = "Tx_Hash"
    os.makedirs(base_folder, exist_ok=True)

    network_folder = os.path.join(base_folder, source_network.replace(" ", "-"))
    os.makedirs(network_folder, exist_ok=True)

    swap_file_path = os.path.join(
        network_folder, f'Tx_{swap_name.replace(" ", "-")}.txt'
    )

    with open(swap_file_path, "a") as file:
        file.write(f"{tx_hash}\n")


def get_transaction_status(tx_hash, w3):
    start_time = time.time()  # Waktu mulai
    logger.info("\033[96mWaiting for transaction to be mined...\033[0m")  # Cyan
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    elapsed_time = time.time() - start_time  # Hitung waktu yang telah berlalu
    logger.info(
        f"\033[92mTransaction mined in {elapsed_time:.2f} seconds.\033[0m"
    )  # Green
    return receipt["status"]  # 1 for success, 0 for failure


def approve_token_if_needed(account, token_contract, router_address, w3):
    allowance = token_contract.functions.allowance(
        account.address, router_address
    ).call()
    balance = token_contract.functions.balanceOf(account.address).call()

    if allowance < balance:
        nonce = w3.eth.get_transaction_count(account.address)
        approval_txn = token_contract.functions.approve(
            router_address, balance
        ).build_transaction(
            {
                "from": account.address,
                "gas": 100000,
                "gasPrice": w3.to_wei("2", "gwei"),
                "nonce": nonce,
            }
        )

        signed_approval_txn = w3.eth.account.sign_transaction(
            approval_txn, private_key=account.key
        )
        approval_tx_hash = w3.eth.send_raw_transaction(
            signed_approval_txn.raw_transaction
        )
        logger.info(
            f"\033[96mApproval Tx Hash:\033[0m {w3.to_hex(approval_tx_hash)}"
        )  # Cyan

        # Wait for approval to be mined and confirm success
        approval_status = get_transaction_status(approval_tx_hash, w3)
        if approval_status != 1:
            logger.error("\033[91mApproval failed. Exiting.\033[0m")  # Red
            sys.exit(1)


def perform_swap(w3, account, router_contract, path, amount_in, is_eth_to_token):
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        deadline = int(time.time()) + 10000

        if is_eth_to_token:
            txn = router_contract.functions.swapExactETHForTokens(
                0, path, account.address, deadline
            ).build_transaction(
                {
                    "from": account.address,
                    "value": amount_in,
                    "gas": 200000,
                    "gasPrice": w3.to_wei("2", "gwei"),
                    "nonce": nonce,
                }
            )
        else:
            balance = (
                w3.eth.contract(address=path[0], abi=ERC20_ABI)
                .functions.balanceOf(account.address)
                .call()
            )
            txn = router_contract.functions.swapExactTokensForETH(
                balance, 0, path, account.address, deadline
            ).build_transaction(
                {
                    "from": account.address,
                    "gas": 200000,
                    "gasPrice": w3.to_wei("2", "gwei"),
                    "nonce": nonce,
                }
            )

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        logger.info(f"\033[92mTransaction Hash:\033[0m {w3.to_hex(tx_hash)}")  # Green

        status = get_transaction_status(tx_hash, w3)
        return status == 1
    except Exception as e:
        logger.error(f"Error during swap: {e}")
        return False


def run_swap_loop(account):
    w3 = Web3(Web3.HTTPProvider(NETWORKS["InitVerse"]["rpc_url"]))
    router_address = "0x4ccB784744969D9B63C15cF07E622DDA65A88Ee7"
    router_contract = w3.eth.contract(
        address=Web3.to_checksum_address(router_address), abi=ROUTER_ABI
    )

    token_contract = w3.eth.contract(
        address=Web3.to_checksum_address(TOKENS["USDT"]), abi=ERC20_ABI
    )

    paths = {
        "eth_to_usdt": [TOKENS["INI"], TOKENS["USDT"]],
        "usdt_to_eth": [TOKENS["USDT"], TOKENS["INI"]],
    }

    while True:
        # Swap ETH to USDT
        logger.info("\033[92mSwap ETH to USDT swap Proceeding....\033[0m")  # Green
        if perform_swap(
            w3,
            account,
            router_contract,
            paths["eth_to_usdt"],
            w3.to_wei("0.00011", "ether"),
            True,
        ):
            logger.info("\033[92mETH to USDT swap successful.\033[0m\n")  # Green
            # Countdown selama 10 menit
            for remaining in range(600, 0, -1):
                sys.stdout.write(
                    f"\r\033[93mWaiting for {remaining} seconds...\033[0m"
                )  # Yellow
                sys.stdout.flush()
                time.sleep(1)
            print()  # Untuk pindah ke baris baru setelah countdown
        else:
            print("\033[91mETH to USDT swap failed. Retrying...\033[0m\n")  # Red
            continue

        # Swap USDT to ETH
        approve_token_if_needed(account, token_contract, router_address, w3)
        logger.info("\033[92mSwap USDT to ETH swap Proceeding....\033[0m")  # Green
        if perform_swap(w3, account, router_contract, paths["usdt_to_eth"], 0, False):
            logger.info("\033[92mUSDT to ETH swap successful.\033[0m\n")  # Green
            # Countdown selama 10 menit
            for remaining in range(600, 0, -1):
                sys.stdout.write(
                    f"\r\033[93mWaiting for {remaining} seconds...\033[0m"
                )  # Yellow
                sys.stdout.flush()
                time.sleep(1)
            print()  # Untuk pindah ke baris baru setelah countdown
        else:
            print("\033[91mUSDT to ETH swap failed. Retrying...\033[0m\n")  # Red
            continue


def main():
    try:
        os.system("clear") if os.name == "posix" else os.system("cls")
        print_banner()

        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            print(
                "\033[91mPrivate key not found in environment variables.\033[0m"
            )  # Red
            sys.exit(1)

        account = Account.from_key(private_key)
        if not verify_user_before_swap(address=account.address):
            print("\033[91mVerification failed. Exiting.\033[0m")  # Red
            sys.exit(1)

        run_swap_loop(account)

    except KeyboardInterrupt:
        logger.info("\033[93mOperation interrupted by user.\033[0m")  # Yellow
        sys.exit()


if __name__ == "__main__":
    main()
