import os
from openai import OpenAI
from prompts.analysis_prompt import ANALYSIS_PROMPT


def get_client():
    """Create and return an OpenAI-compatible client."""
    api_key = os.environ.get('OPENAI_API_KEY', '')
    base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    return OpenAI(api_key=api_key, base_url=base_url)


def analyze_document(document_content: str) -> str:
    """
    Send document content to LLM and get structured three-section analysis.

    Args:
        document_content: The text content of the court ruling draft.

    Returns:
        Markdown-formatted analysis string.
    """
    client = get_client()
    model = os.environ.get('OPENAI_MODEL', 'gpt-4o')
    prompt = ANALYSIS_PROMPT.format(document_content=document_content)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                'role': 'system',
                'content': '你是一名专业的法官助理，协助庭长对裁判文书草稿进行阅核。请严格按要求输出 Markdown 格式的阅核报告。',
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        temperature=0.2,
        max_tokens=4096,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError('AI 模型返回了空响应，请稍后重试')
    return content
