import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrockConverse
load_dotenv()

model=ChatBedrockConverse(
    model=os.getenv("BEDROCK_MODEL_ID"),
    region_name=os.getenv("AWS_REGION"),
    temperature=0
)
parser=StrOutputParser()
chain= model | parser

def ask(question):
    return chain.invoke(question)
