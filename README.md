# 🤖 Discord Bot - Advanced Moderation & Info System

<div align="center">

![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A powerful, feature-rich Discord bot with **hybrid command support** (slash + prefix), **creative embeds**, and **multi-guild support**. Organized with modular cog architecture for easy maintenance.

</div>

---

## ✨ Key Features

- ✅ **Hybrid Commands** - Both `/slash` and `!prefix` command support
- ✅ **Creative Embed Design** - Master-designed beautiful embeds with unique styling for every command
- ✅ **Multi-Guild Support** - Seamlessly works across unlimited servers
- ✅ **Modular Architecture** - Organized folder structure with categorized cogs
- ✅ **Role Hierarchy Protection** - Smart permission checks prevent unauthorized actions
- ✅ **Comprehensive Error Handling** - User-friendly error messages
- ✅ **DM Notifications** - Members receive DM notifications for moderation actions
- ✅ **Persistent Data** - Warning tracking, blacklist system with JSON storage

---

## 📁 Project Structure

```
dc-bot/
├── cogs/
│   ├── moderation/          # 🛡️ All moderation commands
│   │   ├── ban.py
│   │   ├── unban.py
│   │   ├── kick.py
│   │   ├── mute.py
│   │   ├── unmute.py
│   │   ├── warn.py
│   │   ├── clear.py
│   │   ├── channel_management.py  # slowmode, lock, unlock
│   │   ├── role_management.py     # roleadd, roleremove, roleinfo
│   │   └── advanced_moderation.py # softban, prune, infractions, modlog, report, blacklist, whitelist
│   │
│   └── info/                # ℹ️ All information commands
│       ├── basic_info.py    # help, ping, uptime, stats
│       ├── user_info.py     # userinfo, whois, id, joined
│       └── server_info.py   # membercount, roles, channelinfo, emoji, emotes, servericon, boostcount, servercreated, invite
│
├── bot.py                   # Main bot file with cog loading
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## 🛡️ Moderation Commands

### Member Management
| Command | Description | Usage |
|---------|-------------|-------|
| `/ban` | Ban a member from the server | `/ban @user [reason]` |
| `/unban` | Unban a user by ID | `/unban <user_id> [reason]` |
| `/kick` | Kick a member from the server | `/kick @user [reason]` |
| `/mute` | Timeout a member | `/mute @user [duration] [reason]` |
| `/unmute` | Remove timeout from a member | `/unmute @user [reason]` |
| `/warn` | Issue a warning to a user | `/warn @user [reason]` |
| `/softban` | Ban and instantly unban (deletes messages) | `/softban @user [reason]` |

### Message & Channel Management
| Command | Description | Usage |
|---------|-------------|-------|
| `/clear` | Delete messages from channel | `/clear <amount>` |
| `/purge` | Alias for clear command | `/purge <amount>` |
| `/slowmode` | Set channel slowmode delay | `/slowmode <seconds>` |
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
| `/report` | Report a user to moderators | `/report @user <reason>` |
| `/blacklist` | Block user from bot usage (owner) | `/blacklist <user_id>` |
| `/whitelist` | Unblock user from bot usage (owner) | `/whitelist <user_id>` |

---

## ℹ️ Information Commands

### Bot Information
| Command | Description | Usage |
|---------|-------------|-------|
| `/help` | Shows all available commands | `/help` |
| `/ping` | Check bot latency | `/ping` |
| `/uptime` | Show how long bot has been online | `/uptime` |
| `/stats` | Display bot statistics | `/stats` |
| `/invite` | Generate bot invite link | `/invite` |

### User Information
| Command | Description | Usage |
|---------|-------------|-------|
| `/userinfo` | Display user information | `/userinfo [@user]` |
| `/whois` | Detailed user info (alias) | `/whois [@user]` |
| `/id` | Get user or server ID | `/id [@user]` |
| `/joined` | Show when user joined server | `/joined [@user]` |

### Server Information
| Command | Description | Usage |
|---------|-------------|-------|
| `/membercount` | Show server member count | `/membercount` |
| `/roles` | List all server roles | `/roles` |
| `/channelinfo` | Display channel information | `/channelinfo [channel]` |
| `/emoji` | Show server emojis | `/emoji` |
| `/emotes` | List custom emotes (alias) | `/emotes` |
| `/servericon` | Display server icon | `/servericon` |
| `/boostcount` | Show boost statistics | `/boostcount` |
| `/servercreated` | Show server creation date | `/servercreated` |

---

## 🎨 Creative Embed Features

Every command features **master-designed embeds** with:

- **Color-Coded Responses** - Different colors for success (green), warnings (yellow/orange), errors (red), and info (purple/blue)
- **Rich Field Layouts** - Organized information with emoji-enhanced field names
- **Timestamps** - All embeds include creation timestamps
- **Thumbnails & Images** - User avatars, server icons contextually displayed
- **Interactive Elements** - Clickable links, formatted code blocks, timestamp displays
- **Status Indicators** - Visual feedback with emojis (✅ ❌ ⚠️ 🟢 🔴)

**Example Embed Styles:**
- 🛡️ **Moderation Actions** - Red/orange tones with moderator info and reason fields
- ℹ️ **Information Displays** - Blue/purple tones with organized data fields
- ✅ **Success Messages** - Green tones with confirmation details
- 📊 **Statistics** - Purple gradient with visual data presentation

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

---

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

---

## 🤝 Contributing

Contributions are welcome! Here's how:

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

Need help? Resources:
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs/)
- [Project Issues](https://github.com/FrozenX2412/dc-bot/issues)

---

## ⭐ Features Roadmap

- [ ] Advanced logging system
- [ ] Custom prefix per guild
- [ ] Automated moderation (auto-mod)
- [ ] Music commands
- [ ] Leveling system
- [ ] Custom embed builder
- [ ] Dashboard web interface

---

<div align="center">

**Made with ❤️ by FrozenX2412**

⭐ Star this repository if you find it helpful!

</div>
