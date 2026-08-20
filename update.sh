#!/bin/bash
cd /home/deploy/transparencia-osint
python3 transp_reingest.py >> logs/update.log 2>&1
python3 gen_transp_dash4.py >> logs/update.log 2>&1
echo "[$(date -u +%FT%TZ)] actualizado" >> logs/update.log
