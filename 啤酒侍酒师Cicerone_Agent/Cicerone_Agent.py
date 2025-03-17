from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

prompt_template = ChatPromptTemplate.from_messages(
    [
        ('system', "你是一个职业啤酒侍酒师。当用户说他对某一类啤酒感兴趣时，请向用户介绍该类啤酒的特点，如风味、香气、酵母类型、发酵温度等。"),
        ('human', "虽然我喜欢喝啤酒，但其实我对啤酒的了解并不多，我听人说{beer}挺不错的，你能向我介绍一下它的特色吗？")
    ]
)
prompt_template.format(beer='比利时修道院啤酒')

model = ChatOpenAI(
    model = 'glm-4',
    openai_api_base = "https://open.bigmodel.cn/api/paas/v4/",
    max_tokens = 600,
    temperature = 0.7
)

def output_parser(output: str):
    parser_model = ChatOpenAI(
        model = 'glm-3-turbo',
        temperature=0.8,
        openai_api_base = "https://open.bigmodel.cn/api/paas/v4/"
    )
    message = "你需要将传入的文本改写，尽可能更自然。这是你需要改写的文本:`{text}`"
    return parser_model.invoke(message.format(text=output))

chain = prompt_template | model | output_parser
while True:
    beer = input("你想喝点什么呢？")
    answer = chain.invoke(input = {'beer': beer})
    print(answer.content)