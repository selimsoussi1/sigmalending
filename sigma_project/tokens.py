import tiktoken
from typing import Optional

def count_tokens(text: str, model_name: Optional[str] = "gemini-2.5-pro") -> int:
    """
    Counts the number of tokens in a given string using the tokenizer appropriate 
    for the specified model.

    Note: The actual token count can vary slightly between models. This function
    defaults to the encoding used by GPT-4 and GPT-3.5-Turbo (cl100k_base).

    Args:
        text (str): The string content to tokenize and count.
        model_name (str, optional): The name of the model to determine the 
                                    correct tokenizer encoding. 
                                    Defaults to "gpt-4".
                                    
    Returns:
        int: The token count.
    """
    try:
        # Get the appropriate encoding for the model.
        # This handles many common OpenAI models like gpt-4, gpt-3.5-turbo, etc.
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to the common cl100k_base encoding if the model name is unknown
        # This path is taken for models not supported by tiktoken, like Gemini.
        print(f"Warning: Model '{model_name}' not supported by tiktoken. Defaulting to 'cl100k_base' encoding for estimate.")
        encoding = tiktoken.get_encoding("cl100k_base")

    # Encode the text to get the list of tokens (integers)
    tokens = encoding.encode(text)
    
    # Return the number of tokens
    return len(tokens)