import chainlit as cl

from sqlalchemy import create_engine,text
from sql_analyzer.config import cfg


import pandas as pd
import os
from sql_analyzer.config import csv_data

from sql_analyzer.agent_factory import agent_factory
from langchain.agents import AgentExecutor

directory = "../PostNLconsultancy/csv"
file_path = os.path.join(directory, "conversation_data.csv")
conversation_list = csv_data.conversation_data
callback_path =  os.path.join(directory, "callback_list.csv")
sql_path = os.path.join(directory, "sql_data.csv")




@cl.on_chat_start
def start():
    agent_executor = agent_factory()
    cl.user_session.set("agent", agent_executor)



@cl.on_message
async def main(message):
    # Sending an action button within a chatbot message


    agent_executor: AgentExecutor = cl.user_session.get("agent")
    cb = cl.LangchainCallbackHandler(stream_final_answer=True)

    # Add the post-prompt to the user's message
    post_prompt = " Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION."
    message_with_post_prompt = message + post_prompt

    
    resp = await cl.make_async(agent_executor.run)(message_with_post_prompt, callbacks=[cb])
    final_message = cl.Message(content=resp)
    await final_message.send()

    actions = [
        cl.Action(name="Save button", value="save_csv", description="Click me to save!")
    ]

    await cl.Message(content="Save your answers in a csv:", actions=actions).send()


@cl.action_callback("Save button")
async def on_action(action: cl.Action):
    await cl.Message(content=f"Executed {action.name}").send()
    print("The user clicked on the action button!")

    # Save the data with SQL_QUERY to a csv file

    # Create the database engine using the URI from Config
    db_uri = cfg.db_uri
    engine = create_engine(db_uri)
    sql_query = csv_data.callback_list[-1]
    # Run the SQL query
    sql = text(sql_query)
    results = engine.execute(sql)

    # Convert the results to a pandas DataFrame and save to CSV
    df_sql = pd.DataFrame(results, columns=results.keys())  # Provide column names
    df_sql.to_csv(sql_path, index=False)


    # Convert the conversation data to a pandas DataFrame (This is for testing only)
    df = pd.DataFrame(conversation_list)
    df.to_csv(file_path, index=False)

    # Convert the callback list to a pandas DataFrame
    #(Callback list is the list of SQL queries that the user has asked for)
    callback_list = csv_data.callback_list
    df_callback = pd.DataFrame(callback_list)
    df_callback.to_csv(callback_path, index=False)


    return "Thank you for clicking on the action button!"