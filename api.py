import streamlit as st
import re
from langchain_upstage import ChatUpstage
from langchain.utilities import GoogleSerperAPIWrapper
from typing import List
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import json

import os
import getpass
from pprint import pprint
import warnings
from config import Upstage_API  # config.py에서 Upstage_API 키를 가져옴
from openai import OpenAI
from config import Google_API
warnings.filterwarnings("ignore")

if "UPSTAGE_API_KEY" not in os.environ:
    os.environ["UPSTAGE_API_KEY"] = Upstage_API
client = OpenAI(
    api_key=os.environ["UPSTAGE_API_KEY"], base_url="https://api.upstage.ai/v1/solar"
)

google_search = GoogleSerperAPIWrapper(serper_api_key=Google_API)


def convert_time_period(period, hour):
    hour = int(hour)
    if period == "오후": 
        if hour != 12: hour += 12
    elif period == "오전":
        if hour == 12:
            hour = 0
    return f"{hour:02d}"

def reformat_line(line):
    pattern = r"(\d{4})년\s+(\d{1,2})월\s+(\d{1,2})일\s+(오전|오후)\s+(\d{1,2}):(\d{2}),\s+(.+?):\s+(.*)"
    match = re.match(pattern, line)
    if match:
        year, month, day, period, hour, minute, user, message = match.groups()
        month = f"{int(month):02d}"
        day = f"{int(day):02d}"
        hour_24 = convert_time_period(period, hour)
        time_24 = f"{hour_24}:{minute}"
        new_date_time = f"{month}/{day}:{time_24}"
        new_line = f"{new_date_time}:{user}:{message}"
        return new_line
    elif line.strip() == "":
        return None
    elif "저장한 날짜" in line:
        return None
    else:
        return line

# return value : string
# 카카오톡 대화 정보 > 글자수 줄이기
def parse(input) :
    transformed_lines = []
    text= input.getvalue().decode("utf-8")
    name = None
    for line in text.split('\n'):
        reformatted = reformat_line(line)
        if reformatted is None: continue
        if "님과 카카오톡 대화" in reformatted:
            name = reformatted.split("님과 카카오톡 대화")[0]
        else:
            transformed_lines.append(reformatted)
    print(name)
    print(transformed_lines)
    return name, '\n'.join(transformed_lines)

# 상대방 정보를 특정할 수 있는 string 반환
def make_persona(state):
    uploaded_file = state.uploaded_file
    special_info = state.special_info
    name = state.name
    chat_result = client.chat.completions.create(
    model="solar-1-mini-chat",
    messages=[
            {"role": "system", "content": 
            """
            너는 페르소나 분석가로서, 사용자가 제공하는 대화 내역과 추가 정보를 바탕으로 상대방의 성격, 관심사, 취미, 대인관계 스타일 등을 카테고리별로 분석하여 매우 자세한 페르소나 정보를 생성해야 해.
            """,
            },
            {"role": "user", "content": f"""
            다음은 상대방에 대한 정보입니다:
            
            이름: {name}
            대화 내용: {uploaded_file}
            추가 정보: {special_info}

            이 정보를 바탕으로 상대방의 페르소나를 다음 카테고리로 나누어 자세히 설명해줘:
            1. 성격
            2. 관심사
            3. 취미
            4. 대인관계 스타일
            5. 가치관
            6. 거주 지역
            7. 좋아하는 음식
            """},
    ],
    )
    response_text = chat_result.choices[0].message.content
    print(response_text)
    return response_text

# return value : string
# state keys() : ['uploaded_file', 'special_info', 'persona', 'name']
# 상대방 정보 요약
def summarey(state):
    uploaded_file = state.uploaded_file
    special_info = state.special_info
    persona = state.persona
    name = state.name
    chat_result = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": 
            """
            너는 정보 요약가로서, 사용자가 제공하는 상대방에 대한 정보와 대화 내용을 바탕으로 그 사람의 핵심적인 특성을 간략하게 요약해야 해. 
            요약할 때는 성격, 관심사, 취미, 추가 정보 등을 포함하되 간결하게 작성하도록 해.
            """},
            {"role": "user", "content": f"""
            다음은 상대방에 대한 정보입니다:

            이름: {name}
            대화 내용: {uploaded_file}
            추가 정보: {special_info}
            페르소나: {persona}

            이 정보를 바탕으로 상대방에 대한 요약을 간략하게 5줄내로 제공해줘.
            """},
        ],
    )
    response_text = chat_result.choices[0].message.content
    return response_text

