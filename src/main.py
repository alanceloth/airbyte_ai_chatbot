import os
import openai
from supabase import create_client, Client
from langchain_core.embeddings import DeterministicFakeEmbedding
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
api_key: str = os.getenv('OPENAI_API_KEY')

supabase: Client = create_client(url, key)
openai.api_key = api_key

embeddings = DeterministicFakeEmbedding(size=1536)

def get_context(question: str) -> str:
    # Embed the user's question
    question_embedding = embeddings.embed_query(question)
    
    results = []
    
    # Determine which table to query based on keywords in the question
    if "customer" in question.lower():
        query = supabase.rpc("find_related_customer", {'question_vector': question_embedding}).execute()
    elif "product" in question.lower():
        query = supabase.rpc("find_related_products", {'question_vector': question_embedding}).execute()
    elif "invoice" in question.lower():
        query = supabase.rpc("find_related_invoices", {'question_vector': question_embedding}).execute()
    else:
        return "No relevant context found for the given question."

    # Process query results
    for item in query.data:
        results.append(item)

    return results

# Function to get AI response using OpenAI's chat completion
def get_response(question: str):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions about the customers, products, and invoices provided to you in the context. Use only the provided context to answer questions. If the information isn't in the context, say so."},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{get_context(question)}"}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def main():
    question = "Is there a customer named Bob Johnson? If so, show me his information"
    answer = get_response(question)
    print("Answer:", answer)
    #save output to a file txt called output.txt
    with open("output.txt", "w") as f:
        f.write(answer)


if __name__ == "__main__":
    main()