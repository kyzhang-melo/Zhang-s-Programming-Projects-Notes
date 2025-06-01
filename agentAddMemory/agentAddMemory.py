import datetime
import os
from enum import Enum

import requests
from dotenv import load_dotenv
from loguru import logger
from zhipuai import ZhipuAI

load_dotenv()

logger.remove(0)
# 添加一个记录 TRACE 级别日志的处理程序
logger.add("memory.log", filter=lambda record: record["level"].name == "TRACE", level="TRACE", format="{message}")


class FontColor(Enum):
    BLUE_BOLD = "\033[1;34m"
    GREEN_BOLD = "\033[1;32m"
    RED_BOLD = "\033[1;31m"
    RESET = "\033[0m"


class Memory:
    def __init__(self, embedding_url: str, embedding_api_key: str, top_k: int = 1):
        """
        Initialize the Memory system with embedding service configuration.
        
        Args:
            embedding_url: URL for the embedding service
            embedding_api_key: API key for the embedding service
            top_k: Number of most relevant memories to retrieve (default: 5)
        """
        self.embedding_url = embedding_url
        self.embedding_api_key = embedding_api_key
        self.top_k = top_k
        self.memories = []
        
    def _get_embedding(self, text: str) -> list[float]:
        """Get vector embedding for text using the configured embedding service."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.embedding_api_key}"
        }
        
        data = {
            "input": text,
            "encoding_format": "float",
            "model": "embedding-3"
        }
        
        response = requests.request("POST", url=self.embedding_url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            raise Exception(f"Error getting embedding: {response.text}")
    
    def add_user_memory(self, content: str) -> None:
        """Add a user query to memory with timestamp and embedding."""
        timestamp = datetime.datetime.now().isoformat()
        embedding = self._get_embedding(content)
        
        memory_entry = {
            "content": content,
            "timestamp": timestamp,
            "embedding": embedding,
            "type": "user"
        }
        
        self.memories.append(memory_entry)
        
    def add_ai_memory(self, content: str) -> None:
        """Add an AI response to memory with timestamp and embedding."""
        timestamp = datetime.datetime.now().isoformat()
        embedding = self._get_embedding(content)
        
        memory_entry = {
            "content": content,
            "timestamp": timestamp,
            "embedding": embedding,
            "type": "ai"
        }
        
        self.memories.append(memory_entry)
    
    def _calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        if magnitude1 * magnitude2 == 0:
            return 0
            
        return dot_product / (magnitude1 * magnitude2)
    
    def search(self, query: str) -> str:
        """
        Search for relevant memories based on semantic similarity to the query.
        
        Args:
            query: The search query
            
        Returns:
            String containing the most relevant memories formatted for context
        """
        logger.trace(f"Searching for relevant memories for query: {query}")
        if not self.memories:
            logger.trace("No memories available.\n")
            return "No memories available."
            
        query_embedding = self._get_embedding(query)
        
        # Calculate similarity with each memory
        similarities = []
        for i, memory in enumerate(self.memories):
            similarity = self._calculate_similarity(query_embedding, memory["embedding"])
            similarities.append((i, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k most relevant memories
        top_memories = []
        for i in range(min(self.top_k, len(similarities))):
            memory_idx = similarities[i][0]
            memory = self.memories[memory_idx]
            memory_str = f"[{memory['timestamp']}] ({memory['type']}): {memory['content']}"
            top_memories.append(memory_str)
        
        logger.trace(f"Top memories: {top_memories}\n")

        return "\n".join(top_memories)


def main():
    print(
        f'''
        {FontColor.RED_BOLD.value}
        让我们做个实验，看看是否真的能记住我们的对话。
        先发送query说我在学习Python，然后再次发送query让它帮我写一段代码，如果它记住了对话，就会使用Python来回答。
        ''')
    
    # chat with memories
    print(f'{FontColor.RED_BOLD.value}第一轮对话{FontColor.RESET.value}')
    memory = init_memory()
    zhipuai_client = ZhipuAI(
        base_url = "https://open.bigmodel.cn/api/paas/v4",
        api_key = os.getenv('ZHIPUAI_API_KEY')
    )
    query_lst = ["我在学习Python，不用给我建议，我只是告诉你", "请帮我写一个Car类和一个Engine类，然后组合它们。"]
    chat(query_lst, memory, zhipuai_client)

    print(f'''{FontColor.RED_BOLD.value}
        再次做个试验，看看AI是否只会读取相关的记忆。
        发送三次query。
        第一次说我喜欢喝什么，兴趣是什么。
        第二次说我正在学习Python。
        第三次让它帮我写一段代码。
        查看log文件，看看AI是否只会读取相关的记忆。{FontColor.RESET.value}''')
    memory = init_memory()
    query_lst = ["我喜欢喝啤酒，兴趣是看书", "我在学习Python，不用给我建议，我只是告诉你", "请帮我写一个Car类和一个Engine类，然后组合它们。"]
    chat(query_lst, memory, zhipuai_client)


def init_memory():
    memory = Memory(
        embedding_url = "https://open.bigmodel.cn/api/paas/v4/embeddings",
        embedding_api_key = os.getenv('EMBEDDING_API_KEY')
    )
    return memory


def chat(query_lst:list[str], memory:Memory, zhipuai_client:ZhipuAI):
    for idx, query in enumerate(query_lst):
        print(f'用户输入：{FontColor.BLUE_BOLD.value}{query}{FontColor.RESET.value}')

        relevant_memories = memory.search(query=query)

        system_prompt = f"You are a helpful AI. Answer the question based on query and memories.\nUser Memories:\n{relevant_memories}"
        response = zhipuai_client.chat.completions.create(
                            model="glm-4",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": query}
                            ])
        assistant_response = response.choices[0].message.content
        memory.add_user_memory(query)
        memory.add_ai_memory(assistant_response)
        print(f"{FontColor.GREEN_BOLD.value}{assistant_response}{FontColor.RESET.value}")


if __name__ == "__main__":
    main()