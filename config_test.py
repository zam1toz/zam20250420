from dotenv import load_dotenv
import os   

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
else:
    print("OPENAI_API_KEY is set correctly.")
    # You can also print the key, but it's not recommended for security reasons
    # print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")