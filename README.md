<h1 align="center">𓆩⚚ 𝐀𝐙𝐀𝐈 ⚚𓆪</h1>

<h3 align="center">𝐄𝐆𝐎 𝐍𝐄𝐓𝐖𝐎𝐑𝐊 · 𝐄𝐒𝐓. 2026</h3>

<p align="center">
  <b>Official Telegram Community Automation System</b><br>
  Built for verification, protection, economy, anime quiz, shop, garage, gifts, AI chat, owner control, and clean group management.
</p>

---

## Owner

**MR EGO**  
Founder and Owner of EGO NETWORK

- Master: https://t.me/EGOISTICxPRIME
- Updates: https://t.me/EGOxUPDATES
- Support: https://t.me/EGOxSUPPORT

---

## About AZAI

AZAI is the official community automation system of EGO NETWORK.

It is designed for Telegram communities that need verification, moderation, economy, rewards, anime quiz, shop and garage systems, owner tools, and AI chat in one organized bot.

This repository is maintained as a private EGO Network system.

---

## Current Ready Features

### Protection

- Verification system
- /verify, /verifyall, /unverifyall
- Verified and unverified user tracking
- Owner-managed group safety flow

### Economy

- Ego Credits wallet
- /wallet and /balance
- /daily rewards
- /send transfer
- REP, XP, activity reward support
- /leaderboard with display names and usernames

### Market / Garage

- /shop
- /buy item_id
- /inventory
- /garage
- /setbike item_id
- /setcar item_id
- Item ID guide after buying
- Vehicle ID guide inside garage
- Item picture support through /setitempic

### Gift System

- /gift item_id
- Gift is sent as a reply to the target user's message
- Sender and receiver display name support
- Gift price deduction from wallet
- Gift image support when item media is set

### Anime Quiz

- Anime character image quiz
- Four-option answer buttons
- One-attempt answer protection
- Correct answer rewards
- Daily quiz limit and streak reward support

### Family System

- /brother
- /sister
- /adopt
- /family
- /familytree
- /leavefamily
- Name and username display instead of raw user IDs

### AI Chat

- AZAI group and DM AI replies
- Groq API support
- Short chat memory
- Owner recognition
- Bhabhi Ji / Ma'am respectful address support

### Owner Tools

- /owner panel
- Guide button
- Start panel media setup through /setstartpic
- Logger controls through /logon, /logoff, /logstatus
- /alive, /ping, /repo branded AZAI responses

---

## Environment Notes

Required secrets should be stored only in deployment environment variables. Never commit real tokens or database URLs.

Recommended AI variables:

```env
GROQ_API_KEY=your_groq_key
GQRI_API_KEY=your_groq_key
```

If AI does not reply, first check the owner panel AI status and deployment secrets.

---

## Current Pending / Manual Features

These are not marked ready yet:

- Broadcast system
- Events / birthday panel
- Full live restart test

Telegram limitations still apply:

- A bot cannot DM users unless they have started the bot.
- A bot cannot send messages in groups where it lacks permission.
- A bot cannot pin messages unless it is admin with pin permission.

---

## Launch Checklist

Before public use:

- Restart the bot
- Test /settings
- Test /shop
- Test /shop@botusername
- Test /gift item_id by replying to a user message
- Test /garage
- Test /leaderboard
- Test /animeguess
- Test AI chat after setting Groq secrets
- Check /owner panel
- Check /ping

---

## Brand

AZAI is part of EGO NETWORK · EST. 2026.

Official links:

- Master: https://t.me/EGOISTICxPRIME
- Updates: https://t.me/EGOxUPDATES
- Support: https://t.me/EGOxSUPPORT
