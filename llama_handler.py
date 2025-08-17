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
    
    _instance = None
    
    def __new__(cls, model_path: str = None):
        """Ensure only one instance of LLaMAHandler is created."""
        if cls._instance is None:
            cls._instance = super(LLaMAHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_path: str = None):
        """Initialize the LLaMA handler."""
        if not getattr(self, '_initialized', False):
            self.model_path = model_path or "C:/devhome/projects/meta-llama-Llama-3-2-1B-Instruct/meta-llama-Llama-3-2-1B-Instruct"
            self.tokenizer = None
            self.model = None
            self.device = None
            self.model_loaded = False
            self._initialized = True
    
    def load_model(self) -> bool:
        """Load the LLaMA model and tokenizer."""
        if self.model_loaded:
            logger.info("LLaMA model already loaded, reusing instance.")
            return True
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
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                logger.info("Using CUDA for LLaMA model")
            else:
                self.device = torch.device("cpu")
                logger.info("Using CPU for LLaMA model")
            
            # Move model to device
            self.model.to(self.device)
            
            self.model_loaded = True
            logger.info("LLaMA model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load LLaMA model: {e}")
            self.model_loaded = False
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7, top_p: float = 0.9) -> str:
        """Generate a response from the LLaMA model for a given prompt."""
        if not self.model_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load LLaMA model")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                padding=True, 
                truncation=True
            ).to(self.device)
            
            # Generate response
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_tokens,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=1,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Error: Unable to generate response."
    
    def is_model_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self.model_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_path": self.model_path,
            "device": self.device.type if self.device else "Not set",
            "loaded": self.model_loaded
        }
    
    def cleanup(self):
        """Clean up resources."""
        if self.model_loaded:
            try:
                del self.model
                del self.tokenizer
                torch.cuda.empty_cache()  # Clear GPU memory if using CUDA
                self.model_loaded = False
                logger.info("LLaMA model resources cleaned up")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
