from openai import OpenAI
import os

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

messages = [
    {
        "role": "system",
        "content": (
            """
            You are an artificial intelligence assistant and you need to engage in a helpful, detailed, polite conversation with a user.
            Provide citations whenever you state facts. In this case, you will need to cite the news article or source that you got the information from.
            * Use end footnote citations containing the url of the source in the following style [citation|url]. Output the citation as a seperate markdown paragraph at the end of your response
            * For example, a reference from "https://www.exac.com/exactech-announces-completion-of-merger-with-tpg-capital/" would be [citation|https://www.exac.com/exactech-announces-completion-of-merger-with-tpg-capital/]."""
        ),
    },
    {
        "role": "user",
        "content": (
            "Is Exactech still owned by its founder? Note that in a Private Equity acquisition, the founders can still retain some portion of ownership"
        ),
    },
]

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

# chat completion without streaming
response = client.chat.completions.create(
    model="llama-3-sonar-large-32k-online",
    messages=messages,
)
print(response)