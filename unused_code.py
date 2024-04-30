'''

root = True
async with cl.Step(name="Agent Execution",root=root) as step:
        stream = await client.chat.completions.create(
            messages=[{"role": "user", "content": message_with_post_prompt.content}],
            stream=True,
            model="gpt-3.5",
            temperature=0,
        )


@cl.step(type="llm")
async def gpt3_5(message_history):
    settings = {
        "model": "gpt-3.5-turbo-16k-0613",
        "temperature": 0,
    }

    stream = await cfg.llm.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    current_step = cl.context.current_step

    async for part in stream:
        delta = part.choices[0].delta

        if delta.content:
            # Stream the output of the step
            await current_step.stream_token(delta.content)

'''
'''@cl.step
async def fixed_step(resp):

    return resp
    
'''
#chunks = []
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