from pathlib import Path
from openai import OpenAI
import os
import sys
import argparse
import tempfile
import math
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv
from pydub import AudioSegment
from colorama import init, Fore, Style
import time

# Initialize colorama for cross-platform colored terminal output
init()

# Load environment variables from .env file
load_dotenv()

# Constants
MAX_CHARS_PER_REQUEST = 3000  # Reduced from 4096 to improve reliability
COST_PER_1K_CHARS = {
    "tts-1": 0.015,      # $0.015 per 1K characters for standard model
    "tts-1-hd": 0.030    # $0.030 per 1K characters for high-definition model
}
SUPPORTED_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

def get_api_key(args=None):
    """Get API key from command line arguments or environment variables."""
    # Check if API key is provided as command-line argument
    if args and args.api_key:
        return args.api_key
    # Otherwise check environment variable
    elif 'OPENAI_API_KEY' in os.environ:
        return os.environ['OPENAI_API_KEY']
    else:
        print("Error: OpenAI API key not found.")
        print("Either set the OPENAI_API_KEY environment variable or provide it as a command-line argument.")
        print("Example: python generator.py --api-key your-api-key")
        sys.exit(1)

def get_input_text(input_file_path, default_text="Your text here."):
    """Read text from input file with error handling."""
    try:
        with open(input_file_path, 'r') as file:
            input_text = file.read().strip()
        
        if not input_text:
            print(f"Warning: Input file '{input_file_path}' is empty. Using default text.")
            return default_text
        return input_text
    except FileNotFoundError:
        print(f"Input file '{input_file_path}' not found. Using default text.")
        return default_text
    except IOError as e:
        print(f"Error reading file '{input_file_path}': {str(e)}. Using default text.")
        return default_text

