from web3 import Web3
import time

# Konfigurasi RPC dan Web3
RPC_URL = "http://rpc-testnet.inichain.com"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Pastikan koneksi ke node berhasil
if not web3.is_connected():
    print("Gagal terhubung ke RPC")
    exit()

# Konfigurasi
PRIVATE_KEY = "0x_privatekey"  # Ganti dengan private key Anda 
SOURCE_ADDRESS = web3.to_checksum_address("0x_youraddress")  # Ganti dengan alamat pengirim Anda
TARGET_ADDRESSES = [
    "address1",
    "address2",
    # Tambahkan alamat target lainnya
]

AMOUNT = web3.to_wei(0.0001, 'ether')  # Jumlah yang akan dikirim per transaksi
GAS_LIMIT = 21000
GAS_PRICE = web3.to_wei(2, 'gwei')

# Fungsi untuk mengirim transaksi
def send_transaction(private_key, source_address, target_address, amount):
    nonce = web3.eth.get_transaction_count(source_address)
    tx = {
        'nonce': nonce,
        'to': web3.to_checksum_address(target_address),
        'value': amount,
        'gas': GAS_LIMIT,
        'gasPrice': GAS_PRICE,
        'chainId': 7234,  # Tambahkan chain ID untuk EIP-155
    }

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return web3.to_hex(tx_hash)

# Fungsi utama
def main():
    while True:
        print("\nMemulai transfer...")
        for i, target_address in enumerate(TARGET_ADDRESSES):
            try:
                tx_hash = send_transaction(PRIVATE_KEY, SOURCE_ADDRESS, target_address, AMOUNT)
                print(f"Transfer ke {target_address} berhasil. Tx Hash: {tx_hash}")
            except Exception as e:
                print(f"Transfer ke {target_address} gagal. Error: {str(e)}")

            # Countdown 5 menit sebelum transaksi berikutnya
            print("Menunggu 5 menit sebelum transaksi berikutnya...")
            countdown_seconds = 5 * 60  # 5 menit dalam detik
            while countdown_seconds > 0:
                minutes, seconds = divmod(countdown_seconds, 60)
                print(f"⏳ Waktu tersisa: {minutes:02d}:{seconds:02d}", end="\r")
                time.sleep(1)
                countdown_seconds -= 1

        print("\nSemua transfer selesai. Menunggu 10 menit sebelum memulai lagi...")

        # Timer countdown 10 menit
        countdown_seconds = 10 * 60  # 10 menit dalam detik
        while countdown_seconds > 0:
            minutes, seconds = divmod(countdown_seconds, 60)
            print(f"⏳ Waktu tersisa: {minutes:02d}:{seconds:02d}", end="\r")
            time.sleep(1)
            countdown_seconds -= 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh user.")
