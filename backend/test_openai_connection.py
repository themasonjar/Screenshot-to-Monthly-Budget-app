import os
import openai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env file.")
    exit(1)

openai.api_key = api_key

def test_model(model_name):
    print(f"\nTesting model: {model_name}...")
    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=10
        )
        print(f"✅ Success! Response: {response.choices[0].message.content}")
        return True
    except openai.RateLimitError as e:
        print(f"❌ Rate Limit Error (429): {e}")
        print("   -> This usually means you have run out of credits or need to add a payment method.")
        return False
    except openai.NotFoundError as e:
        print(f"❌ Model Not Found (404): {e}")
        print("   -> Your API key might not have access to this model.")
        return False
    except openai.AuthenticationError as e:
        print(f"❌ Authentication Error (401): {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("--- OpenAI Connection Diagnostic ---")
    
    # Test cheaper/older model first
    gpt3_works = test_model("gpt-3.5-turbo")
    
    # Test the model we are using
    gpt4o_works = test_model("gpt-4o")

    # Test mini
    gpt4o_mini_works = test_model("gpt-4o-mini")

    print("\n--- Summary ---")
    if gpt4o_mini_works:
        print("GPT-4o-mini works! We should use this.")
    elif not gpt3_works:
        print("Nothing works.")
        print("Action: Go to https://platform.openai.com/account/billing and ensure you have 'Credit Balance'.")
    elif gpt3_works and not gpt4o_works:
        print("GPT-3.5 worked but GPT-4o failed. You might need to reach a higher usage tier for GPT-4o.")
    elif gpt4o_works:
        print("GPT-4o worked! The previous error might have been temporary.")
