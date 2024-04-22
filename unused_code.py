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