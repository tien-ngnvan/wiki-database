# wiki-database
## Setup
```bash
conda create -n wiki python==3.8 -y
conda activate wiki
pip install -r requirements.txt
```
## .env
- Please access `.env` file to modify database information in order to connect to the database
```bash
PGDBNAME="postgre"
PGHOST="localhost"
PGPORT="postgre"
PGUSER="postgre"
PGPWD="postgre"
TB_WIKI="wiki_tb"
TB_CLIENT="client_tb"
BATCH=16
```
## Implement
### Multi process (hotfix)
- create 2 terminal windows 
- At the first terminal, run:
```bash
CUDA_VISIBLE_DEVICES=0 python src/run.py --n_gpus 2 --gpu_index 0
```
- At the second terminal, run:
```bash
CUDA_VISIBLE_DEVICES=0 python src/run.py --n_gpus 2 --gpu_index 1
```

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
- This script automatically create Wikipedia database with ~17M data. If you want to create Wikipedia database with ~33M data. add use argument: `--dataset_version wikipedia_en_100_0`
- When you have your own table filled up with data before and just want to create index, run:
```bash
python src/run.py --just_create_index \
                  --client_data_path </path/to/client/knowledge/csv>
```
### Create Client database
MSD knowledge can be download [here](https://drive.google.com/file/d/1S2i325zIv13O1IVoDj9jib9bsCUv20Pt/view?usp=sharing)
- if there is no database exists, run:
```bash
pthon src/run_client.py --init_db \
                        --client_data_path </path/to/client/knowledge/csv>
```
- if database already exists (you have your own database) and just want to create the table, run:
```bash
python src/run_client.py --init_tb \
                        --client_data_path </path/to/client/knowledge/csv>
```
- if database and table exist, just want to insert passages, run:
```bash
python src/run_client.py --client_data_path </path/to/client/knowledge/csv>
```
- When you have your own table filled up with data before and just want to create index, run:
```bash
python src/run.py --just_create_index \
                  --client_data_path </path/to/client/knowledge/csv>
```
*Note: When creating index, we try creating index with `4*sqrt(number_of_row)` first. If there were any error, It would automatically change creating index method with default cluster equals to 100*
