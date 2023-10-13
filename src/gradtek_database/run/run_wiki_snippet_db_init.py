from gradtek_database.conponent import (
    WikiSnippet, 
    WikiDataIngestion
)
from gradtek_database.configs import ConfigurationManager
from gradtek_database.constant import *
from gradtek_database.logging import logger
def main(): 
    config = ConfigurationManager(
        config_filepath=CONFIG_FILE_PATH, 
        param_filepath=PARAMS_FILE_PATH
    )

    STAGE_NAME = "DATA INGESTION STAGE"
    try: 
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        data_ingestion = WikiDataIngestion(config=config)
        wiki_snippet = data_ingestion.pipeline()
        encoding_parameters = data_ingestion.get_encoding_params()
        env_parameters = data_ingestion.get_env_params()
    except Exception as e:
        logger.exception(e)
        raise e

    STAGE_NAME = "VECTOR DATABASE INITIALIZATION STAGE"
    try: 
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        wiki = WikiSnippet(
            params=(encoding_parameters, env_parameters), 
            snippet=wiki_snippet
        )
        wiki.pipeline()
    except Exception as e:
        logger.exception(e)
        raise e