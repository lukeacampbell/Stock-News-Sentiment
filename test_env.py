"""
Test script to verify environment variables are set up correctly
"""
import os
from dotenv import load_dotenv

def test_environment():
    # Load environment variables
    load_dotenv()
    
    # Check required API keys
    groq_key = os.getenv("GROQ_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    
    print("🔍 Environment Variable Check:")
    print(f"✅ GROQ_API_KEY: {'Found' if groq_key else '❌ Missing'}")
    print(f"✅ FINNHUB_API_KEY: {'Found' if finnhub_key else '❌ Missing'}")
    
    if groq_key and finnhub_key:
        print("\n🎉 All API keys found! Ready for deployment.")
        return True
    else:
        print("\n⚠️  Missing API keys. Please check your .env file.")
        return False

if __name__ == "__main__":
    test_environment()