def split_text_into_chunks(text, max_chars=MAX_CHARS_PER_REQUEST):
    """Split text into chunks of maximum size."""
    # If text is already under the limit, return it as a single chunk
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    # Try to split at sentence boundaries (periods followed by space)
    sentences = text.split('. ')
    current_chunk = ""
    
    for sentence in sentences:
        # Add period back except for the last sentence if it doesn't end with a period
        if sentence != sentences[-1] or text.endswith('.'):
            sentence = sentence + '. '
            
        # If adding this sentence would exceed the limit, start a new chunk
        if len(current_chunk) + len(sentence) > max_chars:
            # If the sentence itself is too long, split it at word boundaries
            if len(sentence) > max_chars:
                words = sentence.split(' ')
                for word in words:
                    if len(current_chunk) + len(word) + 1 > max_chars:  # +1 for space
                        chunks.append(current_chunk.strip())
                        current_chunk = word + ' '
                    else:
                        current_chunk += word + ' '
            else:
                # Finish current chunk and start new one with this sentence
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        else:
            # Add sentence to current chunk
            current_chunk += sentence
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_speech_for_chunk(client, chunk_text, output_file_path, model='tts-1', voice='alloy', max_retries=3, retry_delay=2):
    """Generate speech for a single text chunk."""
    import time
    
    print(f"[DEBUG] Processing chunk with {len(chunk_text)} characters...")
    print(f"[DEBUG] First 100 chars: {chunk_text[:100]}...")
    
    for retry in range(max_retries):
        try:
            print(f"[DEBUG] Attempt {retry + 1}/{max_retries} - Sending request to OpenAI API...")
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=chunk_text
            ) as response:
                try:
                    print(f"[DEBUG] Streaming response to file: {output_file_path}")
                    response.stream_to_file(output_file_path)
                    print(f"[DEBUG] Successfully saved audio to: {output_file_path}")
                    return True
                except IOError as e:
                    print(f"Error writing to file '{output_file_path}': {str(e)}")
                    raise
        except TimeoutError as e:
            if retry < max_retries - 1:
                wait_time = retry_delay * (retry + 1)
                print(f"Request timed out: {str(e)}. Retrying in {wait_time} seconds... (Attempt {retry + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            print(f"Request timed out after {max_retries} attempts: {str(e)}")
            raise
        except ValueError as e:
            if "API key" in str(e):
                print(f"Authentication error: {str(e)}")
            elif "rate limit" in str(e).lower():
                if retry < max_retries - 1:
                    wait_time = retry_delay * (retry + 1)
                    print(f"Rate limit exceeded: {str(e)}. Retrying in {wait_time} seconds... (Attempt {retry + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                print(f"Rate limit exceeded after {max_retries} attempts: {str(e)}")
            else:
                print(f"API error: {str(e)}")
            raise
        except ConnectionError as e:
            if retry < max_retries - 1:
                wait_time = retry_delay * (retry + 1)
                print(f"Connection error: {str(e)}. Retrying in {wait_time} seconds... (Attempt {retry + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            print(f"Connection error after {max_retries} attempts: {str(e)}")
            raise
        except Exception as e:
            if retry < max_retries - 1 and "peer closed connection" in str(e):
                wait_time = retry_delay * (retry + 1)
                print(f"Connection closed unexpectedly: {str(e)}. Retrying in {wait_time} seconds... (Attempt {retry + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            print(f"Unexpected error: {str(e)}")
            raise

def stitch_audio_files(chunk_files, output_file_path):
    """Combine multiple audio files into a single file."""
    if not chunk_files:
        return False
    
    try:
        # If there's only one chunk, just rename it
        if len(chunk_files) == 1:
            os.replace(chunk_files[0], output_file_path)
            return True
        
        # Otherwise, use pydub to combine audio files
        combined = AudioSegment.empty()
        for chunk_file in chunk_files:
            audio_segment = AudioSegment.from_mp3(chunk_file)
            combined += audio_segment
        
        combined.export(output_file_path, format="mp3")
        
        # Clean up temporary chunk files
        for chunk_file in chunk_files:
            try:
                os.remove(chunk_file)
            except:
                pass
        
        return True
    except Exception as e:
        print(f"Error stitching audio files: {str(e)}")
        raise

def calculate_cost(text_length, model='tts-1'):
    """Calculate the estimated cost for generating speech."""
    # Calculate cost based on character count
    cost_per_1k = COST_PER_1K_CHARS.get(model, COST_PER_1K_CHARS['tts-1'])
    estimated_cost = (text_length / 1000) * cost_per_1k
    return estimated_cost

def display_processing_info(text, model):
    """Display processing information and cost estimate to the user."""
    text_length = len(text)
    chunks = split_text_into_chunks(text)
    estimated_cost = calculate_cost(text_length, model)
    
    print(f"\n{Fore.CYAN}====== Text-to-Speech Processing Information ======{Style.RESET_ALL}")
    print(f"Text length: {text_length} characters")
    
    if len(chunks) > 1:
        print(f"Processing required: {len(chunks)} chunks (max {MAX_CHARS_PER_REQUEST} chars per chunk)")
    else:
        print("Processing required: 1 chunk")
    
    print(f"Model: {model}")
    print(f"{Fore.YELLOW}Estimated cost: ${estimated_cost:.4f}{Style.RESET_ALL}")
    
    if len(chunks) > 1:
        print(f"\n{Fore.MAGENTA}Note: The text will be split into {len(chunks)} parts and stitched together.{Style.RESET_ALL}")
    
    return input(f"\n{Fore.GREEN}Do you want to proceed? (y/n): {Style.RESET_ALL}").lower().startswith('y')

def generate_speech(client, input_text, speech_file_path, model='tts-1', voice='alloy'):
    """Generate speech from text and save to file, handling large inputs by splitting and stitching."""
    assert client is not None, "OpenAI client must be initialized"
    assert input_text, "Input text cannot be empty"
    assert speech_file_path, "Speech file path must be specified"
    assert model, "Model name must be specified"
    assert voice, "Voice name must be specified"
    
    # Split text into chunks if needed
    chunks = split_text_into_chunks(input_text)
    
    # If only one chunk, process directly
    if len(chunks) == 1:
        return generate_speech_for_chunk(client, chunks[0], speech_file_path, model, voice)
    
    # For multiple chunks, create temp files and process each chunk
    temp_files = []
    try:
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} characters)...")
            
            # Create a temporary file for this chunk
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)
            
            # Generate speech for this chunk
            success = generate_speech_for_chunk(client, chunk, temp_path, model, voice)
            
            if success:
                temp_files.append(temp_path)
            else:
                raise Exception(f"Failed to generate speech for chunk {i+1}")
        
        # Stitch all the chunks together
        print(f"Stitching {len(temp_files)} audio files together...")
        success = stitch_audio_files(temp_files, speech_file_path)
        
        if success:
            print(f"Speech generated successfully and saved to {speech_file_path}")
            return True
        else:
            raise Exception("Failed to stitch audio files together")
    
    except Exception as e:
        # Clean up any temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
        raise

def main(args=None):
    """Main function to generate speech from text."""
    if args is None:
        parser = argparse.ArgumentParser(description='Generate speech from text file.')
        parser.add_argument('--api-key', help='OpenAI API key')
        parser.add_argument('--input-file', default='input.txt', help='Path to input text file')
        parser.add_argument('--output-file', default='speech.mp3', help='Path to output speech file')
        parser.add_argument('--model', default='tts-1', choices=['tts-1', 'tts-1-hd'], help='TTS model to use')
        parser.add_argument('--voice', default='alloy', choices=SUPPORTED_VOICES, help='Voice to use')
        parser.add_argument('--test', action='store_true', help='Run in test mode')
        parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation prompt')
        args = parser.parse_args()
    
    # Don't need API key in test mode
    if not args.test:
        api_key = get_api_key(args)
        client = OpenAI(api_key=api_key)
    else:
        client = None  # Will be mocked in test mode
    
    # File paths
    speech_file_path = Path(args.output_file)
    input_file_path = Path(args.input_file)
    
    # Read text from input file
    input_text = get_input_text(input_file_path)
    
    # In test mode, return the values
    if args.test:
        return input_text, speech_file_path, args.model, args.voice
    
    # Show processing information and get confirmation unless --force is used
    if not args.force and not display_processing_info(input_text, args.model):
        print("Operation cancelled by user.")
        return False
    
    # Generate speech
    return generate_speech(client, input_text, speech_file_path, args.model, args.voice)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate speech from text file.')
    parser.add_argument('--api-key', help='OpenAI API key')
    parser.add_argument('--input-file', default='input.txt', help='Path to input text file')
    parser.add_argument('--output-file', default='speech.mp3', help='Path to output speech file')
    parser.add_argument('--model', default='tts-1', choices=['tts-1', 'tts-1-hd'], help='TTS model to use')
    parser.add_argument('--voice', default='alloy', choices=SUPPORTED_VOICES, help='Voice to use')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()

    if args.test:
        print("Tests have been moved to the tests directory.")
        print("Run tests with: pytest tests/ or python -m pytest tests/")
        sys.exit(0)
    else:
        try:
            main(args)
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)
