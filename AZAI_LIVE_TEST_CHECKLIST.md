# AZAI Live Test Checklist

EGO Network - EST. 2026

Use this checklist before calling AZAI production-ready.

## Test Rule

Do not mark any feature complete until it works in a real Telegram group or DM.

## Required Setup Before Test

Add these values in hosting secrets / environment settings:

- BOT_TOKEN or TOKEN
- BOT_USERNAME
- API_ID
- API_HASH
- DB_URL
- DB_URL2 if required by your deployment
- GROQ_API_KEY if testing AI later

Do not paste real secret values in public files.

## Phase 1 - Bot Start Test

Test in bot DM:

- Send /start
- Confirm media panel appears.
- Confirm Help button opens help menu.
- Confirm System Stats button opens stats.
- Confirm Updates button opens EGO updates channel.
- Confirm Support button opens EGO support channel.
- Confirm My Master button opens owner profile.
- Confirm Add AZAI To Your Empire opens group add link.

Expected result:

- Panel should use AZAI branding.
- Button labels should use the saved font style.
- No old Eiko or Alone public branding should appear in the start panel.

## Phase 2 - Profile Setup Test

Test in bot DM and group:

- Send /setup
- Send /setname Test User
- Send /setgender male
- Send /setbirthday 12/10
- Send /setreligion hindu
- Send /profile

Wrong input tests:

- /setbirthday 31/02 should be rejected.
- /setbirthday 12/13 should be rejected.
- /setgender random should be rejected.
- /setreligion random should be rejected.

Expected result:

- AZAI should never auto-detect name, gender, birthday, or religion.
- Only typed or selected data should be saved.
- /profile should show saved data.

## Phase 3 - Group Verification Test

Use a test group.

Bot permissions required:

- Add AZAI as admin.
- Allow delete messages.
- Allow read messages.
- Allow manage group if needed by the base repo.

Test as a normal member, not admin:

1. Send a normal message before verification.
2. Message should be deleted.
3. Send /verify.
4. Captcha should appear.
5. Select wrong answer.
6. Wrong answer alert should appear.
7. Send /verify again if needed.
8. Select correct answer.
9. Verification complete panel should appear.
10. Open Setup In DM button should open bot DM.
11. Send normal message again.
12. Message should stay.

Expected result:

- Before verification, only /verify is allowed.
- After verification, normal chatting works.
- Verification is group-specific.

## Phase 4 - Group-Specific Verification Test

Use two groups.

1. Verify in Group A.
2. Send normal message in Group A.
3. Join Group B.
4. Send normal message in Group B before verification.

Expected result:

- Group A should allow messages.
- Group B should still require /verify.
- One group verification must not unlock all groups.

## Phase 5 - Admin Verification Commands

Test as group admin:

- /verified
- /unverified
- /verifyall
- /unverifyall

Expected result:

- /verifyall should mark current group members verified.
- /unverifyall should force known members to verify again.
- /verified should show verified count.
- /unverified should show known unverified count.

Test as normal user:

- Send /verifyall
- Send /unverifyall

Expected result:

- Normal users should be rejected.

## Phase 6 - AI Status Test

Test:

- Send /aistatus

Expected result:

- If GROQ_API_KEY is set, status should show configured.
- If not set, status should show missing.
- Secret key must never be displayed.

## Known Pending After These Tests

- Full Groq AI chat reply system.
- Economy base.
- Shop and vault base.
- Anime quiz and GK quiz base.
- Birthday and festival scheduler.
- Owner panel and group panel.
- Mini App.
- Custom media commands.
- Image profile cards.

## Failure Report Format

When something fails, report it like this:

Command:
What happened:
Expected:
Screenshot or error:

This makes fixing faster and avoids guessing like a cursed fortune teller.
