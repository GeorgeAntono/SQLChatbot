import chainlit as cl

from sqlalchemy.exc import SQLAlchemyError
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
    #cb = cl.AsyncLangchainCallbackHandler(stream_final_answer=True)

    # Add the post-prompt to the user's message
    post_prompt = " Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION."
    message_with_post_prompt = message.content + post_prompt



    '''
    Runs agent executor with make_async function of chainlit  and 
    takes as input the message as a String 
       
    '''

    chunks = []

    resp = await cl.make_async(agent_executor.run)(message_with_post_prompt)
    '''async for chunk in agent_executor.astream({"input": resp}):
        chunks.append(chunk)
        print("------")
        # Agent Action
        if "actions" in chunk:
            for action in chunk["actions"]:
                print(f"Calling Tool: `{action.tool}` with input `{action.tool_input}`")
        # Observation
        elif "steps" in chunk:
            for step in chunk["steps"]:
                print(f"Tool Result: `{step.observation}`")
        # Final result
        elif "output" in chunk:
            print(f'Final Output: {chunk["output"]}')
        else:
            raise ValueError()
        print("---")'''


    #final_answers = agent_executor(inputs=message_with_post_prompt,callbacks=[cb])
    #final_answers_list = final_answers
    #print(final_answers_list)
    #await final_answers_list['output'].send()

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

    try:
        # Create the database engine using the URI from Config
        db_uri = cfg.db_uri
        engine = create_engine(db_uri)
        sql_query = csv_data.callback_list[-1]

        # Run the SQL query
        sql = text(sql_query)
        results = engine.execute(sql)

        # Check if the results contain any rows
        if not results.rowcount:
            raise Exception("The SQL query returned an empty result set.")

        # Convert the results to a pandas DataFrame and save to CSV
        df_sql = pd.DataFrame(results, columns=results.keys())  # Provide column names
        df_sql.to_csv(sql_path, index=False)

    except SQLAlchemyError as e:
        # Handle the SQLAlchemy error
        error_message = f"An error occurred while executing the SQL query: {str(e)}"
        await cl.Message(content=error_message).send()
        # Log the error or perform any other necessary actions

    except Exception as e:
        # Handle the custom exception for an empty result set
        error_message = f"The SQL query returned an empty result set: {str(e)}"
        await cl.Message(content=error_message).send()
        # Log the error or perform any other necessary actions

    else:
        # If no exception occurred, proceed with other operations

        # Convert the conversation data to a pandas DataFrame (This is for testing only)
        df = pd.DataFrame(conversation_list)
        df.to_csv(file_path, index=False)

        # Convert the callback list to a pandas DataFrame
        #(Callback list is the list of SQL queries that the user has asked for)
        callback_list = csv_data.callback_list
        df_callback = pd.DataFrame(callback_list)
        df_callback.to_csv(callback_path, index=False)

        return "Successful save!"
