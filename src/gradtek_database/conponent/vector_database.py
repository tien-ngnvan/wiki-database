import os
from gradtek_database.logging import logger
from sentence_transformers import SentenceTransformer, util
from gradtek_database.conponent import WikiDataIngestion
from gradtek_database.entity import EncodingParameters, EnvParameters
import dotenv
import psycopg2
from tqdm.auto import tqdm
from typing import List, Optional, Tuple
import torch
import math

class WikiSnippet: 
    def __init__(
        self, 
        params: Tuple[EncodingParameters, EnvParameters], 
        snippet
    ) -> None:
        self.encoding_params, self.env_params = params
        # Sentence Transformers automatically detects cuda or cpu
        self.passage_encoder = SentenceTransformer(self.encoding_params.context_model_name_or_path)
        
        self.snippet = snippet
        
    def check_database_exist(self): 
        """Check if database exists"""
        logger.info("Detecting database...")
        exists = True
        try:
            connection = psycopg2.connect(
                dbname=self.env_params.db_name,                        
                host=self.env_params.db_host,
                port=self.env_params.db_port,
                user=self.env_params.db_user,
                password=self.env_params.db_pwd
            )
            cursor = connection.cursor()
        except (Exception, psycopg2.Error) as e:
            logger.warning(e)
            exists = False
        return exists
    
    def check_table_exist(self):
        """Check if table exists"""
        exists = False
        logger.info(f"Detecting {self.env_params.tb_name}...")
        try:
            connection = psycopg2.connect(
                dbname=self.env_params.db_name,                        
                host=self.env_params.db_host,
                port=self.env_params.db_port,
                user=self.env_params.db_user,
                password=self.env_params.db_pwd
            )
            cursor = connection.cursor()
            cursor.execute(
                f"select exists(select * from information_schema.tables where table_name=%s)", (self.env_params.tb_name,)
            )
            exists = cursor.fetchone()[0]
        except (Exception, psycopg2.Error) as e:
            logger.warning(e)
        return exists

    def init_database(self): 
        """Create a database to contain a data table
        """
        if self.check_database_exist: 
            logger.info(f"Database {self.env_params.db_name} is detected.")
        else:
            logger.warning(f"Database {self.env_params.db_name} does not exist, start creating...")
            try:
                connection = psycopg2.connect(
                        host=self.env_params.db_host,
                        port=self.env_params.db_port,
                        dbname="postgres",
                        user=self.env_params.db_user,
                        password=self.env_params.db_pwd
                        )
                connection.autocommit = True
                cursor = connection.cursor()
                sql = '''CREATE DATABASE {};'''.format(self.env_params.db_name)
                cursor.execute(sql)

                logger.info(f"Database {self.env_params.db_name} is created successfully.")

                if connection:
                    cursor.close()
                    connection.close()

            except (Exception, psycopg2.Error) as e:
                logger.error(f"Error while connecting to PostgreSQL: {e}")

    def init_table(self): 
        """Create a table contains wiki snippets passages
        """
        if self.check_table_exist:
            logger.info(f"Table {self.env_params.tb_name} is detected")
        else:
            logger.warning(f"Table {self.env_params.tb_name} does not exist, start creating")
            try:
                connection = psycopg2.connect(
                    dbname=self.env_params.db_name,                        
                    host=self.env_params.db_host,
                    port=self.env_params.db_port,
                    user=self.env_params.db_user,
                    password=self.env_params.db_pwd
                )
                connection.autocommit = True

                cursor = connection.cursor()
                sql = f'''
                        CREATE EXTENSION IF NOT EXISTS vector;
                        CREATE TABLE {self.env_params.tb_name} (
                        id SERIAL PRIMARY KEY,
                        title TEXT,
                        name TEXT,
                        content TEXT,
                        embedd vector({self.encoding_params.embedding_size}));
                        '''

                cursor.execute(sql)
                logger.info(f"{self.env_params.tb_name} is created successfully.")

                if connection:
                    cursor.close()
                    connection.close()
                    logger.info("PostgreSQL connection is closed.")

            except (Exception, psycopg2.Error) as err:
                logger.error(f"Error while connecting to PostgreSQL: {err}")

    def count_row(self, tb_name: str) -> int:
        """Count the number of row in a table

        It helps us to keep inserting knowledge to the table

        Args:
            tb_name: name of table
        """
        try:
            connection = psycopg2.connect(
                dbname=self.env_params.db_name,                        
                host=self.env_params.db_host,
                port=self.env_params.db_port,
                user=self.env_params.db_user,
                password=self.env_params.db_pwd
            )
            connection.autocommit = True

            cursor = connection.cursor()
            sql = f'''
                    SELECT count(*) FROM {tb_name}
                    '''

            cursor.execute(sql)
            result = cursor.fetchone()[0]

            if connection:
                cursor.close()
                connection.close()
                logger.info("PostgreSQL connection is closed.")
            return result

        except (Exception, psycopg2.Error) as err:
            logger.error(f"Error while connecting to PostgreSQL: {err}")
            return -1

    def insert(self): 
        """Insert wiki snippets or knowledge to wiki table

        Args:
            context_encoder: a model that encodes data to embedding
            context_tokenizer: a tokenizer that creates input for `context_encoder`
            snippets: dataset object that contains wikipedia snippet passages
        """
        logger.info(f"Starting inserting knowledge to {self.env_params.tb_name}")

        try:
            connection = psycopg2.connect(
                dbname=self.env_params.db_name,                        
                host=self.env_params.db_host,
                port=self.env_params.db_port,
                user=self.env_params.db_user,
                password=self.env_params.db_pwd
            )

            cursor = connection.cursor()
            logger.info("Database connection established")

            def _insert(
                batch_titles: List[str],
                batch_names: List[str],
                batch_contents: List[str],
                ) -> None:

                passage_embd = self.passage_encoder.encode(batch_contents) # [batch, embedding_dim]
                embd = list(map(lambda x: str(x),passage_embd.tolist())) # List[str(array)]
                values =  list(zip(batch_titles, batch_names, batch_contents, embd))
                args = ','.join(cursor.mogrify("(%s,%s,%s,%s)", i).decode('utf-8') for i in values)
                sql_insert_query = f"""
                        INSERT INTO {self.env_params.tb_name} (title, name, content, embedd)
                        VALUES"""
                cursor.execute(sql_insert_query + (args))
                connection.commit()

            current_id = self.count_row(tb_name=self.env_params.tb_name)
            batch_titles = []
            batch_names = []
            batch_contents = []

            for idx, article in tqdm(enumerate(self.snippet)): 
                if idx < current_id: 
                    continue
                batch_titles.append(str(article["section_title"]))
                batch_names.append(str(article["article_title"]))
                batch_contents.append(str(article["passage_text"]))
                if len(batch_contents) == self.env_params.batch:
                    assert len(batch_titles) == len(batch_names) == len(batch_contents), \
                            f"len(batch_titles): {len(batch_titles)} "\
                            f"len(batch_names): {len(batch_names)}"\
                            f"len(batch_contents): {len(batch_contents)}"
                    _insert(
                        batch_titles=batch_titles,
                        batch_names=batch_names,
                        batch_contents=batch_contents,
                    )
                    batch_titles.clear()
                    batch_names.clear()
                    batch_contents.clear()
            if connection:
                cursor.close()
                connection.close()
                logger.info("Connection closed")
                logger.info("Knowledge insertions completed")
            
        except (Exception, psycopg2.Error) as e:
            logger.error(f"Failed inserting knowledge into {self.env_params.tb_name}: {e}")
    
    def insert_multiprocess(self): 
        """Insert wiki snippets or knowledge to wiki table (multiprocessing)"""
        logger.info(f"Starting inserting knowledge to {self.env_params.tb_name}")
        
        try:
            connection = psycopg2.connect(
                dbname=self.env_params.db_name,                        
                host=self.env_params.db_host,
                port=self.env_params.db_port,
                user=self.env_params.db_user,
                password=self.env_params.db_pwd
            )

            cursor = connection.cursor()
            logger.info("Database connection established")
            #Start the multi-process pool on all available CUDA devices
            pool = self.passage_encoder.start_multi_process_pool()
            
            def _insert(
                batch_titles: List[str],
                batch_names: List[str],
                batch_contents: List[str],
                ) -> None:

                #Compute the embeddings using the multi-process pool
                passage_embd = self.passage_encoder.encode_multi_process(batch_contents, pool) # [batch, embedding_dim]
                embd = list(map(lambda x: str(x),passage_embd.tolist())) # List[str(array)]
                values =  list(zip(batch_titles, batch_names, batch_contents, embd))
                args = ','.join(cursor.mogrify("(%s,%s,%s,%s)", i).decode('utf-8') for i in values)
                sql_insert_query = f"""
                        INSERT INTO {self.env_params.tb_name} (title, name, content, embedd)
                        VALUES"""
                cursor.execute(sql_insert_query + (args))
                connection.commit()

            
            current_id = self.count_row(tb_name=self.env_params.tb_name)
            batch_titles = []
            batch_names = []
            batch_contents = []

            for idx, article in tqdm(enumerate(self.snippet)): 
                if idx < current_id: 
                    continue
                batch_titles.append(str(article["section_title"]))
                batch_names.append(str(article["article_title"]))
                batch_contents.append(str(article["passage_text"]))
                if len(batch_contents) == self.env_params.batch:
                    assert len(batch_titles) == len(batch_names) == len(batch_contents), \
                            f"len(batch_titles): {len(batch_titles)} "\
                            f"len(batch_names): {len(batch_names)}"\
                            f"len(batch_contents): {len(batch_contents)}"
                    _insert(
                        batch_titles=batch_titles,
                        batch_names=batch_names,
                        batch_contents=batch_contents,
                    )
                    batch_titles.clear()
                    batch_names.clear()
                    batch_contents.clear()
                    
            self.passage_encoder.stop_multi_process_pool(pool)
            if connection:
                cursor.close()
                connection.close()
                logger.info("Connection closed")
                logger.info("Knowledge insertions completed")
            
        except (Exception, psycopg2.Error) as e:
            logger.error(f"Failed inserting knowledge into {self.env_params.tb_name}: {e}")  

    def create_index(
        self,
        tb_name: str,
        num_data: int,
    ) -> None:
        """Create index for embedding column

        Args:
            num_data: number of data or number of rows in the table
        """
        try:
            logger.info("Creating index...")
            connection = psycopg2.connect(
                dbname=self.env_params.db_name,                        
                host=self.env_params.db_host,
                port=self.env_params.db_port,
                user=self.env_params.db_user,
                password=self.env_params.db_pwd
            )
            connection.autocommit = True

            cursor = connection.cursor()
            nlist =  round(2*math.sqrt(num_data))

            create_index_cluster_cmd = f'''
                    SET maintenance_work_mem TO '14 GB';
                    CREATE INDEX ON {tb_name} USING ivfflat (embedd vector_ip_ops) WITH (lists = {nlist});
                    '''
            create_index_default_cmd = f'''
                    CREATE INDEX ON {tb_name} USING ivfflat (embedd vector_ip_ops);
                    '''
            try:
                logger.info(f"Creating index with {nlist} cluster")
                cursor.execute(create_index_cluster_cmd)
            except:
                logger.error(f"Created index clustering on {tb_name} was failed, try default settings")
                cursor.execute(create_index_default_cmd)
            logger.info("Create index successfully")
            if connection:
                cursor.close()
                connection.close()
                logger.info("PostgreSQL connection is closed")

        except (Exception, psycopg2.Error) as err:
            logger.error("Error while connecting to PostgreSQL", err)
    
    def pipeline(self): 
        self.init_database()
        self.init_table()
        if self.encoding_params.purpose == "init_db":
            if self.encoding_params.multiprocessing: 
                self.insert_multiprocess()
            else: 
                self.insert()
        num_data = self.count_row(self.env_params.tb_name)
        self.create_index(
            tb_name=self.env_params.tb_name, 
            num_data=num_data
        )