import os
import logging
from sys import path
import torch
import pandas as pd

from configs.arguments import Arguments
from model import retriever_model
from database import make_database
from data import make_data

import dotenv

dotenv.load_dotenv()

PGDBNAME=os.getenv("PGDBNAME", "wiki_pgvector")
PGHOST=os.getenv("PGHOST", "localhost")
PGPORT=os.getenv("PGPORT", "5432")
PGUSER=os.getenv("PGUSER", "wiki_ad")
PGPWD=os.getenv("PGPWD", "55235")
TB_CLIENT=os.getenv("TB_CLIENT", "client_tb")
BATCH=int(os.getenv("BATCH", 16))

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

def call_sanity_check(path: str):
    """sanity check file requirements and extension

    """
    if len(path) == 0 or path is None or path.lower() == "none":
        raise ValueError("Need knowledge file")
    extension = path.split(".")[-1]
    assert extension == "csv", "knowledge file should be a csv file"

def main():
    arguments = Arguments()
    args = arguments.parse()

    logger.info(f"Read knowledges from {args.client_data_path}")
    call_sanity_check(path=args.client_data_path)
    client_df = pd.read_csv(args.client_data_path)
    row = client_df.shape[0]

    if not args.just_create_index:
        if args.init_db and not args.init_tb:
            make_database.create_postgres_db()
            make_database.create_client_table()
        elif args.init_tb and not args.init_db:
            make_database.create_client_table()
        elif not args.init_tb and not args.init_db:
            logger.warning("Make sure your database and table exist")
        else:
            ValueError("Database and table are created at the same time, or just a table is created")

        encoder_model, model_tokenizer = retriever_model.load_dpr_context_encoder(
                model_name_or_path="vblagoje/dpr-ctx_encoder-single-lfqa-wiki"
                )
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        encoder_model.to(device)
        encoder_model.eval()

        logger.info("Start inserting knowledges")
        make_database.insert_client_knowledges(
                context_encoder=encoder_model,
                context_tokenizer=model_tokenizer,
                snippets=client_df,
                device=device
                )
        make_database.create_index(
                tb_name=TB_CLIENT,
                num_data=row)
    else:
        logger.warning("Only index initialization is perfomed, make sure your table is filled up with data.")
        make_database.create_index(
                tb_name=TB_CLIENT,
                num_data=row)

if __name__=="__main__":
    main()


