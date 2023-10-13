from typing import (
        Tuple,
        Union,
        List
        )

from transformers import (
        DPRContextEncoderTokenizer,
        DPRContextEncoder
        )
import torch

def load_dpr_context_encoder(
        model_name_or_path: str
        )-> Tuple[DPRContextEncoder,DPRContextEncoderTokenizer]:
    """Load model DPR context encoder to encode knowledges

    Args:
        model_name_or_path: name of DPR model needs to be downloaded from
                            HuggingFace hub or path to DPR checkpoint
    """
    ctx_token = DPRContextEncoderTokenizer.from_pretrained(model_name_or_path)
    ctx_model = DPRContextEncoder.from_pretrained(model_name_or_path)

    return (ctx_model, ctx_token)

def get_ctx_embd(
        model_encoder: DPRContextEncoder,
        tokenizer: DPRContextEncoderTokenizer,
        text: Union[str, List[str]],
        device: torch.device
        ) -> torch.tensor:
    """Get knowledge embedding

    Args:
        model_encoder: DPR context encoder model
        tokenizer: DPR tokenizer
        text: a knowledge (sentence, paragraph,...)
    """
    model_encoder.eval()
    encoded_input = tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
            ).to(device)
    with torch.no_grad():
        model_output = model_encoder(**encoded_input)

    return model_output["pooler_output"]

