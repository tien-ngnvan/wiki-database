import os 
from gradtek_database.logging import logger 
from datasets import load_from_disk, DatasetDict
import pandas as pd
from pathlib import Path
from gradtek_database.entity import EncodingParameters
from gradtek_database.utils import (
    has_unicode_quotes, 
    has_byte_string, 
    has_bullets, 
    has_dashes, 
    has_extra_whitespace, 
    has_non_ascii_chars, 
    has_ordered_bullets
)
from typing import Optional
from transformers import AutoTokenizer

class DataValidation: 
    """Validate custom dataset
    
    When clients provide their own dataset, it needs to be validated 
    before being encoded and stored in the database
    """
    def __init__(self, encoding_param: EncodingParameters, dataset: Optional[DatasetDict] = None) -> None:
        self.encoding_param = encoding_param
        self.results = {"Test cases": [], "Status": []}
        self.length_statistics = {"Name":[], "Values": []}
        self.dataset = dataset if dataset is not None else load_from_disk(self.config.data_path)

    def is_text_cleaned(self): 
        def batch_process(examples): 
            status = []
            for passage_text in examples["passage_text"]: 
                text_has_unicode_quotes = has_unicode_quotes(passage_text)
                text_has_byte_string = has_byte_string(passage_text)
                text_has_bullets = has_bullets(passage_text)
                text_has_dashes = has_dashes(passage_text)
                text_has_extra_whitespace = has_extra_whitespace(passage_text)
                text_has_non_ascii_chars = has_non_ascii_chars(passage_text)
                text_has_ordered_bullets = has_ordered_bullets(passage_text)
                status.append({
                    "text_has_unicode_quotes": text_has_unicode_quotes, 
                    "text_has_byte_string": text_has_byte_string, 
                    "text_has_bullets": text_has_bullets, 
                    "text_has_dashes": text_has_dashes, 
                    "text_has_extra_whitespace": text_has_extra_whitespace, 
                    "text_has_non_ascii_chars": text_has_non_ascii_chars, 
                    "text_has_ordered_bullets": text_has_ordered_bullets
                })

            examples["status"] = status
            return examples
        check_cleaned_dataset = self.dataset.map(batch_process, batched=True, num_proc=self.encoding_param.num_proc)
        
        
    def is_text_length_qualified(self): 
        tokenizer = AutoTokenizer.from_pretrained(self.encoding_param.context_model_name_or_path)
        def batch_process(examples): 
            input_ids = tokenizer(examples["passage_text"], truncation=False, padding=False).input_ids
            lengths = [len(inp) for inp in input_ids]
            examples["length"] = lengths
            examples["less_than_length_100"] = lengths < 100
            return examples
        
        check_qualified_length = self.dataset.map(batch_process, batched=True, num_proc=self.encoding_param.num_proc)
        return all(check_qualified_length["less_than_length_100"])


    def validate(self): 
        test1 = self.test_required_dataset_folder()
        test2 = self.test_required_files()
        test3 = self.test_load_dataset()
        test4 = self.test_dataset_type()
        test5 = self.test_dataset_attributes()

        result_df = pd.DataFrame(self.results)
        
        result_df.to_csv(self.config.status_file, index=False)
        logger.info(f"Result file is saved at {self.config.status_file}")

        return test1 and test2 and test3 and test4 and test5