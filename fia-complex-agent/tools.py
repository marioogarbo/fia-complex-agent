import os
from typing import Dict, Any
from vertexai.preview import rag
from httpx import AsyncClient

# Configuration variables
CORPUS_NAME = f"fia-role-based-learning-pathways"
RAG_CORPUS = f"projects/buoyant-purpose-475203-t9/locations/us-east4/ragCorpora/4611686018427387904"
DEFAULT_TOP_K = 10
DEFAULT_VECTOR_DISTANCE_THRESHOLD = 0.6


async def send_zoho_email(path_variables: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send email via Zoho Mail MCP server with proper enum handling.
    
    Args:
        path_variables: Object containing accountId (required)
        body: Email details with fromAddress and toAddress (required)
    """
    mcp_url = os.getenv("TESTUSER1_ZOHO_MCP", "https://course-advisor-agent-project-902810301.zohomcp.com/mcp/message?key=3f0cf7a431fdc96a5a24bb002a7d4897")
    timeout = 60
    
    try:
        # Convert scheduleType back to integer if provided as string (fix for schema issue)
        if "scheduleType" in body:
            try:
                body["scheduleType"] = int(body["scheduleType"])
            except (ValueError, TypeError):
                pass
        
        # Make HTTP request to MCP server
        async with AsyncClient(timeout=timeout) as client:
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "ZohoMail_sendEmail",
                        "arguments": {
                            "path_variables": path_variables,
                            "body": body
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    return {"error": result["error"]}
                else:
                    return {"error": "Unexpected response format"}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
    except Exception as e:
        return {"error": f"Failed to call MCP server: {str(e)}"}

def rag_query(query: str) -> Dict[str, Any]:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.

    Args:
        query (str): The text query to search for in the corpus

    Returns:
        dict: The query results and status
    """
    try:
        # Perform the query
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=RAG_CORPUS
                )
            ],
            text=query,
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=DEFAULT_TOP_K,
                filter=rag.Filter(vector_distance_threshold=DEFAULT_VECTOR_DISTANCE_THRESHOLD),
            ),
        )

        # Process the response into a more usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)

        # If we didn't find any results
        if not results:
            return {
                "status": "warning",
                "message": f"No results found in corpus '{CORPUS_NAME}' for query: '{query}'",
                "query": query,
                "corpus_name": CORPUS_NAME,
                "results": [],
                "results_count": 0,
            }

        return {
            "status": "success",
            "message": f"Successfully queried corpus '{CORPUS_NAME}'",
            "query": query,
            "corpus_name": CORPUS_NAME,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"Error querying corpus: {str(e)}"
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "corpus_name": CORPUS_NAME,
        }