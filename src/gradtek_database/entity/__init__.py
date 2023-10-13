from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

@dataclass
class DataIngestionConfig: 
    root_dir: Path
    source_url: str
    id_download: str
    local_data_file: Path
    unzip_dir: Path
    data_path: Path
    
@dataclass(frozen=True)
class DataValidationConfig: 
    root_dir: Path
    status_file: Path
    all_required_files: list
    data_path: Path
    mock_data_url_id: str
    local_mock_data_file: Path
    unzip_dir: Path
    mock_data_path: Path

@dataclass(frozen=True)
class EncodingParameters: 
    context_model_name_or_path: str
    dataset_name: str
    dataset_version: str
    target_devices: Optional[List[str]]
    multiprocessing: bool
    embedding_size: int
    encoding: str
    streaming: bool
    num_proc: int
    purpose: str

@dataclass(frozen=True)
class EnvParameters: 
    db_name: str
    db_host: str
    db_port: str
    db_user: str
    db_pwd: str
    tb_name: str
    batch: int