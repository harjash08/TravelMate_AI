from langchain_core.prompts import ChatPromptTemplate
from core.mesh_config import model
from graph.state import TravelState, VerificationDecision
from core.logger import get_logger, track_execution


VERIFICATION_SYSTEM_PROMPT = """
You are TravelMate's response verification agent. Determine whether the generated response satisfies the user's original query.

EVALUATION CRITERIA:
1. Relevance: Does the response answer the original query?
2. Completeness: Does it cover all important user requirements?
3. Accuracy: Is it consistent with worker agent results?
4. Quality: Is it meaningful and understandable?

RULES:
1. Compare the original query against the generated response and worker results.
2. Do not reject responses merely because they are short.
3. Accept appropriate responses to greetings, general questions and conversational queries.
4. Do not expect execution of tasks the user never requested.
5. Set is_valid=True if the response satisfies the request; otherwise, set is_valid=False.
6. When invalid, provide specific feedback identifying missing, incorrect or insufficient information.
7. Feedback must help the orchestrator determine whether additional worker execution or simple response regeneration is required.

Return your decision using the required output schema.
"""


VERIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", VERIFICATION_SYSTEM_PROMPT),
    (
        "human",
        """QUERY: {query}

WORKER RESULTS: {agent_results}

GENERATED RESPONSE: {final_response}

Verify whether the response satisfies the original query."""
    )
])

# VERIFICATION_SYSTEM_PROMPT = """
# You are the response verification agent of TravelMate.

# Your responsibility is to verify whether the generated response
# satisfies the user's original query.

# You must evaluate the response carefully.

# CHECK THE FOLLOWING:

# 1. RELEVANCE:
#    Does the response actually answer the user's original query?

# 2. COMPLETENESS:
#    Does the response address all the important requirements
#    mentioned by the user?

# 3. ACCURACY:
#    Does the response remain consistent with the information
#    provided by the worker agents?

# 4. RESPONSE QUALITY:
#    Is the response meaningful and understandable?

# RULES:

# 1. Compare the original user query with the generated response.

# 2. Do not reject a response merely because it is short.

# 3. For greetings and general conversational questions,
#    accept an appropriate conversational response.

# 4. Do not expect travel agents to execute tasks that
#    the user never requested.

# 5. If the response satisfies the user's request,
#    return is_valid=True.

# 6. If the response fails to satisfy the user's request,
#    return is_valid=False.

# 7. When verification fails, provide specific feedback
#    explaining what is missing or incorrect.

# 8. Your feedback must help the orchestrator decide
#    whether additional worker execution is necessary
#    or whether the response simply needs regeneration.

# Return your decision using the required output schema.
# """


# VERIFICATION_PROMPT = ChatPromptTemplate.from_messages([
#     ("system", VERIFICATION_SYSTEM_PROMPT),
#     (
#         "human",
#         """
#         ORIGINAL USER QUERY:
#         {query}

#         WORKER RESULTS:
#         {agent_results}

#         GENERATED RESPONSE:
#         {final_response}

#         Verify whether the generated response satisfies
#         the original user query.
#         """
#     )
# ])











logger = get_logger(__name__)


verification_llm = model.with_structured_output(
    VerificationDecision
)


@track_execution
async def verification_node(state: TravelState):

    logger.info("Verification started")
    

    prompt = VERIFICATION_PROMPT.invoke({

        "query": state["query"],

        "agent_results": state.get("agent_results", {}),

        "final_response": state.get("final_response", "")
    })

    decision = await verification_llm.ainvoke(prompt)

    retry_count = state.get("retry_count", 0)

    # Successful verification
    if decision.is_valid:
        logger.info(f"VERIFICATION DECISION: {decision.is_valid}")

        logger.info("Response verification successful")

        return {
            "is_valid": True,
            "verification_feedback": ""
        }

    # Failed verification
    retry_count += 1

    logger.warning(
        f"Verification failed. Retry count: {retry_count}"
    )

    return {
        "is_valid": False,
        "verification_feedback": decision.verification_feedback,
        "retry_count": retry_count
    }