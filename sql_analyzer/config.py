import os

from gptcache.embedding import langchain
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv
from sql_analyzer.log_init import logger

from gptcache import Cache
from gptcache.adapter.api import init_similar_cache
from langchain.cache import GPTCache
import hashlib


def get_hashed_name(name):
    return hashlib.sha256(name.encode()).hexdigest()


def init_gptcache(cache_obj: Cache, llm: str):
    hashed_llm = get_hashed_name(llm)
    init_similar_cache(cache_obj=cache_obj, data_dir=f"similar_cache_{hashed_llm}")


load_dotenv()

SNOWFLAKE = "snowflake"
MYSQL = "mysql"
SELECTED_DBS = [SNOWFLAKE, MYSQL]


class SnowflakeConfig:
    snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
    snowflake_user = os.getenv("SNOWFLAKE_USER")
    snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
    snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
    snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")
    snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    snowflake_host = os.getenv("SNOWFLAKE_HOST")


class Config:
    model = "gpt-3.5-turbo-16k-0613"
    # model = 'gpt-4-0613'
    llm = ChatOpenAI(model=model, temperature=0)
    db_uri = os.getenv("DB_CONNECTION_STRING")
    snow_flake_config = SnowflakeConfig()
    selected_db = os.getenv("SELECTED_DB")
    if selected_db not in SELECTED_DBS:
        raise Exception(
            f"Selected DB {selected_db} not recognized. The possible values are: {SELECTED_DBS}."
        )


class Email:
    receiver = os.getenv("EMAIL_RECEIVER")
    sender_address = os.getenv("EMAIL_SENDER_ADDRESS")
    sender_password = os.getenv("EMAIL_SENDER_PASSWORD")


class Csv:
    conversation_data = []
    callback_list = []


cfg = Config()

langchain.llm_cache = GPTCache(init_gptcache)

csv_data = Csv()

mail = Email()

if __name__ == "__main__":
    logger.info("LLM %s", cfg.llm)
    logger.info("db_uri %s", cfg.db_uri)
    logger.info("selected_db %s", cfg.selected_db)
    logger.info("conversation_data %s", csv_data.conversation_data)
