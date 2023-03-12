# wiki-database
## Setup
```bash
conda create -n wiki python==3.8 -y
conda activate wiki
pip install -r requirements.txt
```
- Please access `.env` file to modify database information in order to connect to the database

## Implement
- if there is no database exists, run:
```bash
pthon src/run.py --init_db
```
- if database already exists (you have your own database) and just want to create the table, run:
```bash
python src/run.py --init_tb
```
- if database and table exist, just want to insert passages, run:
```bash
python src/run.py
```
