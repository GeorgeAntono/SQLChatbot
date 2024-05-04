import chainlit as cl

from chainlit.input_widget import Select, Switch, Slider

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine,text
from sql_analyzer.config import cfg



import pandas as pd
import os
from sql_analyzer.config import csv_data

from typing import Dict, Optional


from sql_analyzer.agent_factory import agent_factory
from langchain.agents import AgentExecutor

from sql_analyzer.email import send_email

directory = "../PostNLconsultancy/csv"
file_path = os.path.join(directory, "conversation_data.csv")
conversation_list = csv_data.conversation_data
callback_path = os.path.join(directory, "callback_list.csv")
sql_path = os.path.join(directory, "sql_data.csv")


@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user

@cl.on_chat_start
async def start():
    agent_executor = agent_factory()
    cl.user_session.set("agent", agent_executor)
    cl.user_session.set("counter", 0)
    cl.user_session.set("conversation_dict_saver", {})

    # subject = "Chatbot Customer Request"
    # attach_filename = "Conversation_List"
    # # df = pd.DataFrame(conversation_list)
    # d = {'col1': [1, 2], 'col2': [3, 4]}
    # df = pd.DataFrame(data=d)
    # send_email(subject, attach_filename, df)


    # settings = await cl.ChatSettings(
    #     [
    #         Select(
    #             id="Model",
    #             label="OpenAI - Model",
    #             values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
    #             initial_index=0,
    #         ),
    #         Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
    #         Slider(
    #             id="Temperature",
    #             label="OpenAI - Temperature",
    #             initial=1,
    #             min=0,
    #             max=2,
    #             step=0.1,
    #         ),
    #         Slider(
    #             id="SAI_Steps",
    #             label="Stability AI - Steps",
    #             initial=30,
    #             min=10,
    #             max=150,
    #             step=1,
    #             description="Amount of inference steps performed on image generation.",
    #         ),
    #         Slider(
    #             id="SAI_Cfg_Scale",
    #             label="Stability AI - Cfg_Scale",
    #             initial=7,
    #             min=1,
    #             max=35,
    #             step=0.1,
    #             description="Influences how strongly your generation is guided to match your prompt.",
    #         ),
    #         Slider(
    #             id="SAI_Width",
    #             label="Stability AI - Image Width",
    #             initial=512,
    #             min=256,
    #             max=2048,
    #             step=64,
    #             tooltip="Measured in pixels",
    #         ),
    #         Slider(
    #             id="SAI_Height",
    #             label="Stability AI - Image Height",
    #             initial=512,
    #             min=256,
    #             max=2048,
    #             step=64,
    #             tooltip="Measured in pixels",
    #         ),
    #     ]
    # ).send()

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



    resp = await cl.make_async(agent_executor.run)(message_with_post_prompt)
    final_message = cl.Message(content=resp)
    await final_message.send()

    # Save the last query in sql_query
    sql_query = csv_data.callback_list[-1]

    #Remember every different message with a counter for one session
    counter = cl.user_session.get("counter")
    conversation_dict_saver = cl.user_session.get("conversation_dict_saver")

    counter += 1
    # Save the button call and the results in a dictionary
    conversation_dict_saver[counter] = sql_query

    cl.user_session.set("conversation_dict_saver", conversation_dict_saver)
    cl.user_session.set("counter", counter)




    actions = [
        cl.Action(name="Save button", value=cl.user_session.get("counter"), description="Click me to save!")
    ]

    await cl.Message(content="Save your answers in a csv:", actions=actions).send()

    res = await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="send_email", value="send_email", label="📧 Email to CDA Team"),
            cl.Action(name="cancel", value="cancel", label="❌ Exit"),
        ],
    ).send()

    if res and res.get("value") == "send_email":
        # await cl.Message(
        #     content="Continue!",
        # ).send()
        # try:
        subject = "Chatbot Customer Request"
        attach_filename = "Conversation_List"
        df = pd.DataFrame(conversation_list)
        # d = {'col1': [1, 2], 'col2': [3, 4]}
        # df = pd.DataFrame(data=d)
        send_email(subject, attach_filename, df)
        # except Exception as e:
        #     # Handle the SQLAlchemy error
        #     error_message = f"An error occurred while sending email: {str(e)}"
        #     # Log the error or perform any other necessary actions
        #     await cl.Message(content=error_message).send()




@cl.action_callback("Save button")
async def on_action(action: cl.Action):
    await cl.Message(content=f"Executed {action.name}").send()
    print("The user clicked on the action button!")
    try:

        # Create the database engine using the URI from Config
        db_uri = cfg.db_uri
        engine = create_engine(db_uri)
        # Get the specific button call from conversation_dict_saver
        conversation_dict_saver = cl.user_session.get("conversation_dict_saver")
        counter = int(action.value)
        sql_query = conversation_dict_saver[counter]
        # Run the SQL query
        sql = text(sql_query)
        results = engine.execute(sql)

        # Convert the results to a pandas DataFrame and save to CSV
        df_sql = pd.DataFrame(results, columns=results.keys())  # Provide column names
        df_sql.to_csv(sql_path, index=False)


        # Check if the results contain any rows
        if not results.rowcount:
            raise Exception(f"The SQL query returned an empty result set. ")

    except SQLAlchemyError as e:
        # Handle the SQLAlchemy error
        error_message = f"An error occurred while executing the SQL query: {str(e)}"
        # Log the error or perform any other necessary actions
        await cl.Message(content=error_message).send()


    except Exception as e:
        # Handle the custom exception for an empty result set
        error_message = f"The SQL query returned an empty result set: {str(e)}"
        # Log the error or perform any other necessary actions
        await cl.Message(content=error_message).send()


    # If no exception occurred, proceed with other operations
    else:

        # Convert the conversation data to a pandas DataFrame (This is for testing only)
        df = pd.DataFrame(conversation_list)
        df.to_csv(file_path, index=False)

        # Convert the callback list to a pandas DataFrame
        #(Callback list is the list of SQL queries that the user has asked for)
        callback_list = csv_data.callback_list
        df_callback = pd.DataFrame(callback_list)
        df_callback.to_csv(callback_path, index=False)

    return "Successful save!"

@cl.on_chat_end
def end():
    if (os.path.exists(file_path) and os.path.isfile(file_path)):
        os.remove(file_path)

    if (os.path.exists(callback_path) and os.path.isfile(callback_path)):
        os.remove(callback_path)

    if (os.path.exists(sql_path) and os.path.isfile(sql_path)):
        os.remove(sql_path)

# @cl.on_settings_update
# async def setup_agent(settings):
#     print("on_settings_update", settings)


