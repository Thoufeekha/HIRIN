@echo off
set PYTHONUTF8=1
cd /d "E:\job app\HIREIN\HIRIN"
python manage.py fetch_park_jobs >> scraper_log.txt 2>&1