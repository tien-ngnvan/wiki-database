import datasets
from datasets import load_dataset

def download_dataset(
        dataset_name:str = "wiki_snippets",
        dataset_version: str = "wiki40b_en_100_0",
        streaming: bool = True
        ) -> datasets.iterable_dataset.IterableDataset:
    """Download dataset (Wikipedia) from Huggingface

    Args:
        dataset_name: name of the dataset we want to download
        dataset_version: configuration of the dataset. For example,
                        wiki_snippets performs 2 configuration of dataset
                        (with 100 snippet passage length and 0 overlap) in
                        English: `wiki40b_en_100_0` with 17 553 713 snippets
                        passages, and `wikipedia_en_100_0` with 33 849 898
                        snippets passages
        streaming: When a dataset is in streaming mode, we can iterate over it
                    directly without having to download the entire dataset. This
                    is useful if we don't have enough space on our disk to donwload
                    dataset, or if we don't want to wait for our dataset to be downloaded
                    before using it. Wikipedia tasks hours to downloaded, then it should be
                    accessed in streaming mode.

    Returns:
        wiki_snippets


    """
    wiki_snippet = load_dataset(
            dataset_name,
            name=dataset_version,
            streaming=streaming
            )["train"]
    return wiki_snippet
