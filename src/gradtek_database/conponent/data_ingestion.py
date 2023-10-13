import os 
import tarfile
from gradtek_database.logging import logger
from gradtek_database.utils import get_size
from gradtek_database.entity import DataIngestionConfig, EncodingParameters
from gradtek_database.configs import ConfigurationManager
import gdown
from pathlib import Path

import datasets
from datasets import load_dataset
from datasets import Dataset
# conponent
class ClientDataIngestion: 
    def __init__(self, config: DataIngestionConfig) -> None:
        self.config = config
    
    def download_drive_file(self): 
        """Download dataset from google drive with gdown."""
        if not os.path.exists(self.config.local_data_file):
            gdown.download(id=self.config.id_download, quiet=False, output=self.config.local_data_file)
            # os.system(f"cd {self.config.root_dir}; gdown --id {self.config.id_download}; cd ../")
            logger.info(f"{os.path.basename(self.config.source_url)} downloaded.")
        else: 
            logger.info(f"{os.path.basename(self.config.source_url)} already exists of size: ~{get_size(Path(self.config.local_data_file))} KB")

    def untar_file(self): 
        """Untar .tar.gz file"""
        logger.info(f"Untar {self.config.local_data_file}")
        # open file
        file = tarfile.open(self.config.local_data_file)
        
        # print file names
        logger.info(file.getnames())
        
        # extract files
        file.extractall(self.config.unzip_dir)
        logger.info(f"{self.config.local_data_file} was extracted successfully to: {self.config.unzip_dir}")
        
        # close file
        file.close()

class WikiDataIngestion: 
    def __init__(self, config: ConfigurationManager) -> None:

        self.param = config.get_encoding_parameters()
        self.env_param = config.get_env_parameters()
    
    def download(self, streaming: bool): 
        """Download dataset from google drive with gdown."""
        wiki_snippet = load_dataset(
            self.param.dataset_name,
            name=self.param.dataset_version,
            streaming=streaming
            )["train"]
        return wiki_snippet
    
    def get_encoding_params(self): 
        return self.param
    
    def get_env_params(self): 
        return self.env_param
    
    def pipeline(self): 
        logger.info("Start to download Wiki Snippet")
        wiki_snippet = self.download(self.param.streaming)
        return wiki_snippet