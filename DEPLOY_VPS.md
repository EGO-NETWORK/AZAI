# AZAI VPS DEPLOYMENT

EGO NETWORK · MR EGO

This guide is for hosting AZAI on a paid VPS with systemd.
Do not commit real tokens, database URLs, API keys, or private IDs.

## 1. Server packages

```bash
apt update
apt install -y git python3 python3-pip python3-venv ffmpeg tmux screen nano curl build-essential
```

## 2. Clone repo

```bash
mkdir -p /home/bots
cd /home/bots
git clone -b ALONE https://github.com/EGO-NETWORK/AZAI.git AZAI
cd AZAI
```

If repo is already cloned:

```bash
cd /home/bots/AZAI
git pull origin ALONE
```

## 3. Python venv

```bash
cd /home/bots/AZAI
python3 -m venv venv
source venv/bin/activate
pip install -U pip wheel setuptools
pip install -r requirements.txt
```

## 4. Environment file

Create `.env` on VPS only:

```bash
nano /home/bots/AZAI/.env
```

Use `.env.example` as the template.
Never paste real secrets into GitHub.

Important keys:

```env
TOKEN=
API_ID=
API_HASH=
DB_URL=
OWNER_ID=
GROQ_API_KEY=
GQRI_API_KEY=
ALIZA_ID=
BHABHI_ID=
LOG_GROUP_ID=
AZAI_TODAY_FESTIVAL=
```

## 5. Compile check

```bash
cd /home/bots/AZAI
source venv/bin/activate
python -m compileall AloneX/plugins
```

If compile fails, fix before starting systemd.

## 6. Manual test run

```bash
cd /home/bots/AZAI
source venv/bin/activate
python3 -m AloneX
```

Stop with `CTRL+C` after confirming it starts.

## 7. Install systemd service

```bash
cp /home/bots/AZAI/deploy/azai.service /etc/systemd/system/azai.service
systemctl daemon-reload
systemctl enable azai
systemctl start azai
```

## 8. Check status and logs

```bash
systemctl status azai
journalctl -u azai -f
```

## 9. Restart / stop

```bash
systemctl restart azai
systemctl stop azai
```

## 10. Bot health command

After bot starts, send this from owner account:

```text
/azstatus
```

It should show AI key, DB env, owner IDs, Bhabhi IDs, time mode, festival mode, and important plugin file checks.

## 11. Festival manual mode

For moving festivals that do not have a fixed date, set this in `.env`:

```env
AZAI_TODAY_FESTIVAL=DIWALI
```

Examples:

```env
AZAI_TODAY_FESTIVAL=EID
AZAI_TODAY_FESTIVAL=HOLI
AZAI_TODAY_FESTIVAL=RAKSHA BANDHAN
```

Restart after changing `.env`:

```bash
systemctl restart azai
```
