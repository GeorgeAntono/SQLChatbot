import chainlit as cl

from chainlit.input_widget import Select, Switch, Slider

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine,text
from sql_analyzer.config import cfg
from literalai import LiteralClient


import pandas as pd
import os
from sql_analyzer.config import csv_data

from typing import Dict, Optional


from sql_analyzer.agent_factory import agent_factory
from langchain.agents import AgentExecutor
from sql_analyzer.email import email_to_analyst,email_to_user, validate_email


directory = "../PostNLconsultancy/csv"
file_path = os.path.join(directory, "conversation_data.csv")
conversation_list = csv_data.conversation_data
callback_path = os.path.join(directory, "callback_list.csv")
sql_path = os.path.join(directory, "sql_data.csv")
#conversation_dict_saver = {}
literal_client = LiteralClient(api_key=os.getenv("LITERAL_API_KEY"))

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

@cl.on_message
async def main(message):
    literal_client.reset_context()
    # Sending an action button within a chatbot message
    name_of_message = message.content.strip()
    with literal_client.thread(name=name_of_message) as thread:
        agent_executor: AgentExecutor = cl.user_session.get("agent")
        literal_client.message(content=message.content, type="user_message", name="User")
        # Add the post-prompt to the user's message
        post_prompt = " Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION."
        message_with_post_prompt = message.content + post_prompt



        '''
        Runs agent executor with make_async function of chainlit  and 
        takes as input the message as a String 
           
        '''



        resp = await cl.make_async(agent_executor.run)(message_with_post_prompt)
        # Splitting the response to remove the final answer part
        if "Final Answer:" in resp:
            answer_part = resp.split("Final Answer:")[0].strip()
        else:
            answer_part = resp
        final_message = cl.Message(content="This is an example answer: " + answer_part)
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
        # Log the response as an assistant message
        literal_ai_log=conversation_list
        literal_ai_log.append(sql_query)
        narrative = []
        for item in literal_ai_log:
            try:
                # Check if 'Action' key exists and handle it
                if "Action" in item:
                    action_title = item['Action'].replace('_', ' ').title()
                    first_part_of_text = item.get('Text', '').split('\n')[0]
                    narrative.append(f"**{action_title}**: {first_part_of_text}")

                # Check if 'Answer' key exists and handle it
                if "Answer" in item:
                    answer_text = f"**Query Result**: The answer is {item['Answer']}."
                    narrative.append(answer_text)

            except Exception as e:
                print(f"Error processing item in narrative: {str(e)}")

        answer_text = f"**SQL Query**: The sql query is {sql_query}."
        narrative.append(answer_text)
        narrative_text = "\n- ".join(narrative)
        thread.tags = ["SQL_Query","To review"]
        literal_client.message(content=narrative_text, type="assistant_message", name="Agent Response")



        actions = [
            cl.Action(name="Save", value=cl.user_session.get("counter"), description="Click me to save!")
        ]

        await cl.Message(content="Save your answers in a csv:", actions=actions).send()

    res = await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="confirm", value="confirm", label="✅ Confirm the result"),
            cl.Action(name="continue", value="continue", label="➡️ Resume the conversation"),
            cl.Action(name="send_email", value="send_email", label="📧 Email to CDA Team"),
            #cl.Action(name="cancel", value="cancel", label="❌ Exit"),
        ],
    ).send()

    # When the user confirm the result, finish the conversation and email the user the result data from real DB.
    if res and res.get("value") == "confirm":
        # ask user to input email address
        require_email_address = True
        while require_email_address:
            res1 = await cl.AskUserMessage(
                content="Please provide your email address to receive the data.", timeout=600).send()
            if res1:
                user_email_address = res1['output']
                if validate_email(user_email_address):
                    await cl.Message(
                        content=f"We have recorded your email address: {user_email_address}",
                    ).send()
                    require_email_address = False
                else:
                    await cl.Message(
                        content=f"The email address \"{user_email_address}\" is invalid.",
                    ).send()
                    continue
                # ask user to write his/her name
                res2 = await cl.AskUserMessage(
                    content="Please provide your name.", timeout=600).send()
                if res2:
                    user_name = res2['output']
                    # send the email
                    # here's the example for test
                    df = pd.DataFrame(conversation_list)
                    email_to_user(user_email_address, user_name, df)
                    await cl.Message(content="Thank you! The data will be sent to your email address.").send()
    elif res and res.get("value") == "send_email":
        # ask user to input email address
        require_email_address = True
        while require_email_address:
            res1 = await cl.AskUserMessage(content="Please provide your email address to receive the feedback from CDA Team.", timeout= 600).send()
            if res1:
                user_email_address = res1['output']
                if validate_email(user_email_address):
                    await cl.Message(
                        content=f"We have recorded your email address: {user_email_address}",
                    ).send()
                    require_email_address = False
                else:
                    await cl.Message(
                        content=f"The email address \"{user_email_address}\" is invalid.",
                    ).send()
                    continue
                # ask user to write message to the CDA Team
                res2 = await cl.AskUserMessage(
                    content="Please write down your message to the CDA Team.", timeout=600).send()
                if res2:
                    user_message = res2['output']
                    # send the email
                    df = pd.DataFrame(conversation_list)
                    re = email_to_analyst(user_email_address, user_message, df)
                    if re:
                        await cl.Message(content="The email is successfully sent to the CDA Team.").send()
                    else:
                        await cl.Message(content="Email sending failed.").send()
    else:
        pass




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

