import os
from dotenv import load_dotenv
load_dotenv() 

from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.retrievers import WebResearchRetriever

def getDeepSeek():
    model = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"), 
        temperature=0,
    )
    # model = OpenAI(
    #     model="gpt-4o-mini"
    # )
    return model

def setup_web_researcher(persist_directory: str = "web_research_db") -> WebResearchRetriever:
    """
    Initialize the WebResearchRetriever with ChromaDB vector store and OpenAI.
    
    Args:
        persist_directory: Directory to store the ChromaDB database
    """
    # Initialize the embedding model
    embeddings = OpenAIEmbeddings()
    
    # Initialize ChromaDB vector store
    vectorstore = Chroma(
        collection_name="web_research",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    # Set up the LLM
    llm = OpenAI(temperature=0)
    #llm = getDeepSeek()
    
    # Initialize Google Search
    search = GoogleSearchAPIWrapper()
    
    # Create the WebResearchRetriever
    researcher = WebResearchRetriever.from_llm(
        vectorstore=vectorstore,
        llm=llm,
        search=search,
        num_search_results=3,  # Number of search results to analyze per query
        allow_dangerous_requests=True  # Be cautious with this in production
    )
    
    return researcher

_g_researcher = None

def research_topic(query: str, researcher: WebResearchRetriever) -> str:
    global _g_researcher
    """
    Perform web research on a given query and summarize the findings.
    
    Args:
        query: The research question
        researcher: Initialized WebResearchRetriever
    
    Returns:
        str: Summary of findings
    """

    researcher = _g_researcher if researcher is None else researcher
    # Get relevant documents
    documents = researcher.get_relevant_documents(query)
    
    # Create a summary prompt
    summary_prompt = f"""Based on the following extracted information, provide a comprehensive answer to: {query}
    
    Extracted information:
    {'-' * 50}
    {chr(10).join([doc.page_content for doc in documents])}
    {'-' * 50}
    
    Answer:"""
    
    # Generate summary using OpenAI
    llm = OpenAI(temperature=0.2)
    llm = getDeepSeek()
    summary = llm.invoke(summary_prompt)
    
    return summary

def ask_question(question: str) -> str:
    global _g_researcher
    # Initialize the researcher with persistent storage
    if _g_researcher is None :
        _g_researcher = setup_web_researcher()

    results = ""
    try:
        results = research_topic(question, _g_researcher)
        print("Research Findings:")
        print(results)
        
    except Exception as e:
        print(f"Error researching '{question}': {str(e)}")
        results = str(e)
    
    return results


def main():

    ask_question("What are the latest developments in quantum computing?")
    return
    
    # Example research questions
    research_questions = [
        "What are the latest developments in quantum computing?",
        "How does CRISPR gene editing work?",
        "What are the environmental impacts of electric vehicles?"
    ]
    
    # Perform research
    for question in research_questions:
        print(f"\n{'=' * 80}")
        print(f"Research Question: {question}")
        print(f"{'=' * 80}\n")
        ask_question(question)

        

if __name__ == "__main__":
    main()