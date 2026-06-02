from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import httpx
import json
from enum import Enum
import uuid
from datetime import datetime
import logging
from notion_client import Client
from supabase_service import get_supabase_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Prompt Engineering Studio API",
    description="Backend API for Prompt Studio - A Notion-based prompt engineering workspace",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your Notion domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Notion client initialization
notion = Client(auth=NOTION_API_KEY) if NOTION_API_KEY else None

# Database IDs (from user configuration)
NOTION_DATABASE_IDS = {
    "prompts": "36d3431ec8e680169aa5f78ff6c7e1e6",  # Corrected: from URL p/ parameter
    "prompt_versions": "36e3431ec8e68045a413fc20efd7a4c8",  # Corrected: from URL p/ parameter
    "evaluations": "36e3431ec8e6808cb129f5c60b0a56b9",  # Corrected: from URL p/ parameter
    "prompt_templates": "36e3431ec8e680009298ea5aff019272"  # Corrected: from URL p/ parameter
}

# Validate required environment variables
required_vars = ["NOTION_API_KEY", "DEEPSEEK_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.warning(f"Missing environment variables: {missing_vars}")

# Models
class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"
    # OPENAI = "openai"
    # CLAUDE = "claude"

class PromptOptimizationRequest(BaseModel):
    original_prompt: str = Field(..., description="The original prompt to optimize")
    provider: ModelProvider = Field(ModelProvider.DEEPSEEK, description="AI provider to use")

class PromptOptimizationResponse(BaseModel):
    diagnosis: str = Field(..., description="Analysis of issues in the original prompt")
    optimized_versions: List[str] = Field(..., description="Three optimized versions of the prompt")
    score_before: float = Field(..., ge=0, le=10, description="Estimated quality score before optimization")
    score_after: float = Field(..., ge=0, le=10, description="Estimated quality score after optimization")

class PromptEvaluationRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to evaluate")
    test_cases: List[str] = Field(..., description="Test cases (input examples)")
    provider: ModelProvider = Field(ModelProvider.DEEPSEEK, description="AI provider to use for evaluation")

class TestCaseResult(BaseModel):
    test_case: str = Field(..., description="The test case input")
    output: str = Field(..., description="AI generated output")
    scores: Dict[str, float] = Field(..., description="Scores for each dimension")

class PromptEvaluationResponse(BaseModel):
    prompt: str = Field(..., description="The evaluated prompt")
    average_scores: Dict[str, float] = Field(..., description="Average scores across all test cases")
    test_case_results: List[TestCaseResult] = Field(..., description="Detailed results for each test case")
    overall_score: float = Field(..., ge=0, le=10, description="Overall quality score")

class ActivationRequest(BaseModel):
    activation_code: str = Field(..., description="Activation code from purchase")
    notion_page_id: str = Field(..., description="Notion page ID where the template is installed")

class ActivationResponse(BaseModel):
    success: bool = Field(..., description="Whether activation was successful")
    message: str = Field(..., description="Activation result message")
    api_url: str = Field(..., description="API base URL for future calls")

# Dependency for activation code validation
async def verify_activation(activation_code: str = Header(..., alias="X-Activation-Code")):
    """
    Validate activation code for protected endpoints.
    This is used by /optimize and /evaluate endpoints.
    """
    if not activation_code:
        raise HTTPException(status_code=401, detail="Activation code required")
    
    try:
        # Validate against Supabase
        supabase = get_supabase_service()
        validation = supabase.validate_activation_code(activation_code)
        
        if not validation.get("valid"):
            logger.warning(f"Invalid activation code in header: {activation_code[:8]}... - {validation.get('message')}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid activation code: {validation.get('message')}"
            )
        
        # Check if code is already used (should be used by now)
        record = validation.get("record", {})
        if record.get("status") != "used":
            logger.warning(f"Activation code not marked as used: {activation_code[:8]}...")
            # Still allow access, but log warning
        
        logger.debug(f"Valid activation code: {activation_code[:8]}...")
        return activation_code
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error validating activation code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating activation code: {str(e)}"
        )

# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "AI Prompt Engineering Studio API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "optimize": "/optimize",
            "evaluate": "/evaluate",
            "activate": "/activate"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "notion_api": "configured" if NOTION_API_KEY else "missing",
            "deepseek_api": "configured" if DEEPSEEK_API_KEY else "missing",
            "supabase": "configured" if SUPABASE_URL and SUPABASE_KEY else "missing"
        }
    }

