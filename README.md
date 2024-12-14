# Discord Bot For Surplox

## Description

This Discord bot, built using the `discord.py` library, includes various command functionalities organized into multiple
**Cogs**. Each cog handles specific features, such as text-to-speech, Steam user statuses, stock information, and other
utilities.

---

## Features

### 1. **Text-to-Speech (TTS)**

**Command:** `!tts <text>`

- Converts the provided text into speech using the **ElevenLabs API**.
- The bot joins the user's voice channel, plays the generated speech, and then disconnects.
- Supports clean-up of temporary audio files.

**Dependencies:**

- `aiohttp` for making API calls.
- `FFmpeg` for playing audio in Discord voice channels.

---

### 2. **Music Playback**

**Command:** `!p <file>`

- Plays a pre-uploaded MP3 file from a specific directory (`assets/mp3/sounds/`).
- The bot joins the user's voice channel, plays the requested file, and then disconnects.

---

### 3. **Pavel Commands**

**Commands:**

- `!pavel` - Activates Pavel mode.
- `!disable_pavel` - Disables Pavel mode.
- `!picture` / `!peter` - Sends a random picture from a folder (`assets/pictures/random`).

**Special Listener**:

- Monitors voice channel updates. If a user with a specific ID joins a channel, the bot sends a humorous message in the
  text channel.

---

### 4. **Steam Status Commands**

**Command:** `!steam_status <name/ID>`

- Fetches and displays the current Steam status of a user.
- Supports user-friendly names mapped to Steam IDs.
- Displays:
    - User's profile picture.
    - Steam status (Online, Offline, Busy, etc.).
    - Profile URL.

**Dependencies:**

- `aiohttp` for Steam API requests.

---

### 5. **Stock Market Commands**

**Commands:**

- `!stock <ticker>` - Fetches general information about a stock, such as name, sector, and market cap.
- `!stock <ticker>.history <period> <interval>` - Displays historical data for the specified stock.
- `!stockhelp` - Displays available stock-related commands.

**Supported Stock Attributes:**

- Dividends, splits, actions, financials, balance sheets, cashflows, earnings, and more.

**Dependencies:**

- `yfinance` for stock market data.

---

## Requirements

### Libraries:

- Check `requirements.txt` for a complete list of required libraries.
- **FFmpeg** (must be installed and available in your system's PATH).

---

## Installation

You can set up this bot either **locally** or using **Docker**.

---

### 1. **Local Installation**

Clone the repository:
```bash
git clone https://github.com/yourusername/discord-bot-for-surplox.git
```
Cd in to it
```bash
cd discord-bot-for-surplox
```
Install the required libraries using `pip`:
```bash
pip install -r requirements.txt
```

#### **2. Docker Installation**

You need to add the .env to the repo before using the docker command!

Build the docker container
```bash
docker build -t discord-bot .
```
Run the docker container
```bash
docker run -d --name discord-bot discord-bot
```
