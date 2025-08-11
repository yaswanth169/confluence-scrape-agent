#!/usr/bin/env python3
"""
Example script demonstrating LLaMA handler usage.
This shows how to use the LLaMA model directly without the full Crew AI system.
"""

from llama_handler import LLaMAHandler
import time

def main():
    """Demonstrate basic LLaMA functionality."""
    print("🤖 LLaMA Handler Example")
    print("=" * 50)
    
    # Create LLaMA handler instance
    print("📥 Creating LLaMA handler...")
    handler = LLaMAHandler()
    
    # Show model info before loading
    print(f"📊 Model path: {handler.model_path}")
    print(f"📊 Model loaded: {handler.is_model_loaded()}")
    
    # Load the model
    print("\n🔄 Loading LLaMA model...")
    start_time = time.time()
    
    if handler.load_model():
        load_time = time.time() - start_time
        print(f"✅ Model loaded successfully in {load_time:.2f} seconds")
        
        # Get model information
        model_info = handler.get_model_info()
        print(f"📊 Device: {model_info['device'].upper()}")
        print(f"📊 CUDA Available: {'✅ Yes' if model_info['cuda_available'] else '❌ No'}")
        
        # Test basic generation
        print("\n🧪 Testing basic text generation...")
        
        test_prompts = [
            "What is the capital of France?",
            "Explain machine learning in simple terms.",
            "Write a short poem about technology."
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Prompt {i}: {prompt}")
            print("-" * 40)
            
            start_gen = time.time()
            response = handler.generate_response(
                prompt=prompt,
                max_tokens=100,
                temperature=0.7,
                top_p=0.9
            )
            gen_time = time.time() - start_gen
            
            print(f"🤖 Response: {response}")
            print(f"⏱️ Generated in: {gen_time:.2f} seconds")
        
        # Test longer generation
        print("\n🧪 Testing longer text generation...")
        long_prompt = "Write a brief summary of artificial intelligence and its applications in modern business."
        
        print(f"📝 Long prompt: {long_prompt}")
        print("-" * 40)
        
        start_long = time.time()
        long_response = handler.generate_response(
            prompt=long_prompt,
            max_tokens=200,
            temperature=0.7,
            top_p=0.9
        )
        long_time = time.time() - start_long
        
        print(f"🤖 Long response: {long_response}")
        print(f"⏱️ Generated in: {long_time:.2f} seconds")
        
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        handler.cleanup()
        print("✅ Resources cleaned up")
        
    else:
        print("❌ Failed to load LLaMA model")
        print("\nTroubleshooting tips:")
        print("1. Check if the model path is correct")
        print("2. Ensure you have sufficient memory")
        print("3. Verify the model files exist")
        print("4. Check if PyTorch is properly installed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        print("\nThis might be due to:")
        print("1. Missing dependencies")
        print("2. Incorrect model path")
        print("3. Insufficient system resources")
