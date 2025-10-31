# 🤖 Discord Moderation Bot

<div align="center">

![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A powerful and feature-rich Discord moderation bot with **hybrid command support** (both slash commands and prefix commands) built with discord.py.

</div>

---

## ✨ Features

### 🛡️ Moderation Commands
- **Ban** - Ban members from the server with reason tracking
- **Unban** - Unban previously banned users
- **Kick** - Kick members from the server
- **Mute** - Timeout members for a specified duration
- **Unmute** - Remove timeout from members

### 📊 Information Commands
- **Server Info** - Detailed server statistics and information
- **User Info** - Display comprehensive user information
- **Avatar** - View and download user avatars in multiple formats

### 🔧 Utility Commands
- **Ping** - Check bot latency and response time
- **Help** - Comprehensive help system (coming soon)

### 🎯 Key Features
- ✅ **Hybrid Commands** - Works with both `/` slash commands and `!` prefix commands
- ✅ **Role Hierarchy Checks** - Prevents unauthorized actions based on role positions
- ✅ **Beautiful Embeds** - All responses use attractive Discord embeds
- ✅ **Error Handling** - Comprehensive error handling with user-friendly messages
- ✅ **Permission Checks** - Automatic permission verification for all commands
- ✅ **DM Notifications** - Members receive DM notifications for moderation actions
- ✅ **Multi-Guild Support** - Works seamlessly across multiple servers

---

## 📋 Requirements

- Python 3.8 or higher
- discord.py 2.0+
- python-dotenv

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/FrozenX2412/dc-bot.git
cd dc-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_bot_token_here
PREFIX=!
```

### 4. Run the Bot
```bash
python bot.py
```

---

## 📁 Project Structure

```
dc-bot/
├── cogs/
│   ├── ban.py          # Ban command
│   ├── unban.py        # Unban command
│   ├── kick.py         # Kick command
│   ├── mute.py         # Mute/timeout command
│   ├── unmute.py       # Unmute command
│   ├── serverinfo.py   # Server information
│   ├── avatar.py       # Avatar display
│   └── utility.py      # Utility commands & helpers
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file
└── README.md           # This file
```

---

## 🎮 Commands

### Moderation Commands

| Command | Description | Usage | Permissions Required |
|---------|-------------|-------|---------------------|
| `/ban` | Ban a member from the server | `/ban @user [reason]` | Ban Members |
| `/unban` | Unban a user by ID | `/unban <user_id> [reason]` | Ban Members |
| `/kick` | Kick a member from the server | `/kick @user [reason]` | Kick Members |
| `/mute` | Timeout a member | `/mute @user [duration] [reason]` | Moderate Members |
| `/unmute` | Remove timeout from a member | `/unmute @user [reason]` | Moderate Members |

### Information Commands

| Command | Description | Usage | Permissions Required |
|---------|-------------|-------|---------------------|
| `/serverinfo` | Display server information | `/serverinfo` | None |
| `/userinfo` | Display user information | `/userinfo [@user]` | None |
| `/avatar` | Display user's avatar | `/avatar [@user]` | None |
| `/ping` | Check bot latency | `/ping` | None |

> **Note:** All commands support both slash commands (`/command`) and prefix commands (`!command`)

---

## 🔧 Configuration

### Bot Intents
The bot requires the following intents to function properly:
- `guilds` - Access to guild information
- `members` - Access to member information
- `message_content` - Required for prefix commands

### Permissions
Recommended bot permissions:
- Ban Members
- Kick Members
- Moderate Members (Timeout)
- Manage Roles
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History

**Permission Integer:** `1099511627830`

### Invite Link Template
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=1099511627830&scope=bot%20applications.commands
```

---

## 💡 Usage Examples

### Using Slash Commands
```
/ban @JohnDoe Spamming in general chat
/mute @JaneDoe 10m Inappropriate language
/serverinfo
/avatar @User
```

### Using Prefix Commands
```
!ban @JohnDoe Spamming in general chat
!mute @JaneDoe 10m Inappropriate language
!serverinfo
!avatar @User
```

### Mute Duration Formats
- `10m` - 10 minutes
- `2h` - 2 hours
- `1d` - 1 day
- `30` - 30 minutes (default unit)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🐛 Bug Reports & Feature Requests

If you encounter any bugs or have feature suggestions, please [open an issue](https://github.com/FrozenX2412/dc-bot/issues).

---

## 📞 Support

Need help? Here are some resources:
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs/)
- [Project Issues](https://github.com/FrozenX2412/dc-bot/issues)

---

## ⚠️ Disclaimer

This bot is provided as-is without any warranties. Use at your own risk. Always ensure you comply with Discord's Terms of Service and Community Guidelines when using this bot.

---

<div align="center">

**Made with ❤️ by FrozenX2412**

⭐ Star this repository if you find it helpful!

</div>
