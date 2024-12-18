# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime
import json
import re
import textwrap
import pandas as pd
from botbuilder.core import (
    ActivityHandler,
    CardFactory,
    ConversationState,
    MemoryStorage,
    MessageFactory,
    TurnContext,
)
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import Activity, ActivityTypes, Attachment, ChannelAccount
from config import DefaultConfig
import datarobotx as drx
from utilities import generate_links

adaptive_card_json = json.load(open("./card_template.json"))

CONFIG = DefaultConfig()
# DataRobot Connect
drx.Context(token=CONFIG.DATAROBOT_TOKEN, endpoint=CONFIG.DATAROBOT_ENDPOINT)
deployment_id = CONFIG.DATAROBOT_DEPLOYMENT
deployment = drx.Deployment(deployment_id)

# store chat history
memstore = MemoryStorage()
convstate = ConversationState(memstore)


class ConversationData:
    def __init__(self, chat_history=[]):
        self.chat_history = chat_history


class MyBot(TeamsActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password
        self.convstate_accessor = convstate.create_property("convdata")

    def format_answer(self,answer):
        """
        Formats the answer to be displayed in a structured and readable way.
        Supports headings, bullet points, and normal text.
        """
        # Initialize the adaptive card JSON structure
        formatted_response = {
            "type": "AdaptiveCard",
            "body": []
        }
        
        # Split the answer by newline to detect sections and bullet points
        sections = answer.split("\n\n")
        
        for line in sections:
            # Check if the line looks like a heading (e.g., "1. INTRODUCTION")
            if re.match(r"^\d+\.\s+[A-Za-z ]+$", line):
                formatted_response["body"].append({
                    "type": "TextBlock",
                    "text": f"**{line.strip()}**",  # Make the heading bold
                    "size": "Medium",
                    "wrap": True
                })
            # Check for bullet points (lines starting with "*")
            elif line.strip().startswith("*"):
                formatted_response["body"].append({
                    "type": "TextBlock",
                    "text": f"{line.strip()}",
                    "wrap": True
                })
            # For normal text, just add as a paragraph
            elif line.strip():
                formatted_response["body"].append({
                    "type": "TextBlock",
                    "text": line.strip(),
                    "wrap": True
                })
        
        # Return the formatted response in the format for Adaptive Cards
        return formatted_response

    async def on_message_activity(self, turn_context: TurnContext):
        time_start = datetime.now()
        convdata = await self.convstate_accessor.get(turn_context, ConversationData)
        chat_history = convdata.chat_history
        TurnContext.remove_recipient_mention(turn_context.activity)
        
        try:
            # Prepare input in the correct format for the model
            print('helooooooooooooooooooo')
            current_time = datetime.now()
            input_data = pd.DataFrame([{"promptText": f"today's date is {current_time}" + turn_context.activity.text}])
            print(input_data)

            # Call the prediction method
            answer = await deployment._predict(X=input_data, batch_mode=False)
            
            # Check if the answer is a dataframe, and if so, format it
            if isinstance(answer, pd.DataFrame):
                answer_text = answer.to_string(index=False)
            else:
                answer_text = answer.get("answer", "No answer available.")
            
            # Format the answer
            formatted_response = self.format_answer(answer_text)

            # Send the formatted message as an Adaptive Card
            message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(formatted_response)],
            )
            print(answer)
            text = answer['prediction'][0]

            # Print the extracted text
            print(text)
            # sections = answer.split("\n\n")
            # for section in sections:
            #     print(section)
            #     print() 
            await turn_context.send_activity(text)

        except Exception as e:
            print(f"Error during prediction: {e}")
            await turn_context.send_activity("An error occurred while processing your request.")

    
    # async def on_message_activity(self, turn_context: TurnContext):
    #     time_start = datetime.now()
    #     convdata = await self.convstate_accessor.get(turn_context, ConversationData)
    #     chat_history = convdata.chat_history
    #     TurnContext.remove_recipient_mention(turn_context.activity)

    #     try:
    #         # Prepare input in the correct format for the model
    #         input_data = pd.DataFrame(
    #             [{"promptText": turn_context.activity.text}]
    #         )

    #         # Call the prediction method
    #         answer = await deployment._predict(X=input_data, batch_mode=False)

    #         # print("Deployment response:", answer)
    #         # answer_formatted = answer.get("answer", answer)
    #         if isinstance(answer, pd.DataFrame):
    #             # Assuming the answer is in the first row of the DataFrame and the column is named 'answer'
    #             # answer_formatted = answer.iloc[0]["answer"] if "answer" in answer.columns else "No answer available."
    #             # answer_formatted = answer.get("answer", answer.to_string(index=False))
    #             # print(answer)
    #             # print(answer.to_string(index=False))  # To print without indices
    #             # wrapper = textwrap.TextWrapper(width=80, expand_tabs=False, replace_whitespace=False)
    #             # formatted_text = wrapper.fill(text=answer.to_string(index=False))

    #             # Print the formatted policy text
    #             # print(formatted_text)
    #             answer_to_format = answer.to_string(index=False)
    #             answer_formatted = answer.get("answer", answer_to_format.splitlines(True))
    #         else:
    #             # If the answer is a dictionary, we handle it as a dictionary
    #             answer_formatted = answer.get("answer", "No answer available.")
    #         references = generate_links(answer.get("references", []))

    #         # Update chat history
    #         chat_history.append((turn_context.activity.text, answer_formatted))

    #         # Build adaptive card response
    #         link_block = []
    #         if references:
    #             link_block.append(
    #                 {"type": "TextBlock", "size": "medium", "text": "References:"}
    #             )
    #             link_block.append(
    #                 {"type": "FactSet", "facts": [{"value": f"[{link}]({link})"} for link in references]}
    #             )
    #         adaptive_card_json["body"] = link_block
    #         message = Activity(
    #             text=answer_formatted,
    #             type=ActivityTypes.message,
    #             attachments=[CardFactory.adaptive_card(adaptive_card_json)],
    #         )
    #         await turn_context.send_activity(message)
    #     except Exception as e:
    #         print(f"Error during prediction: {e}")
    #         await turn_context.send_activity("An error occurred while processing your request.")


    # # async def on_message_activity(self, turn_context: TurnContext):
    # #     time_start = datetime.now()
    # #     convdata = await self.convstate_accessor.get(turn_context, ConversationData)
    # #     chat_history = convdata.chat_history
    # #     TurnContext.remove_recipient_mention(turn_context.activity)
    # #     # answer = await deployment.predict(
    # #     #     {"question": turn_context.activity.text, "chat_history": chat_history}
    # #     # )
    # #     input_data = pd.DataFrame(
    # #         [{"promptText": turn_context.activity.text}]
    # #     )
    # #     # input_data = pd.DataFrame(
    # #     #     [{"question": turn_context.activity.text, "chat_history": json.dumps(chat_history)}]
    # #     # )

    # #     # Call the prediction method with batch_mode=False
    # #     answer = await deployment._predict(X=input_data, batch_mode=False)
    # #     print("deployment response")
    # #     print(answer)
    # #     answer_formatted = answer["answer"]
    # #     references = generate_links(answer["references"])
    # #     print(json.dumps(answer))
    # #     chat_history.append((turn_context.activity.text, answer_formatted))
    # #     time_end = datetime.now()
    # #     link_block = []
    # #     if len(references) > 0:
    # #         link_block.append(
    # #             {"type": "TextBlock", "size": "medium", "text": "References:"}
    # #         )
    # #         fs = {"type": "FactSet", "facts": []}
    # #         for link in references:
    # #             # [Adaptive cards!](https://adaptivecards.io)
    # #             fs["facts"].append({"value": "[" + link + "](" + link + ")"})
    # #         link_block.append(fs)
    # #     adaptive_card_json["body"] = link_block
    # #     message = Activity(
    # #         text=answer_formatted,
    # #         type=ActivityTypes.message,
    # #         attachments=[CardFactory.adaptive_card(adaptive_card_json)],
    # #     )
    # #     await turn_context.send_activity(message)

    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hello!. I am DataRobot's Generative AI Bot, how can I help you?"
                )
