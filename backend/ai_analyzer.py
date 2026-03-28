"""AI 分析模块：调用 LLM 生成阅核报告"""
from __future__ import annotations

import os
import textwrap
from typing import Optional


SYSTEM_PROMPT = textwrap.dedent("""\
    你是一名经验丰富的高级法官助理，精通公司法、合同法及商事审判实务。
    庭长将向你提供一份裁判文书草稿，请你严格按照以下三个部分进行分析并全部使用 Markdown 格式输出。
    分析时请严格保留案件核心细节，不要过度删减。

    ---
    ## 一、案情事实与思维导图

    ### 1.1 案情简述
    用精炼的语言客观概括原告诉求、被告答辩及案件核心事实。

    ### 1.2 事实思维导图
    使用 Mermaid 代码绘制案情时间线、法律关系主体图或资金流向图（优先选择最能反映本案特征的图类型）。
    代码块格式必须为：
    ```mermaid
    graph TD
        ...
    ```

    ### 1.3 争议焦点
    提炼本案核心争议，逐条列出。

    ---
    ## 二、案件研究报告

    ### 2.1 法律适用审查
    基于现行公司法及相关商事法律规范，分析草稿中的法律适用是否准确，指出潜在问题。

    ### 2.2 类案裁判规则提示
    基于公开的商事审判原则（无需极度细化，侧重宏观裁判尺度），提示类似案件的常见处理思路和法律风险。

    ### 2.3 阅核意见
    给出是否同意签发的初步结论及理由，明确标注"**建议签发**"或"**建议退改**"。

    ---
    ## 三、判决书修订建议（修订人：石）

    针对文书中存在的事实认定不清、说理不透彻或表述不规范的段落进行修订，每处修订使用如下格式：

    **原文段落：**
    > [引用需要修改的原文]

    **修订后段落：**
    > [修改后的文本，**加粗**新增或修改的文字，~~删除线~~标识删除的文字]

    **【石评】：** [简要说明修改理由]

    ---
    如文书内容较短或信息不足，请在相应位置注明"（文书内容不足，无法完整分析，建议补充）"。
""")


async def analyze_document(
    document_text: str,
    api_key: str,
    model: str = "gpt-4o",
    base_url: Optional[str] = None,
) -> str:
    """
    调用 OpenAI 兼容接口分析文书，返回 Markdown 格式的阅核报告。
    如果未提供 API Key，则返回模拟示例报告（演示用）。
    """
    if not api_key:
        return _demo_report(document_text)

    try:
        from openai import AsyncOpenAI  # type: ignore
    except ImportError as exc:
        raise ImportError("请安装 openai 库：pip install openai") from exc

    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    client = AsyncOpenAI(**kwargs)

    # Truncate very long documents to stay within model context window limits.
    # At ~3 chars/token, 60 000 chars ≈ 20 000 tokens, leaving ample room for
    # the system prompt and the generated response within a 32k-token context.
    max_chars = 60000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n\n[...文书内容过长，已截断...]"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"以下是裁判文书草稿，请按要求进行阅核分析：\n\n---\n{document_text}\n---",
        },
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=8000,
    )

    return response.choices[0].message.content or ""


def _demo_report(document_text: str) -> str:
    """当未配置 API Key 时返回演示报告，说明系统功能。"""
    char_count = len(document_text)
    preview = document_text[:200].replace("\n", " ") + ("..." if len(document_text) > 200 else "")

    return textwrap.dedent(f"""\
        > ⚠️ **演示模式**：未配置 AI API Key，以下为系统功能演示。请在设置中填写您的 OpenAI API Key 以启用真实分析。

        ---

        ## 一、案情事实与思维导图

        ### 1.1 案情简述

        （演示）系统已接收文书内容（共 **{char_count}** 字符），内容预览：

        > {preview}

        配置 API Key 后，系统将自动提取：原告诉求、被告答辩、案件核心事实。

        ### 1.2 事实思维导图

        ```mermaid
        graph TD
            A["案件当事人"] --> B["原告"]
            A --> C["被告"]
            B --> D["诉讼请求"]
            C --> E["抗辩意见"]
            D --> F["核心争议"]
            E --> F
            F --> G["法院裁判"]
        ```

        ### 1.3 争议焦点

        1. （演示）争议焦点一：合同效力认定
        2. （演示）争议焦点二：损失数额计算
        3. （演示）争议焦点三：责任主体认定

        ---

        ## 二、案件研究报告

        ### 2.1 法律适用审查

        配置 API Key 后，系统将：
        - 核查引用法条的准确性
        - 分析法律适用逻辑
        - 指出潜在法律风险

        ### 2.2 类案裁判规则提示

        配置 API Key 后，系统将基于商事审判原则提供：
        - 类似案件处理思路
        - 常见裁判尺度
        - 法律风险提示

        ### 2.3 阅核意见

        **（演示）建议签发** / **建议退改**

        配置 API Key 后，系统将给出具体签发意见及理由。

        ---

        ## 三、判决书修订建议（修订人：石）

        **原文段落：**
        > （演示）原文示例段落

        **修订后段落：**
        > （演示）**修订后的文本**，~~删除的内容~~，**新增的内容**

        **【石评】：** 配置 API Key 后，系统将针对实际文书给出具体修订意见。
    """)
