"""
Quick test script to verify OpenRouter API connection
Run this first to make sure everything is configured correctly
"""

import os
from langchain_openai import ChatOpenAI

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    
    print("\n" + "="*60)
    print("OPENROUTER CONNECTION TEST")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY not set!")
        print("\nPlease set it:")
        print("  export OPENROUTER_API_KEY='sk-or-v1-your-key-here'")
        return False
    
    print(f"\n✓ API Key found: {api_key[:15]}...{api_key[-4:]}")
    
    # Get model
    model = os.getenv("LLM_MODEL", "google/gemini-3-flash-preview")
    print(f"✓ Using model: {model}")
    
    # Test connection
    print("\n" + "-"*60)
    print("Testing API call...")
    print("-"*60)
    
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            max_tokens=128,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "Regulation Intelligence Agent",
            }
        )
        
        # Make a simple test call
        response = llm.invoke("Say 'Hello from OpenRouter!' and nothing else.")
        
        print(f"\n✅ SUCCESS! Response received:")
        print(f"   {response.content}")
        
        print("\n" + "="*60)
        print("CONNECTION TEST PASSED! ✓")
        print("="*60)
        print("\nYou're ready to run the main agent!")
        print("Next steps:")
        print("  python regulation_intelligence_agent.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nCommon issues:")
        print("  1. Invalid API key - check https://openrouter.ai/keys")
        print("  2. Model not available - check https://openrouter.ai/models")
        print("  3. Insufficient credits - add credits at https://openrouter.ai/credits")
        print("  4. Rate limit - wait 60 seconds and try again")
        
        return False


def test_embeddings():
    """Test local embeddings"""
    
    print("\n" + "="*60)
    print("EMBEDDING MODEL TEST")
    print("="*60)
    
    try:
        print("\nLoading sentence-transformers model...")
        print("(First run will download ~90MB)")
        
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        print("✓ Model loaded successfully!")
        
        # Test embedding
        test_text = "This is a test sentence for embeddings."
        embedding = model.encode([test_text])
        
        print(f"✓ Generated embedding (shape: {embedding.shape})")
        print(f"✓ Embedding dimension: {embedding.shape[1]}")
        
        print("\n" + "="*60)
        print("EMBEDDING TEST PASSED! ✓")
        print("="*60)
        
        return True
        
    except ImportError:
        print("\n❌ ERROR: sentence-transformers not installed")
        print("\nInstall it with:")
        print("  pip install sentence-transformers torch")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def run_all_tests():
    """Run all connection tests"""
    
    print("\n" + "="*70)
    print("REGULATION INTELLIGENCE AGENT - SYSTEM CHECK")
    print("="*70)
    
    # Test 1: OpenRouter
    openrouter_ok = test_openrouter_connection()
    
    # Test 2: Embeddings
    embeddings_ok = test_embeddings()
    
    # Summary
    print("\n" + "="*70)
    print("SYSTEM CHECK SUMMARY")
    print("="*70)
    print(f"\nOpenRouter API: {'✅ PASS' if openrouter_ok else '❌ FAIL'}")
    print(f"Local Embeddings: {'✅ PASS' if embeddings_ok else '❌ FAIL'}")
    
    if openrouter_ok and embeddings_ok:
        print("\n🎉 All systems ready! You can now run:")
        print("   python regulation_intelligence_agent.py")
    else:
        print("\n⚠️  Please fix the issues above before proceeding.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    # Set your API key here for testing
    # os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-your-key-here"
    
    run_all_tests()