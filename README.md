<p style="font-size:14px" align="right">
<a href="https://t.me/airdropasc" target="_blank">Join our telegram <img src="https://user-images.githubusercontent.com/50621007/183283867-56b4d69f-bc6e-4939-b00a-72aa019d1aea.png" width="30"/></a>
</p>

<p align="center">
  <img height="300" height="auto" src="https://user-images.githubusercontent.com/109174478/209359981-dc19b4bf-854d-4a2a-b803-2547a7fa43f2.jpg">
</p>

## INITVERSE - BOT | Auto Swap and Swap | Single / Multi Transfer

### NOTE SWAP 1x before | USE USDT-INI & INI-USDT

### Install

```
bash <(curl -s https://data.zamzasalim.xyz/file/uploads/initverse2.sh)
```

### Paste PrivateKeys

```
cd initverse-auto-swap
```

```
nano .env
```

**After Paste CTRL + XY**

### Install Modul | Need Web3 V7.3.0 | MANUAL INSTALL eth-account

```
pip install eth-account
```

```
pip install python-dotenv
```

```
pip install web3
```

**Check Version web3**

```
pip show web3
```

```
npm install
```

```
pip install -r requirements.txt
```

### RUN Bot

**Create Screen**

```
screen -S verse
```

**Run Bot**

```
python3 swap.py
```

### Multi Transfer (Transaction every 5 minutes, loop every 10 minutes)

**Re-enter Value**

```
1. PRIVATE_KEY = "0x_privatekey"
2. SOURCE_ADDRESS = ...("0x_youraddress")
3. TARGET_ADDRESSES = [
    "address1",
    "address2",
    # Tambahkan alamat target lainnya
]
```

**Run Bot**

```
python3 multi_transfer.py
```

### Single Transfer (Loop every 1 hours)

**Re-enter Value**

```
1. TARGET_ADDRESS = "address_receiver"
2. AMOUNT = 0.001 # Dalam INI
3. PRIVATE_KEYS = ["0x_privatekey"]
```

**Run Bot**

```
python3 single_transfer.py
```

### Troubleshoot Screen

**Close Screen | CTRL + AD**

**Go back to Screen**

```
Screen -r verse
```

**Delete Screen**

```
screen -S verse -X kill
```

**Credit @Stelaer**
