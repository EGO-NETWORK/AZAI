# AZAI Economy Blueprint

EGO Network - EST. 2026

## Current Lock

Currency name: EGO CREDIT
Short form: EC

Branding rule:
- Do not force EGO wording everywhere.
- Use clean names such as Market, Wallet, Garage, Vault, Inventory, Leaderboard.
- Keep EGO Network only as brand footer or official network mention.

## Economy Core

Rewards:
- Daily reward: 100 EC
- Chat activity reward: every 10 valid messages gives 5 EC and 10 XP
- Chat reward cooldown: 60 seconds per user
- Quiz reward: planned
- Admin gift: planned
- Refer earn: planned

Level plan:
- Level 1 = 0 XP
- Level 2 = 100 XP
- Level 3 = 250 XP
- Level 4 = 500 XP
- Level 5 = 900 XP

REP:
- One user can give +1 REP to one user per day.

Credit send:
- Use /send instead of /transfer.
- Display name: Send Credits.
- Fee: 3 percent.
- Example: sending 100 EC gives receiver 97 EC and burns 3 EC.

## Public Economy Commands

- /wallet
- /balance
- /daily
- /send
- /leaderboard
- /rep
- /myrep
- /inventory
- /refer
- /redeemref

## Admin / Owner Economy Commands

- /give
- /take
- /resetwallet

## Market / Shop Structure

Use /shop for the main market panel.

Main buttons:
- Cars
- Bikes
- Gifts
- Boosters
- Titles
- Badges
- Garage
- Inventory
- Vault
- Close

Important:
- Cars and Bikes must be provided by owner before adding lists.
- Item images can be saved when owner provides them.
- Start media, PFP, and banner are final-launch tasks.

## Working Item Categories

### Cars

Working use:
- Save bought cars in garage.
- Allow active car selection.
- Show active car in profile later.
- Future race/event usage possible.

Owner must provide:
- Car name
- Price in EC
- Rarity
- Image if available

### Bikes

Working use:
- Save bought bikes in garage.
- Allow active bike selection.
- Show active bike in profile later.
- Future race/event usage possible.

Owner must provide:
- Bike name
- Price in EC
- Rarity
- Image if available

### Gifts

Starter gift list from owner reference:
- Rose = 500 EC
- Chocolate = 800 EC
- Ring = 2000 EC
- Teddy Bear = 1500 EC
- Pizza = 600 EC
- Surprise Box = 2500 EC
- Puppy = 3000 EC
- Cake = 1000 EC
- Love Letter = 400 EC
- Cat = 2500 EC
- Tulip = 1500 EC

Rules:
- Gift command should work by replying to a user.
- Gift is saved in receiver inventory or gift history.
- Gift image/sticker can be sent if owner provides media.
- Girlfriend/Boyfriend must not be treated as a normal buyable market item.
- If relationship style feature is added later, it should be consent-based, not direct purchase.

### Boosters

Working boosters:
- XP Booster: increases XP reward for a limited time.
- Credit Booster: increases chat EC reward for a limited time.
- Daily Booster: increases next daily reward once.

### Titles

Working use:
- Bought titles are saved.
- User can set active title later.
- Active title can show in profile later.

### Badges

Working use:
- Bought badges are saved.
- Badges can show in profile later.
- Special badges can be event or owner-gift only.

### Vault

Use /vault.

Purpose:
- Rare items
- Limited event items
- Owner-gifted items
- Special collectibles

Vault should feel premium and separate from normal market.

## Image Collection Plan

Ask owner for images when needed:
- Shop main panel image
- Vault image
- Car category image
- Bike category image
- Gift item images
- Title or badge background

Do not add final start media, PFP, or banner before final visual approval.

## Naming Decision

Use /send instead of /transfer.

Reason:
- Shorter
- Cleaner
- Easier for users
- Better for button text: Send Credits

## Pending Before Code

Need owner to provide:
- Car list
- Bike list
- Any extra working gift list
- Optional shop and item images

Code can begin with:
- Wallet
- Daily
- Send Credits with 3 percent fee
- REP
- Leaderboard panel
- Inventory skeleton
- Refer earn skeleton
- Shop/Garage/Vault skeleton with starter gifts only