# Activation endpoint
@app.post("/activate", response_model=ActivationResponse)
async def activate(request: ActivationRequest):
    """
    Activate a purchased copy of Prompt Studio.
    Validates the activation code and links it to a Notion page.
    """
    logger.info(f"Activation requested for code: {request.activation_code[:8]}..., page: {request.notion_page_id}")
    
    try:
        # Get Supabase service
        supabase = get_supabase_service()
        
        # 1. Validate activation code
        validation = supabase.validate_activation_code(request.activation_code)
        
        if not validation.get("valid"):
            logger.warning(f"Invalid activation code: {request.activation_code[:8]}... - {validation.get('message')}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid activation code: {validation.get('message')}"
            )
        
        # 2. Mark code as used with notion_page_id
        mark_result = supabase.mark_activation_code_used(
            code=request.activation_code,
            notion_page_id=request.notion_page_id
        )
        
        if not mark_result.get("success"):
            logger.error(f"Failed to mark activation code as used: {mark_result.get('message')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to activate license: {mark_result.get('message')}"
            )
        
        logger.info(f"Activation successful for code: {request.activation_code[:8]}...")
        
        return ActivationResponse(
            success=True,
            message="Activation successful. Your Prompt Studio is now ready to use.",
            api_url=API_BASE_URL
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during activation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during activation: {str(e)}"
        )

# Prompt optimization endpoint
@app.post("/optimize", response_model=PromptOptimizationResponse)
async def optimize_prompt(
    request: PromptOptimizationRequest,
    activation_code: str = Depends(verify_activation)
):
    """
    Analyze a prompt and provide optimization suggestions.
    """
    logger.info(f"Optimization requested for prompt: {request.original_prompt[:50]}...")
    
    # System prompt for optimization
    system_prompt = """你是一位世界级的提示词工程专家。
你的任务是分析用户提供的Prompt，并给出优化建议。

诊断维度：
1. 角色设定是否清晰
2. 任务描述是否具体
3. 输出格式是否明确
4. 是否包含示例（Few-shot）
5. 是否有约束条件

输出格式（JSON）：
{
    "diagnosis": "逐条分析问题，每条用短句描述",
    "optimized_versions": ["优化版1（完整Prompt）", "优化版2（完整Prompt）", "优化版3（完整Prompt）"],
    "score_before": 6.5,
    "score_after": 8.8
}

请确保优化后的Prompt是完整的、可直接使用的。"""
    
    user_prompt = f"请分析并优化以下Prompt：\n\n{request.original_prompt}"
    
    try:
        # Call DeepSeek API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="AI service temporarily unavailable")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            # The response should be a JSON string
            try:
                # Extract JSON if there's any extra text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                optimization_result = json.loads(content)
                
                return PromptOptimizationResponse(
                    diagnosis=optimization_result.get("diagnosis", "分析完成"),
                    optimized_versions=optimization_result.get("optimized_versions", []),
                    score_before=optimization_result.get("score_before", 6.0),
                    score_after=optimization_result.get("score_after", 8.0)
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON: {content[:200]}")
                # Fallback response
                return PromptOptimizationResponse(
                    diagnosis="AI返回格式异常，已记录错误。",
                    optimized_versions=[
                        f"优化版1（请检查原始Prompt的清晰度）:\n{request.original_prompt}",
                        f"优化版2（尝试添加角色设定）:\n作为一名专家，请完成以下任务：{request.original_prompt}",
                        f"优化版3（尝试明确输出格式）:\n{request.original_prompt}\n\n请以JSON格式输出结果。"
                    ],
                    score_before=5.0,
                    score_after=7.0
                )
                
    except Exception as e:
        logger.exception(f"Error in optimize_prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Prompt evaluation endpoint
@app.post("/evaluate", response_model=PromptEvaluationResponse)
async def evaluate_prompt(
    request: PromptEvaluationRequest,
    activation_code: str = Depends(verify_activation)
):
    """
    Evaluate a prompt against test cases and provide scores.
    """
    logger.info(f"Evaluation requested for prompt with {len(request.test_cases)} test cases")
    
    # Evaluation system prompt
    evaluation_prompt = """请对以下AI输出质量进行评分（1-10分），评分维度：
1. 清晰度：是否易于理解
2. 完整性：是否覆盖了用户需求
3. 可执行性：是否可以直接使用

仅返回JSON：{"clarity": 8, "completeness": 7, "actionability": 9, "overall": 8.0}"""
    
    test_case_results = []
    total_scores = {"clarity": 0, "completeness": 0, "actionability": 0, "overall": 0}
    
    try:
        for test_case in request.test_cases:
            # Generate output for this test case
            async with httpx.AsyncClient() as client:
                # First, get the AI's output for the test case
                output_response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": request.prompt},
                            {"role": "user", "content": test_case}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if output_response.status_code != 200:
                    logger.error(f"DeepSeek API error in evaluation: {output_response.status_code}")
                    continue
                
                output_result = output_response.json()
                output = output_result["choices"][0]["message"]["content"]
                
                # Now evaluate the output
                eval_response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": evaluation_prompt},
                            {"role": "user", "content": f"AI输出：\n{output}"}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 200
                    },
                    timeout=30.0
                )
                
                if eval_response.status_code != 200:
                    logger.error(f"DeepSeek API evaluation error: {eval_response.status_code}")
                    scores = {"clarity": 5.0, "completeness": 5.0, "actionability": 5.0, "overall": 5.0}
                else:
                    eval_result = eval_response.json()
                    eval_content = eval_result["choices"][0]["message"]["content"]
                    
                    try:
                        # Extract JSON
                        import re
                        json_match = re.search(r'\{.*\}', eval_content, re.DOTALL)
                        if json_match:
                            eval_content = json_match.group(0)
                        
                        scores = json.loads(eval_content)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse evaluation scores: {eval_content[:200]}")
                        scores = {"clarity": 5.0, "completeness": 5.0, "actionability": 5.0, "overall": 5.0}
                
                # Add to results
                test_case_results.append(TestCaseResult(
                    test_case=test_case,
                    output=output[:500] + "..." if len(output) > 500 else output,
                    scores=scores
                ))
                
                # Accumulate scores
                for key in total_scores:
                    if key in scores:
                        total_scores[key] += scores[key]
    
    except Exception as e:
        logger.exception(f"Error in evaluate_prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
    
    # Calculate averages
    num_cases = len(test_case_results)
    if num_cases > 0:
        average_scores = {key: total_scores[key] / num_cases for key in total_scores}
    else:
        average_scores = {key: 0.0 for key in total_scores}
    
    return PromptEvaluationResponse(
        prompt=request.prompt,
        average_scores=average_scores,
        test_case_results=test_case_results,
        overall_score=average_scores.get("overall", 0.0)
    )

# Notion integration endpoints (to be implemented)
@app.post("/notion/create-prompt")
async def create_prompt_in_notion(title: str, content: str, category: str = "uncategorized"):
    """Create a new prompt record in Notion"""
    if not notion:
        raise HTTPException(status_code=500, detail="Notion client not configured")
    
    try:
        database_id = NOTION_DATABASE_IDS["prompts"]
        
        # Create page in the database
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Content": {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                },
                "Category": {
                    "select": {
                        "name": category
                    }
                }
            }
        )
        
        return {
            "success": True,
            "message": "Prompt created successfully",
            "page_id": new_page.get("id"),
            "url": new_page.get("url")
        }
    
    except Exception as e:
        logger.exception(f"Error creating Notion page: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create prompt: {str(e)}")

