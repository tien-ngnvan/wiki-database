# wiki-database
## Setup
```bash
conda create -n wiki python==3.8 -y
conda activate wiki
pip install -r requirements.txt
```
- Please access `.env` file to modify database information in order to connect to the database

## Implement
### Create Wikipedia database
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
- This script automatically create Wikipedia database with ~17M data. If you want to create Wikipedia database with ~33M
  data. add use argument: `--dataset_version wikipedia_en_100_0`
### Just Create index
- When you have your own table filled up with data before and just want to create index, run:
```bash
python src/run.py --just_create_index
```
