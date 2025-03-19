# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# comment
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google import genai
from google.genai.types import (
    Tool,
    Content,
    LiveConnectConfig,
    FunctionDeclaration,
)

from app.client import genai_client
from app.tools.fact_check import fact_check
from app.tools.retriver import retrieve_docs
from app.templates import SYSTEM_INSTRUCTION

MODEL_ID = "gemini-2.0-flash-001"


tool_functions = {"retrieve_docs": retrieve_docs, "fact_check": fact_check}

tool_declarations = Tool(
    function_declarations=[
        FunctionDeclaration.from_callable(client=genai_client, callable=retrieve_docs),
        FunctionDeclaration.from_callable(client=genai_client, callable=fact_check)
    ]
)
 
live_connect_config = LiveConnectConfig(
    response_modalities=["AUDIO"],
    tools=[tool_declarations],
    system_instruction=Content(parts=[{"text": SYSTEM_INSTRUCTION}]),
)