@app.get("/notion/prompts")
async def get_prompts_from_notion():
    """Retrieve prompts from Notion database"""
    if not notion:
        raise HTTPException(status_code=500, detail="Notion client not configured")
    
    try:
        # Query the prompts database
        database_id = NOTION_DATABASE_IDS["prompts"]
        response = notion.databases.query(database_id=database_id)
        
        # Extract relevant data from each page
        prompts = []
        for page in response.get("results", []):
            # Extract properties (adjust based on your database schema)
            properties = page.get("properties", {})
            
            # Try to get title and content
            title = "Untitled"
            content = ""
            
            # Check for Title property (could be "Name", "Prompt Name", etc.)
            for prop_name, prop_value in properties.items():
                if prop_value.get("type") == "title" and prop_value.get("title"):
                    title = prop_value["title"][0].get("plain_text", "Untitled")
                elif prop_name.lower() in ["content", "prompt", "text"]:
                    # Handle different property types
                    if prop_value.get("type") == "rich_text" and prop_value.get("rich_text"):
                        content = prop_value["rich_text"][0].get("plain_text", "")
                    elif prop_value.get("type") == "text" and prop_value.get("text"):
                        content = prop_value["text"][0].get("plain_text", "")
            
            prompts.append({
                "id": page.get("id"),
                "title": title,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time")
            })
        
        return {
            "database_id": database_id,
            "total": len(prompts),
            "prompts": prompts
        }
    
    except Exception as e:
        logger.exception(f"Error querying Notion database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query Notion: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)