import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
from typing import Optional, Dict, Any
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLaMAHandler:
    """Handler for local LLaMA model integration with Crew AI."""
    
    def __init__(self, model_path: str = None):
        """Initialize the LLaMA handler."""
        self.model_path = model_path or "C:/devhome/projects/meta-llama-Llama-3-2-1B-Instruct/meta-llama-Llama-3-2-1B-Instruct"
        self.tokenizer = None
        self.model = None
        self.device = None
        self.model_loaded = False
        
    def load_model(self) -> bool:
        """Load the LLaMA model and tokenizer."""
        try:
            logger.info(f"Loading LLaMA model from: {self.model_path}")
            
            # Check if model path exists
            if not os.path.exists(self.model_path):
                logger.error(f"Model path does not exist: {self.model_path}")
                return False
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                local_files_only=True
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path, 
                local_files_only=True, 
                torch_dtype=torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Set device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            if self.device == "cpu":
                self.model.to(self.device)
            
            self.model_loaded = True
            logger.info(f"✅ LLaMA model loaded successfully on {self.device.upper()}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading LLaMA model: {str(e)}")
            self.model_loaded = False
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7, top_p: float = 0.9) -> str:
        """Generate a response using the LLaMA model."""
        if not self.model_loaded:
            return "❌ Model not loaded. Please check the model path."
        
        try:
            # Format input for LLaMA 3.2 Instruct
            formatted_input = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
            
            # Tokenize input
            inputs = self.tokenizer(
                formatted_input, 
                return_tensors="pt", 
                truncation=True, 
                max_length=2048
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up response
            if formatted_input in response:
                response = response.replace(formatted_input, "").strip()
            
            response = response.replace("<|eot_id|>", "").replace("<|end_of_text|>", "").strip()
            
            if not response:
                response = "I understand your question, but I'm having trouble generating a response right now. Could you please rephrase your question?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"❌ Error generating response: {str(e)}"
    
    def is_model_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self.model_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.model_loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": self.model_path,
            "device": self.device,
            "model_type": type(self.model).__name__,
            "tokenizer_type": type(self.tokenizer).__name__,
            "cuda_available": torch.cuda.is_available()
        }
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model is not None:
            del self.model
        if self.tokenizer is not None:
            del self.tokenizer
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.model_loaded = False
        logger.info("Model resources cleaned up")

# Global instance for use across the application
llama_handler = LLaMAHandler()
