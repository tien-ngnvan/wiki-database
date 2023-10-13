from pathlib import Path
from gradtek_database.constant import *
from gradtek_database.utils import (
    read_yaml, 
    create_directories
)
from gradtek_database.entity import (
    DataIngestionConfig, 
    DataValidationConfig, 
    EncodingParameters, 
    EnvParameters
)

class ConfigurationManager: 
    def __init__(
        self, 
        config_filepath: Path = CONFIG_FILE_PATH, 
        param_filepath: Path = PARAMS_FILE_PATH
    ) -> None:
        self.config = read_yaml(config_filepath)
        self.param = read_yaml(param_filepath)

        create_directories([self.config.artifacts_root])
    
    def get_data_ingestion_config(self) -> DataIngestionConfig: 
        """create instace for data ingestion config"""
        config = self.config.data_ingestion
        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_url=config.source_url,
            id_download=config.id_download,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir, 
            data_path=config.data_path,
        )
        return data_ingestion_config
    
    def get_data_validation_config(self): 
        config = self.config.data_validation

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir = config.root_dir,
            status_file = config.status_file,
            all_required_files = config.all_required_files, 
            data_path=config.data_path, 
            mock_data_url_id=config.mock_data_url_id, 
            local_mock_data_file=config.local_mock_data_file, 
            unzip_dir=config.unzip_dir, 
            mock_data_path=config.mock_data_path
        )

        return data_validation_config
    
    def get_encoding_parameters(self): 
        encoding_params = self.param.encoding

        parameters = EncodingParameters(
            context_model_name_or_path=encoding_params.context_model_name_or_path,
            dataset_name=encoding_params.dataset_name,
            dataset_version=encoding_params.dataset_version,
            target_devices=encoding_params.target_devices,
            multiprocessing=encoding_params.multiprocessing,
            embedding_size=encoding_params.embedding_size,
            encoding=encoding_params.encoding, 
            streaming=encoding_params.streaming,
            num_proc=encoding_params.num_proc,
            purpose=encoding_params.purpose
        )

        return parameters
    
    def get_env_parameters(self): 
        env_params = self.param.env

        parameters = EnvParameters(
            db_name=env_params.db_name,
            db_host=env_params.db_host, 
            db_port=env_params.db_port,
            db_user=env_params.db_user,
            db_pwd=env_params.db_pwd,
            tb_name=env_params.tb_name,
            batch=env_params.batch
        )

        return parameters