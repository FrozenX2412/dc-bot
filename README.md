# 🤖 Discord Bot - Advanced Moderation & Info System

[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

> A powerful, feature-rich Discord bot with **hybrid command support** (slash + prefix), **creative embeds**, and **multi-guild support**. Organized with modular cog architecture for easy maintenance.

## ✨ Key Features

- ✅ **Hybrid Commands** - Both `/slash` and `!prefix` command support
- ✅ **Creative Embed Design** - Master-designed beautiful embeds with unique styling for every command
- ✅ **Multi-Guild Support** - Seamlessly works across unlimited servers
- ✅ **Modular Architecture** - Organized folder structure with categorized cogs
- ✅ **Role Hierarchy Protection** - Smart permission checks prevent unauthorized actions
- ✅ **Comprehensive Error Handling** - User-friendly error messages
- ✅ **DM Notifications** - Members receive DM notifications for moderation actions
- ✅ **Persistent Data** - Warning tracking, blacklist system with JSON storage
- ✅ **150+ Commands** - Extensive collection across Fun, Info, Moderation, and Utility categories

## 📁 Project Structure

```
dc-bot/
├── cogs/
│   ├── fun/                    # 🎉 Entertainment commands
│   │   ├── compliment.py       # Send compliments
│   │   ├── dadjoke.py          # Dad jokes
│   │   ├── darkjoke.py         # Dark humor jokes
│   │   ├── eightball.py        # Magic 8-ball
│   │   ├── fakequote.py        # Fake celebrity quotes
│   │   ├── insult.py           # Playful insults
│   │   ├── meme.py             # Random memes
│   │   ├── pickup.py           # Pickup lines
│   │   ├── pun.py              # Puns & wordplay
│   │   ├── roast.py            # Roasts
│   │   └── showerthought.py    # Random shower thoughts
│   ├── info/                   # ℹ️ Information commands
│   │   ├── basic_info.py       # Bot stats, ping, uptime
│   │   ├── user_info.py        # User details & profiles
│   │   └── server_info.py      # Server statistics
│   ├── moderation/             # 🛡️ Moderation commands
│   │   ├── ban.py, unban.py
│   │   ├── kick.py, warn.py
│   │   ├── mute.py, unmute.py
│   │   ├── clear.py, purge.py
│   │   ├── slowmode.py, lock.py, unlock.py
│   │   ├── roleadd.py, roleremove.py, roleinfo.py
│   │   ├── move.py, nick.py
│   │   ├── advanced_moderation.py  # softban, prune, infractions, modlog, report
│   │   ├── avatar.py
│   │   ├── antihosting.py, antilink.py, antispam.py
│   │   └── other utilities
│   └── utility/                # 🔧 Utility & tools
│       ├── banner.py, botinfo.py
│       ├── calc.py, color.py, convert.py
│       ├── decodebinary.py, editsnipe.py
│       ├── expand.py, remind.py, shorten.py
│       ├── time.py, timer.py
│       ├── translate.py, weather.py, whois.py
│       └── more utilities
├── bot.py                  # Main bot file
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🎨 Fun Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/joke` | Get a random joke | `/joke [type]` |
| `/meme` | Random meme from Reddit | `/meme` |
| `/compliment` | Get a compliment | `/compliment` |
| `/insult` | Playful insult | `/insult` |
| `/roast` | Epic roast | `/roast [@user]` |
| `/8ball` | Magic 8-ball | `/8ball [question]` |
| `/pun` | Random pun | `/pun` |
| `/pickup` | Pickup line | `/pickup` |
| `/fakequote` | Fake celebrity quote | `/fakequote` |
| `/showerthought` | Random shower thought | `/showerthought` |

## 🛡️ Moderation Commands

### Member Management

| Command | Description | Usage |
|---------|-------------|-------|
| `/ban` | Ban a member from the server | `/ban @user [reason]` |
| `/unban` | Unban a user by ID | `/unban [reason]` |
| `/kick` | Kick a member from the server | `/kick @user [reason]` |
| `/mute` | Timeout a member | `/mute @user [duration] [reason]` |
| `/unmute` | Remove timeout | `/unmute @user [reason]` |
| `/warn` | Issue a warning | `/warn @user [reason]` |
| `/softban` | Ban and instantly unban | `/softban @user [reason]` |

### Message & Channel Management

| Command | Description | Usage |
|---------|-------------|-------|
| `/clear` | Delete messages from channel | `/clear [amount]` |
| `/purge` | Alias for clear | `/purge [amount]` |
| `/slowmode` | Set channel slowmode | `/slowmode [seconds]` |
| `/lock` | Lock a channel | `/lock [channel]` |
| `/unlock` | Unlock a channel | `/unlock [channel]` |

### Role Management

| Command | Description | Usage |
|---------|-------------|-------|
| `/roleadd` | Add a role to a user | `/roleadd @user @role` |
| `/roleremove` | Remove a role from a user | `/roleremove @user @role` |
| `/roleinfo` | Display role information | `/roleinfo @role` |

### Advanced Moderation

| Command | Description | Usage |
|---------|-------------|-------|
| `/prune` | Preview inactive member removal | `/prune [days]` |
| `/infractions` | Show user's warning history | `/infractions @user` |
| `/modlog` | Display moderation actions log | `/modlog` |
| `/report` | Report a user to moderators | `/report @user [reason]` |
| `/blacklist` | Block user from bot usage | `/blacklist @user` |
| `/whitelist` | Unblock user from bot usage | `/whitelist @user` |

## ℹ️ Information Commands

### Bot Information

| Command | Description | Usage |
|---------|-------------|-------|
| `/help` | Shows all available commands | `/help` |
| `/ping` | Check bot latency | `/ping` |
| `/uptime` | Show how long bot has been online | `/uptime` |
| `/stats` | Display bot statistics | `/stats` |
| `/botinfo` | Detailed bot information | `/botinfo` |

### User Information

| Command | Description | Usage |
|---------|-------------|-------|
| `/userinfo` | Display user information | `/userinfo [@user]` |
| `/whois` | Detailed user info (alias) | `/whois [@user]` |
| `/id` | Get user or server ID | `/id [@user]` |
| `/joined` | Show when user joined server | `/joined [@user]` |
| `/avatar` | Get user's avatar | `/avatar [@user]` |

### Server Information

| Command | Description | Usage |
|---------|-------------|-------|
| `/membercount` | Show server member count | `/membercount` |
| `/roles` | List all server roles | `/roles` |
| `/channelinfo` | Display channel information | `/channelinfo [channel]` |
| `/emoji` | Show server emojis | `/emoji` |
| `/servericon` | Display server icon | `/servericon` |
| `/boostcount` | Show boost statistics | `/boostcount` |
| `/servercreated` | Show server creation date | `/servercreated` |

## 🔧 Utility Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/calc` | Calculator | `/calc [expression]` |
| `/color` | Color converter | `/color [color_code]` |
| `/convert` | Unit converter | `/convert [amount] [from] [to]` |
| `/time` | Current time in timezone | `/time [timezone]` |
| `/weather` | Weather information | `/weather [location]` |
| `/translate` | Translate text | `/translate [text] [language]` |
| `/shorten` | Shorten URL | `/shorten [url]` |
| `/expand` | Expand shortened URL | `/expand [url]` |
| `/remind` | Set a reminder | `/remind [time] [message]` |
| `/timer` | Create a timer | `/timer [duration]` |
| `/decodebinary` | Decode binary | `/decodebinary [binary]` |

## 📋 Requirements

- Python 3.8 or higher
- discord.py 2.0+
- python-dotenv

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

## 🔧 Configuration

### Bot Intents

The bot requires the following intents:

- `guilds` - Access to guild information
- `members` - Access to member information
- `message_content` - Required for prefix commands

### Recommended Permissions

```
Ban Members
Kick Members
Moderate Members (Timeout)
Manage Roles
Manage Channels
Manage Messages
Read Messages/View Channels
Send Messages
Embed Links
Attach Files
Read Message History
```

**Permission Integer:** `1099511627830`

### Invite Link Template

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=1099511627830&scope=bot%20applications.commands
```

## 💡 Usage Examples

### Slash Commands

```
/ban @JohnDoe Spamming in chat
/mute @User 30m Inappropriate language
/warn @Member Breaking rules
/roleadd @User @Verified
/userinfo @Someone
/servericon
```

### Prefix Commands

```
!ban @JohnDoe Spamming in chat
!mute @User 30m Inappropriate language
!warn @Member Breaking rules
!roleadd @User @Verified
!userinfo @Someone
!servericon
```

### Mute Duration Formats

- `10m` - 10 minutes
- `2h` - 2 hours
- `1d` - 1 day
- `30` - 30 minutes (default unit)

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

If you encounter any bugs or have feature suggestions, please [open an issue](https://github.com/FrozenX2412/dc-bot/issues).

## 📞 Support

Need help? Resources:

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs/)
- [Project Issues](https://github.com/FrozenX2412/dc-bot/issues)

## ⭐ Features Roadmap

- [ ] Advanced logging system
- [ ] Custom prefix per guild
- [ ] Automated moderation (auto-mod)
- [ ] Music commands
- [ ] Leveling system
- [ ] Custom embed builder
- [ ] Dashboard web interface

---

**Made with ❤️ by FrozenX2412**

⭐ Star this repository if you find it helpful!
