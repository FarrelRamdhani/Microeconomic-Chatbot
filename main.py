"""Main program for the Microeconomics Chatbot"""

# Import the necessary modules
import json
import openai
import streamlit as st
from llama_index.core import Document
from llama_index.retrievers.bm25 import BM25Retriever

# Prompt
search_system_prompt = """You are a Search Query Generator specialized in crafting BM25 queries for Elasticsearch, with a focus on microeconomics topics. You will receive a user’s chat history containing multiple turns related to microeconomics. Your task is to analyze that history, extract key microeconomic concepts, and generate a clear, concise, and optimized BM25 search query.

Instructions:
1. Identify and extract the core microeconomics concepts (e.g., supply, demand, market equilibrium, consumer surplus, price elasticity, etc.) from the chat history.
2. Use BM25 optimization techniques: incorporate Boolean operators (AND, OR), phrase matching (using quotes for exact phrases), and term boosting if needed.
3. Consider synonyms and related terms to cover variations (e.g., "price elasticity" may also relate to "elasticity of demand").
4. Use a multi-shot approach: if multiple distinct questions or ideas are present, generate a compound query that covers each point.
5. Be succinct and output only the final BM25 query with no extra commentary.
6. Follow these examples as guides:

   Example 1:
   - Chat history snippet: "How does price elasticity affect consumer demand?"
   - Generated query: `"price elasticity" AND "consumer demand" AND microeconomics`
   
   Example 2:
   - Chat history snippet: "Discuss market equilibrium and the effects of supply and demand shifts."
   - Generated query: `("market equilibrium" OR "supply demand") AND microeconomics`
   
   Example 3 (Multi-shot):
   - Chat history includes two topics: one about "consumer surplus" affected by price changes, and another on "price discrimination" and its market impact.
   - Generated query: `("consumer surplus" AND "price changes") OR ("price discrimination" AND "market efficiency") AND microeconomics`

Make sure to follow the above instructions and examples to generate a BM25 query that is both precise and tailored to microeconomics.
Directly provide the final BM25 query as your response"""

search_user_prompt = """Chat History: 
{chat_history}
Instruction: Using the above chat history, generate an optimized BM25 query for Elasticsearch that captures all key microeconomic concepts mentioned.
Search query: """

answer_system_prompt = """You are an Answer Generator specialized in synthesizing information from multiple sources to respond accurately to user queries on microeconomics topics. You will receive three types of information: the chat history, the documents, and a BM25-optimized search query focused on microeconomics.

Instructions:
1. Analyze the chat history to understand the context and specific microeconomic concerns raised by the user.
2. Review the provided documents carefully and extract key insights that address the user’s query.
3. Use the BM25-optimized search query as a guide to focus on the relevant topics within the documents.
4. Synthesize the extracted information into a clear, coherent, and contextually accurate answer.
5. If any piece of information is missing or not applicable, adjust your response to rely on the available data.
6. Provide a concise final answer that directly addresses the user query, using evidence from the documents when relevant."""

answer_user_prompt = """Below is the context and information available to help answer your query:

Chat History: {chat_history}

Search Query: {search_query}
This search query then resulted in founding:
Documents: {documents}
Based on the above information, please provide a detailed answer to the user’s query. Ensure that your response integrates the relevant points from the documents, aligns with the context from the chat history, and addresses the microeconomics topics highlighted by the search query."""


# Load the documents from JSON file
with open("knowledge.json", "r") as f:
    knowledge_data = json.load(f)

# Convert the JSON data into Document objects
documents = []
for item in knowledge_data:
    # Load the document text from the file
    with open(item["filename"], "r") as f:
        opened_document = f.read()

    # Convert dictionary item to Document
    doc = Document(text=item["summary"], metadata={
        "filename": item["filename"],
        "text": opened_document
    })
    documents.append(doc)

# Create a BM25 retriever: Will retrieve the top 3 documents
retriever = BM25Retriever.from_defaults(
    nodes=documents, similarity_top_k=3
)

# Initiate the openai package to interact with Kolosal AI
llm = openai.OpenAI(base_url="http://localhost:8080/v1",
                    api_key="sk-dummy")

# User Interface
st.title("Microeconomics Chatbot")
st.write("Welcome to the Microeconomics Chatbot! Please ask me any questions you have about microeconomics.")
st.caption("Powered locally by Kolosal AI")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input via chat
if user_prompt := st.chat_input("Ask me anything about microeconomics"):
    # Display and save the user's message
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Build the chat history into string for LLM consumption
    built_chat_history = ""
    for chat in st.session_state.messages:
        if chat["role"] == "user":
            built_chat_history += f"User: {chat['content']}"
        else:
            built_chat_history += f"Assistant: {chat['content']}"

    # Generate search query
    with st.spinner("Generating search query..."):
        search_query = llm.chat.completions.create(
            model="kolosal",
            messages=[
                {"role": "system", "content": search_system_prompt},
                {"role": "user", "content": search_user_prompt.format(chat_history=built_chat_history)}
            ],
            max_tokens=128
        )
    
    # Search documents
    built_documents = ""
    with st.spinner("Searching documents..."):
        retrieved_documents = retriever.retrieve(search_query.choices[0].message.content)
        
        # Built the retrieved documents into string
        for doc in retrieved_documents:
            built_documents += f"Document name: {doc.metadata['filename']}\n"
            built_documents += f"{doc.metadata['text']}\n\n"
    
    # Generate response
    with st.spinner("Generating response..."):
        # Create a placeholder for the streamed response
        response_placeholder = st.empty()
        
        # Initialize an empty response
        full_response = ""
        
        # Create streaming chat completion
        with st.chat_message("assistant"):
            stream = llm.chat.completions.create(
                model="kolosal",
                messages=[
                    {"role": "system", "content": answer_system_prompt},
                    {"role": "user", "content": answer_user_prompt.format(
                        chat_history=built_chat_history,
                        search_query=search_query.choices[0].message.content,
                        documents=built_documents
                    )}
                ],
                stream=True
            )
            
            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    response_placeholder.markdown(full_response)
        
        # Add the complete response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Display the documents as toggleable dropdowns
    st.subheader("Referenced Documents")
    for doc in retrieved_documents:
        with st.expander(f"📄 {doc.metadata['filename']}"):
            st.markdown("---")
            st.markdown(doc.metadata['text'])
            st.markdown("---")
    

