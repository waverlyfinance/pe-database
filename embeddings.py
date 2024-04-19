from openai import OpenAI
import os

# Generate embeddings
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

def generate_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    output = response.data[0].embedding
    print(output)
    return output

# Example text
# text = "Headquartered in Phoenix, AZ, FastMed is one of the nation’s leading urgent care providers with 114 clinics located throughout Arizona, North Carolina, and Texas. The Company provides walk-in treatment for acute illnesses and injuries and differentiates itself with a low-cost, physician assistant based model. FastMed has expanded through acquisitions and de novo clinic launches, completing six acquisitions and opening an average of 14 clinics a year since 2010."

generate_embedding("Waste management")
