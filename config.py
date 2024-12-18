#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = os.environ.get("PORT", 3978)  # Port to run the bot service on
    SERVER = os.environ.get("SERVER", "localhost")  # Server IP. Accepts localhost
    APP_ID = os.environ.get(
        "MicrosoftAppId", "bcf17d5e-1f5d-426a-918b-447d2eb766cf"
        # "d2b8976e-5ec9-4ea2-933f-edfd05c2150f"
    )  # Bot Identifier from https://dev.teams.microsoft.com/bots/2d3fb680-8234-4e59-95db-3339824a2d76/configure
    APP_PASSWORD = os.environ.get(
        "MicrosoftAppPassword", "y3I8Q~G1P963WGoKFJFif~RlyrSvV1C-BbmBAbOP"
        # "qEq8Q~fsmmz9~JLqS~OjGutxhEd41ms5MPvTyduN"
    )  # Client Secret from Bot Configure page.
    DATAROBOT_TOKEN = os.environ.get(
        "apiToken", "Njc2MTMxOWYzMTk1ZmFiMGFiNmI2NjM5OmUxS0JXVEdvYUlnRGtuR3JlMUtXQlBDQWMvZy9mVW8yWk93RStEbm5wS2M9"
    )  # DataRobot API Token for authorization
    DATAROBOT_ENDPOINT = os.environ.get(
        "DATAROBOT_ENDPOINT", "https://app.datarobot.com/api/v2"
    )  # DataRobot Endpoint
    DATAROBOT_DEPLOYMENT = os.environ.get(
        "deploymentId", "676130916ee556117457cdff"
        # 674d755bbe1497c3149eb168
    )  # DataRobot LLM Deployment Identifier
