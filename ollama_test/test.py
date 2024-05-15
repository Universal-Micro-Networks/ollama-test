import os

import logging
import sys

from sqlalchemy import text
from IPython.display import Markdown, display
from llama_index.core import SQLDatabase, Settings, PromptTemplate
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.llms import ChatResponse
from apigw_analysis_db import get_db_connection
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



def parse_response_to_sql(response: ChatResponse) -> str:
    """Parse response to SQL."""
    response = response.message.content # type: ignore
    sql_query_start = response.find("SQLQuery:") # type: ignore
    if sql_query_start != -1:
        response = response[sql_query_start:] # type: ignore
        # TODO: move to removeprefix after Python 3.9+
        if response.startswith("SQLQuery:"): # type: ignore
            response = response[len("SQLQuery:") :] # type: ignore
    sql_result_start = response.find("SQLResult:") # type: ignore
    if sql_result_start != -1:
        response = response[:sql_result_start] # type: ignore
    return response.strip().strip("```").strip() # type: ignore


# 使用モデルを選択します。
llm = Ollama(model="llama3", request_timeout=120.0)
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
Settings.llm = llm
Settings.embed_model = embed_model

# 使用するデータベースを選択します。
engine = get_db_connection()
sql_database = SQLDatabase(engine, schema="log_analysis")

sql_parser_component = FnComponent(fn=parse_response_to_sql)

text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
    dialect=engine.dialect.name
)
print(text2sql_prompt.template)

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["access_logs"], llm=llm, text_to_sql_prompt=text2sql_prompt
)

query_str = "Which has the largest response_latency?"
response = query_engine.query(query_str)

print(response)
