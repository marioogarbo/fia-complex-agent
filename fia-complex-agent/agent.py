import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from .tools import send_zoho_email, rag_query
from .prompts import (
    STUDENT_SUPPORT_AGENT_INSTRUCTION,
    COURSE_ADVISOR_AGENT_INSTRUCTION,
    ORCHESTRATOR_AGENT_INSTRUCTION,
)

# Load environment variables
load_dotenv(override=True)

# FIA Student Coordinator - Multi-Agent System
# 1. Student Support Agent - Handles student queries and support requests
student_support_agent = Agent(
    name="student_support_agent",
    model="gemini-2.0-flash-exp",
    description="Handles student enrollment queries, course status checks, and administrative support for FIA learners",
    instruction=STUDENT_SUPPORT_AGENT_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("FIA_AXCELERATE_MCP", 'https://fia-axcelerate-mcp-905053609184.us-central1.run.app/mcp')
            )
        )
    ]
)

# 2. Course Advisor Agent - Recommends courses based on student profile
course_advisor_agent = Agent(
    name="course_advisor_agent",
    model="gemini-2.5-flash",
    description="An agent that advises prospective learners on suitable FIA (Fire Industry Academy) courses based on their job role, fire protection system interests, location, experience, and prior learning.",
    instruction=COURSE_ADVISOR_AGENT_INSTRUCTION,
    tools=[rag_query, send_zoho_email]
)

# 3. FIA Orchestrator Agent - Coordinates Student Support and Course Advisor
fia_orchestrator_agent = Agent(
    name="fia_orchestrator_agent",
    model="gemini-2.0-flash-exp",
    description="Intelligent orchestrator for FIA Student Coordinator system, routing queries and coordinating workflows between specialized agents",
    instruction=ORCHESTRATOR_AGENT_INSTRUCTION,
    sub_agents=[
        student_support_agent,
        course_advisor_agent,
    ],
)

# Set the root agent
root_agent = fia_orchestrator_agent