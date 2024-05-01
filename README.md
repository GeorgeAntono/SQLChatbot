# SQL Chain Playground

This project is a chatbot user interface which allows users to query a specific database using natural language.
It allows you to query in a technical, but also in a business like way.

So you can ask questions like e.g:

- Can you please show me all the indices used in this database?
- Which are the 5 most popular X ?
- Which tables are referencing the X table?

## Installation


Do the installation preferably on PyCharm or any other terminal than conda. If you use conda here is the commands. 
```
# conda remove -n langchain_sql --all
conda create -n langchain_sql python=3.11
conda activate langchain_sql
pip install langchain
pip install prompt_toolkit
pip install openai
pip install mysqlclient
pip install chainlit
pip install geoalchemy2
pip install gptcache
# Support MySQL geometry types
pip install acryl-datahub
pip install black



pip install poetry
poetry install

```

If you use Pycharm or VsCode or any other IDE or text editor, git clone this repository 
and then run the following commands on the terminal of the cloned repository.


```
pip install langchain
pip install prompt_toolkit
pip install openai
pip install mysqlclient
pip install chainlit
pip install geoalchemy2
pip install gptcache
# Support MySQL geometry types
pip install acryl-datahub
pip install black


pip install poetry
poetry install

```


### Snowflake

```
# conda activate base
# conda remove -n langchain_snowflake --all
conda create -n langchain_snowflake python=3.11
conda activate langchain_snowflake
pip install langchain
pip install snowflake-sqlalchemy
# pip install SQLAlchemy-Utils
pip install openai
pip install gptcache
pip install chainlit
# pip install black

# pip install poetry
# poetry install
```


To install as a package, please use (check if it works, it might not install, pip install mysqlclient):

```bash
pip install -e .
```

This might be useful under Ubuntu
```
sudo apt install pkg-config
```

## Run Chainlit

For development:
```
chainlit run ./sql_analyzer/mysql_analyzer_chainlit.py --port 8084 -w
```

Normally:
```
chainlit run ./sql_analyzer/mysql_analyzer_chainlit.py --port 8084
```

## Notes on the Sakila DB

We have used for testing the Sakila database. However it seems that the SQLAlchemy package does not like the "geometry" data type and so
we more some data to a varchar datatype with these commands:

```SQL
alter table address add column point_location varchar(256);
update address set point_location = ST_AsText(location);
alter table address drop column location;
```

## Notes on .env file

You will also need a `.env` file in the directory you are running this application as well as an installed MySQL database server with the Sakila database installed.


The .env file should have the following variables:

```
DB_CONNECTION_STRING=mysql+mysqldb://<user>:<password>@localhost/sakila
OPENAI_API_KEY=<openapi-key>

# Snowflake
SNOWFLAKE_ACCOUNT=****
SNOWFLAKE_USER=****
SNOWFLAKE_PASSWORD=****
SNOWFLAKE_DATABASE=SNOWFLAKE_SAMPLE_DATA
SNOWFLAKE_SCHEMA=TPCDS_SF10TCL
SNOWFLAKE_WAREHOUSE=DEMO_WH
SNOWFLAKE_HOST=****

SELECTED_DB=snowflake # snowflake or mysql
```

Sakila is a test database used by SQL. You can create a custom table like PostNL and reference it with
``` 
DB_CONNECTION_STRING=mysql+mysqldb://<user>:<password>@localhost/PostNL
```

To add Data Persistency, we need authentication and the Literal API key. 

Here you will find how to create the literal API key: https://docs.chainlit.io/data-persistence/overview

Here you will find how to create the github credentials: https://docs.chainlit.io/authentication/oauth


To get the CHAINLIT_AUTH_SECRET you need to run the following command on the terminal.
``` 
chainlit create-secret
```

This how the .env should look like eventually. 

```
DB_CONNECTION_STRING=mysql+mysqldb://<user>:<password>@localhost/PostNL
OPENAI_API_KEY=<openapi-key>
SELECTED_DB=mysql
CHAINLIT_AUTH_SECRET="YOUR_CHAINLIT_SECRET_KEY"
OAUTH_GITHUB_CLIENT_ID=your_github_client_id
OAUTH_GITHUB_CLIENT_SECRET=your_github_secret_token
LITERAL_API_KEY=your_literal_API_key
```
