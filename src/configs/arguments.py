import argparse
import logging

logger = logging.getLogger(__name__)

class Arguments:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                conflict_handler="resolve"
                )
        self.init_environment()

    def init_environment(self) -> None:
        """Provide environment variables
        """
        self.parser.add_argument(
            "--dbname",
            type=str,
            help="name of database to connect",
            required=True,
        )
        self.parser.add_argument(
            "--host",
            type=str,
            help="host of database to connect",
            required=True,
        )
        self.parser.add_argument(
            "--port",
            type=str,
            help="port of database to connect",
            required=True,
        )
        self.parser.add_argument(
            "--user",
            type=str,
            help="user name to log in to database",
            required=True,
        )
        self.parser.add_argument(
            "--pwd",
            type=str,
            help="password to log in to database",
            required=True,
        )
        self.parser.add_argument(
            "--tbname",
            type=str,
            help="name of table in the database",
            required=True,
        )

    def parse(self):
        """Get arguments
        """
        args = self.parser.parse_args()
        return args