# return value : string
# state.keys() : ['uploaded_file', 'special_info', 'persona', 'name']
# Using RAG model
# 함수 3: 커스텀 리트리버 클래스 정의
class SerperRetriever(BaseRetriever):
    search_tool: GoogleSerperAPIWrapper = Field(description="The search tool to use")

    def get_relevant_documents(self, query: str) -> List[Document]:
        search_result = self.search_tool.run(query)
        documents = []

        if isinstance(search_result, str):
            return [Document(page_content=search_result, metadata={"source": "No URL available"})]
        
        if isinstance(search_result, dict):
            if 'organic' in search_result:
                for item in search_result['organic']:
                    documents.append(Document(
                        page_content=item.get('snippet', ''),
                        metadata={"source": item.get('link', 'No URL available')}
                    ))
            elif 'answerBox' in search_result:
                answer_box = search_result['answerBox']
                documents.append(Document(
                    page_content=answer_box.get('snippet', ''),
                    metadata={"source": answer_box.get('link', 'No URL available')}
                ))
            else:
                documents.append(Document(
                    page_content=str(search_result),
                    metadata={"source": "No URL available"}
                ))
        
        return documents

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        return self.get_relevant_documents(query)

def create_retriever(search_tool: GoogleSerperAPIWrapper) -> SerperRetriever:
    return SerperRetriever(search_tool=search_tool)

def create_prompt_template() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a helpful assistant. Based on the following information, answer the user's question shorty:\n
        {context}\n 
        Question: {question}\n
        Answer:
        """
    )

def create_rag_chain(llm, retriever, prompt_template) -> RetrievalQA:
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )

def run_rag_chain(qa_chain, query: str):
    result = qa_chain({"query": query})
    answer = result['result']
    sources = result['source_documents']
    return answer, sources

llm=ChatUpstage()


# return value : string
# state.keys() : ['uploaded_file', 'special_info', 'persona', 'name']
def date_course(state): 
    query =f"""
        제공한 정보를 바탕으로 데이트 코스를 3개 추천해줘\n
        각 데이트 코스는 실제로 존재하는 음식점을 포함해야해\n
        이름: {state.name}\n
        페르소나: {state.persona}\n
    """
    qa_chain = create_rag_chain(llm, create_retriever(google_search), create_prompt_template())
    return run_rag_chain(qa_chain, query)[0]

# return value : string
# state.keys() : ['uploaded_file', 'special_info', 'persona', 'name']
# 현재 대화에 대한 평가
def evaluate(state):
    uploaded_file = state.uploaded_file
    special_info = state.special_info
    persona = state.persona
    name = state.name
    chat_input = state.chat_input
    chat_result = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": 
            """
            너는 대화 분석가로서, 사용자가 제공하는 정보와 대화 입력을 바탕으로 상대방이 그 입력을 어떻게 받아들일지를 평가해야 해. 
            상대방의 성격, 관심사, 대인관계 스타일을 고려하여 그 입력이 긍정적일지 부정적일지를 설명하고, 이유를 상세하게 제시해야 해.
            """},
            {"role": "user", "content": f"""
            다음은 상대방에 대한 정보입니다:

            이름: {name}
            대화 내용: {uploaded_file}
            추가 정보: {special_info}
            페르소나: {persona}

            그리고 다음은 내가 상대방에게 보낸 메시지입니다:
            {chat_input}

            이 메시지가 상대방에게 긍정적일지 부정적일지 평가해주고, 그 이유를 자세히 설명해줘.
            """},
        ],
    )
    response_text = chat_result.choices[0].message.content
    return response_text

# return value : string
# state.keys() : ['uploaded_file', 'special_info', 'persona', 'name']
# 상대방에 맞춤 연애 팁 제공
def tips(state):
    uploaded_file = state.uploaded_file
    special_info = state.special_info
    name = state.name
    persona = state.persona
    chat_result = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": 
            """
            너는 연애 상담가로서, 사용자가 제공하는 상대방에 대한 정보와 대화 내역을 바탕으로 맞춤형 연애 팁 5개를 제공해야 해.
            상대방의 성격, 관심사, 취미 및 대인관계 스타일을 고려하여 적절한 조언을 제시하도록 해.
            """},
            {"role": "user", "content": f"""
            다음은 상대방에 대한 정보입니다:

            이름: {name}
            페르소나: {persona}
            대화 내용: {uploaded_file}
            추가 정보: {special_info}
            이 정보를 바탕으로 상대방에게 적합한 맞춤형 연애 팁을 제공해줘.
            """},
        ],
    )
    response_text = chat_result.choices[0].message.content
    print(response_text)
    return response_text
