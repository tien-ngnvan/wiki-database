import os
import logging
import torch

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
TB_WIKI=os.getenv("TB_WIKI", "wiki_tb")
TB_CLIENT=os.getenv("TB_CLIENT", "client_tb")
BATCH=int(os.getenv("BATCH", 16))

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

def main():
    arguments = Arguments()
    args = arguments.parse()
    row = 17553713 if args.dataset_version == "wiki40b_en_100_0" else 33849898
    if not args.just_create_index:
        if args.init_db and not args.init_tb:
            make_database.create_postgres_db()
            make_database.create_wiki_table()
        elif args.init_tb and not args.init_db:
            make_database.create_wiki_table()
        elif not args.init_tb and not args.init_db:
            logger.warning("Make sure your database and table exist")
        else:
            ValueError("Database and table are created at the same time, or just a table is created")

        encoder_model, model_tokenizer = retriever_model.load_dpr_context_encoder(
                model_name_or_path="vblagoje/dpr-ctx_encoder-single-lfqa-wiki"
                )
        if torch.cuda.is_available(): 
            device = torch.device(f"cuda:{args.gpu_index}")
        else: 
            device = torch.device("cpu")
        
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Start downloading dataset")
        encoder_model.to(device)
        encoder_model.eval()
        wiki_snippets = make_data.download_dataset(
                dataset_name=args.dataset_name,
                dataset_version = args.dataset_version,
                streaming=args.streaming
                )

        print("Start inserting knowledges")
        make_database.insert_knowledges(
                context_encoder=encoder_model,
                context_tokenizer=model_tokenizer,
                snippets=wiki_snippets,
                device=device
                )
        make_database.create_index(
                tb_name=TB_WIKI,
                num_data=row)
    else:
        logger.warning("Only index initialization is perfomed, make sure your table is filled up with data.")
        make_database.create_index(
                tb_name=TB_WIKI,
                num_data=row)

if __name__=="__main__":
    main()


