from jieba import analyse
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """抽取关键词节点

    使用jieba分词从用户查询中提取关键词。

    :param state: DataAgentState，包含query等状态信息
    :param runtime: Runtime[DataAgentContext]，包含stream_writer等上下文
    :return: dict，包含keywords键，值为提取的关键词列表
    """
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "抽取关键词","status":"running"})

    try:
        query = state["query"]

        allow_pos = [
            "n",  # 名词:数据、服务器、表格
            "nr",  # 人名:张三、李四
            "ns",  # 地名:北京、上海
            "nt",  # 机构名:公司、学校
            "nz",  # 其他专名:苹果、华为
            "v",  # 动词:运行、停止
            "vn",  # 名词性动词:分析、设计
            "a",  # 形容词:大的、小的
            "an",  # 名词性形容词:美丽的、漂亮的
            "eng",  # 英文单词
            "i",  # 成语
            "l"  # 习惯用语
        ]

        keywords = analyse.extract_tags(query, allowPOS=allow_pos)

        keywords = list(set(keywords + [query]))
        writer({"type": "progress", "step": "抽取关键词","status":"success"})
        logger.info(f"抽取关键词:{keywords}")
        return {"keywords": keywords}
    except Exception as e:
        logger.error(e)
        writer({"type": "progress", "step": "抽取关键词","status":"error"})
        raise

