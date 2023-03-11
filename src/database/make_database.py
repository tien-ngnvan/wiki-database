import os
import sys
from tqdm.auto import tqdm
import psycopg2
from psycopg2 import Error
import math
from transformers import (
        DPRContextEncoderTokenizer,
        DPRContextEncoder
        )
import datasets

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from model.retriever_model import (
         get_ctx_embd
         )

import logging
import dotenv

logger = logging.getLogger(__name__)

dotenv.load_dotenv()

PGDBNAME=os.getenv("DBNAME", "wiki_pgvector")
PGHOST=os.getenv("HOST", "localhost")
PGPORT=os.getenv("PORT", "5432")
PGUSER=os.getenv("USER", "wiki_ad")
PGPWD=os.getenv("PASSWORD", "55235")
TB_WIKI=os.getenv("TB_WIKI", "wiki_tb")

def create_postgres_db() -> None:
    """Create a database to contain a data table
    """
    try:
        connection = psycopg2.connect(
                host=PGHOST,
                port=PGPORT,
                dbname="postgres",
                user=PGUSER,
                password=PGPWD
                )
        connection.autocommit = True
        cursor = connection.cursor()
        sql = '''CREATE DATABASE {};'''.format(PGDBNAME)
        cursor.execute(sql)

        logger.info(f"Database {PGDBNAME} is created successfully.")

        if connection:
            cursor.close()
            connection.close()

    except (Exception, Error) as e:
        logger.error(f"Error while connecting to PostgreSQL: {e}")

def create_wiki_table() -> None:
    """Create a table contains wiki snippets passages
    """
    try:
        connection = psycopg2.connect(dbname=PGDBNAME,
                                      host=PGHOST,
                                      port=PGPORT,
                                      user=PGUSER,
                                      password=PGPWD)
        connection.autocommit = True

        cursor = connection.cursor()
        sql = f'''
                CREATE EXTENSION IF NOT EXISTS vector;
                CREATE TABLE {TB_WIKI} (
                id SERIAL PRIMARY KEY,
                title VARCHAR,
                name VARCHAR,
                content VARCHAR,
                embedd vector(128));
                '''

        cursor.execute(sql)
        logger.info(f"{TB_WIKI} is created successfully.")

        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed.")

    except (Exception, Error) as err:
        logger.error(f"Error while connecting to PostgreSQL: {err}")

def insert_knowedges(
        context_encoder: DPRContextEncoder,
        context_tokenizer: DPRContextEncoderTokenizer,
        snippets: datasets.iterable_dataset.IterableDataset
        )->None:
    """Insert wiki snippets or knowledge to wiki table

    Args:
        context_encoder: a model that encodes data to embedding
        context_tokenizer: a tokenizer that creates input for `context_encoder`
        snippets: dataset object that contains wikipedia snippet passages
    """
    logger.info(f"Starting inserting knowledge to {TB_WIKI}")

    try:
        connection = psycopg2.connect(dbname=PGDBNAME,
                                      host=PGHOST,
                                      port=PGPORT,
                                      user=PGUSER,
                                      password=PGPWD)

        cursor = connection.cursor()

        for _, article in enumerate(iter(snippets)):
            passage_embd = get_ctx_embd(
                    model_encoder=context_encoder,
                    tokenizer=context_tokenizer,
                    text=article["passage_text"]
                    )
            embd = str(list(passage_embd.cpu().detach().numpy().reshape(-1)))

            sql_insert_query = f"""INSERT INTO {TB_WIKI} (title, name, content, embedd) VALUES (%s, %s, %s, %s)"""
            result = cursor.execute(sql_insert_query, (article['section_title'], article['article_title'], article['passage_text'], embd))
            connection.commit()

        logger.info(f"Insert knowledges to {TB_WIKI} successfully")

        if connection:
            cursor.close()
            connection.close()
    except (Exception, Error) as e:
        logger.error(f"Failed inserting knowledge into {TB_WIKI}: {e}")

def create_index(
        num_data: int,
    ) -> None:
    """Create index for embedding column

    Args:
        num_data: number of data or number of rows in the table
    """
    try:
        print("Creating index")
        connection = psycopg2.connect(dbname=PGDBNAME,
                                      host=PGHOST,
                                      port=PGPORT,
                                      user=PGUSER,
                                      password=PGPWD)
        connection.autocommit = True

        cursor = connection.cursor()
        nlist =  round(2*math.sqrt(num_data))

        sql = f'''
                CREATE INDEX ON {TB_WIKI} USING ivfflat (embedd vector_ip_ops) WITH (lists = {nlist});
                '''

        cursor.execute(sql)
        logger.info(f"Created index on {TB_WIKI} successfully")

        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")

    except (Exception, psycopg2.Error) as err:
        logger.error("Error while connecting to PostgreSQL", err)

