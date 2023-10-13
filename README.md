# wiki-database
## Download postgreSQL 
- PostgreSQL is used here which is taken from [pgvector](https://github.com/pgvector/pgvector) helps us speed up our retrieval task.
- Go to `Docker-compose.yml` to change `user` and `password`
```bash
docker-compose up
```
## Setup
```bash
conda create -n wiki python==3.10 -y
conda activate wiki
pip install -r requirements.txt
```
## Parameters
- modify your database configuration and encoding parameters in `./config/params.yaml`
```yaml
encoding:
  context_model_name_or_path: sentence-transformers/msmarco-bert-base-dot-v5
  dataset_name: wiki_snippets
  dataset_version: wiki40b_en_100_0
  target_devices: null
  multiprocessing: True
  embedding_size: 768
  encoding: "utf-8"
  streaming: true
  num_proc: 4
  purpose: "init_db"
env: 
  PGDBNAME: wikipedia_db
  PGHOST: localhost
  PGPORT: "5432"
  PGUSER: postgresql
  PGPWD: postgresql
  TB_WIKI: wiki_tb
  TB_CLIENT: client_tb
  BATCH: 1024
```
- `purpose`: If you wanted to initialize vector database, you could set `init_db`, if you already had your vector database initialized and just wanted to create index for speeding up querying, you would set `create_index`
- `target_devices`: If you do multiprocessing encoding, you need to specify all available devices. If it is null, model will detect all available devices

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
