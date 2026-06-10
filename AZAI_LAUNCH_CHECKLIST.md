# AZAI Launch Checklist

EGO NETWORK · EST. 2026  
Owner: MR EGO

## Current Build Status

AZAI is in launch-prep stage.

Core systems are added. Final launch needs restart, live testing, and bug fixes.

## Done

- Start panel and help system
- Command center menu
- Owner panel control center
- Group verification base
- Profile setup base
- AI chat with short memory
- Log guard
- Moderation base
- Economy base with EGO CREDIT
- Market base
- Item image save and caption card system
- Referral system
- Family system
- Removed shortcut guard
- Anime quiz system with economy reward

## Anime Quiz Reward

- Correct answer: 100 EC and 15 XP
- Wrong answer: 0
- Daily reward limit: 10 quiz per user
- 5 correct streak bonus: 200 EC

## Image Card System

Use this command by replying to an item image:

```text
/setitempic item_id
```

Examples:

```text
/setitempic bike_splendor
/setitempic car_scorpio_s11_black
/setitempic rose
```

When item image is saved, buy, garage, and gift flows should show image with caption.

## Anime Quiz Setup

Owner adds quiz by replying to anime image:

```text
/addanimeq answer | option1 | option2 | option3 | option4
```

Example:

```text
/addanimeq Naruto | Naruto | Luffy | Gojo | Eren
```

User commands:

```text
/animeguess
/quiz
/quizstats
/quiztop
/quizon
/quizoff
```

## Must Test After Restart

1. `/start`
2. `/commands`
3. `/owner`
4. `/verify`
5. `/verifyall`
6. `/unverifyall`
7. `/wallet`
8. `/daily`
9. `/shop`
10. `/setitempic item_id`
11. item buy flow
12. `/garage`
13. `/gift item_id`
14. `/addanimeq answer | option1 | option2 | option3 | option4`
15. `/animeguess`
16. quiz buttons
17. `/quizstats`
18. `/quiztop`
19. group mention AI reply
20. DM AI reply

## Manual / Deferred

Events and birthday panel is deferred for now because automated GitHub patching was blocked.

## Launch Rule

Do not publish directly after restart.

Run live group testing first, then fix errors for 1-2 days, then publish the cleaner version.
