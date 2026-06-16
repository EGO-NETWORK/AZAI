# START AZAI ON VPS

Use this when you want to test AZAI manually before systemd.

```bash
cd /home/bots/AZAI
source venv/bin/activate
python3 -m AloneX
```

Stop manual run with:

```text
CTRL+C
```

For permanent hosting, use the systemd file:

```bash
cp /home/bots/AZAI/deploy/azai.service /etc/systemd/system/azai.service
systemctl daemon-reload
systemctl enable azai
systemctl start azai
journalctl -u azai -f
```
