from transformers import AutoTokenizer, AutoModel
import config

# Global model cache
_embedding_model = None
_embedding_tokenizer = None


def get_embedding_model():
    global _embedding_model, _embedding_tokenizer
    
    if _embedding_model is None:
        _embedding_tokenizer = AutoTokenizer.from_pretrained(
            config.EMBEDDING_MODEL
        )
        _embedding_model = AutoModel.from_pretrained(
            config.EMBEDDING_MODEL
        )
        _embedding_model.eval()
    
    return _embedding_model, _embedding_tokenizer
