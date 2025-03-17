import os
import time
import json
import uuid
import humanize
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import TextAreaField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Optional
from openai import OpenAI
from generator import (
    split_text_into_chunks, 
    generate_speech, 
    calculate_cost, 
    SUPPORTED_VOICES,
    combine_audio_files
)
from dotenv import load_dotenv
import PyPDF2
import io
import base64

# Constants
MAX_TEXT_LENGTH = 1000000  # Maximum text length allowed (increased from 25,000)
MAX_UPLOAD_SIZE_MB = 150  # Maximum file upload size in MB (increased from 20MB)
MAX_CHUNK_SIZE = 4000  # Maximum size of text chunks for processing
HISTORY_TEXT_PREVIEW_LENGTH = 1000  # Length of text preview in history and UI displays
COST_PER_CHAR_STANDARD = 0.000015  # Cost per character for standard model
COST_PER_CHAR_HD = 0.000030  # Cost per character for HD model

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes
app.config['HISTORY_FILE'] = os.path.join(app.config['UPLOAD_FOLDER'], 'history.json')
app.config['SESSION_TYPE'] = 'filesystem'  # For larger text that won't fit in URL

# Set up logging
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.debug("Debug logging enabled")

# Ensure the output directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Create history file if it doesn't exist
if not os.path.exists(app.config['HISTORY_FILE']):
    with open(app.config['HISTORY_FILE'], 'w') as f:
        json.dump([], f)

csrf = CSRFProtect(app)

# Create OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class TTSForm(FlaskForm):
    text = TextAreaField('Text to Convert', validators=[
        Optional(),
        Length(max=MAX_TEXT_LENGTH, message=f'Text must be less than {MAX_TEXT_LENGTH:,} characters.')
    ])
    pdf_file = FileField('Or Upload a PDF File')
    voice = SelectField('Voice', choices=[
        ('alloy', 'Alloy'),
        ('echo', 'Echo'),
        ('fable', 'Fable'),
        ('onyx', 'Onyx'),
        ('nova', 'Nova'),
        ('shimmer', 'Shimmer')
    ])
    model = SelectField('Model', choices=[
        ('tts-1', 'Standard (tts-1)'),
        ('tts-1-hd', 'High Definition (tts-1-hd)')
    ])
    submit = SubmitField('Generate Speech')


def save_to_history(text, voice, model, filename, file_size, source_type="Text", original_filename="Direct text input"):
    """Save a generation to the history file"""
    try:
        with open(app.config['HISTORY_FILE'], 'r') as f:
            history = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        history = []
    
    # Add the new entry
    history.append({
        'timestamp': datetime.now().isoformat(),
        'text': text[:HISTORY_TEXT_PREVIEW_LENGTH] + ('...' if len(text) > HISTORY_TEXT_PREVIEW_LENGTH else ''),
        'voice': voice,
        'model': model,
        'filename': filename,
        'file_size': file_size,
        'source_type': source_type,
        'original_filename': original_filename
    })
    
    # Save back to file
    with open(app.config['HISTORY_FILE'], 'w') as f:
        json.dump(history, f)


def get_history():
    """Get the generation history with formatted timestamps"""
    try:
        with open(app.config['HISTORY_FILE'], 'r') as f:
            history = json.load(f)
            
        for item in history:
            # Convert ISO format timestamp to datetime object
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
            # Add formatted file size
            item['file_size_formatted'] = humanize.naturalsize(item['file_size'])
        
        # Sort by timestamp, newest first
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return history
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def remove_from_history(filename):
    """Remove an entry from the history file"""
    try:
        with open(app.config['HISTORY_FILE'], 'r') as f:
            history = json.load(f)
        
        # Filter out the entry with the given filename
        history = [item for item in history if item['filename'] != filename]
        
        with open(app.config['HISTORY_FILE'], 'w') as f:
            json.dump(history, f)
        
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False


def clear_all_history():
    """Remove all entries from the history file and delete all audio files"""
    try:
        # Get the current history to find files to delete
        with open(app.config['HISTORY_FILE'], 'r') as f:
            history = json.load(f)
        
        # Delete all audio files from the output directory
        for item in history:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], item['filename'])
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Clear the history file
        with open(app.config['HISTORY_FILE'], 'w') as f:
            json.dump([], f)
        
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        # Create an empty history file if it doesn't exist
        with open(app.config['HISTORY_FILE'], 'w') as f:
            json.dump([], f)
        return True


@app.template_filter('now')
def _now(format_='%Y'):
    """Return the current year or other formatted date"""
    return datetime.now().strftime(format_)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TTSForm()
    
    if form.validate_on_submit():
        voice = form.voice.data
        model = form.model.data
        
        # Extract text either from form input or PDF file
        text = form.text.data or ""
        pdf_file = request.files.get('pdf_file')
        
        # If both text and PDF are empty, show an error
        if not text and not pdf_file:
            flash("Please provide either text or upload a PDF file", "danger")
            return redirect(url_for('index'))
        
        # If PDF file is provided, extract text from it
        if pdf_file and pdf_file.filename:
            try:
                pdf_text = extract_text_from_pdf(pdf_file)
                # If form text is empty, use the PDF text
                if not text:
                    text = pdf_text
                # If both are provided, append PDF text to form text
                else:
                    text += "\n\n" + pdf_text
            except Exception as e:
                flash(f"Error processing PDF: {str(e)}", "danger")
                return redirect(url_for('index'))
        
        # Check if we have valid text after processing
        if not text:
            flash("No text could be extracted from the provided sources", "danger")
            return redirect(url_for('index'))
            
        # Check text length
        if len(text) > MAX_TEXT_LENGTH:
            flash(f"Text is too long. Maximum is {MAX_TEXT_LENGTH:,} characters.", "danger")
            return redirect(url_for('index'))
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        start_time = time.time()
        try:
            # Process text and generate audio
            if len(text) <= MAX_CHUNK_SIZE:
                # Single chunk processing for short text
                generate_speech(text, output_path, voice=voice, model=model)
                num_chunks = 1
            else:
                # Multi-chunk processing for longer text
                # Split text into chunks
                chunks = [text[i:i+MAX_CHUNK_SIZE] for i in range(0, len(text), MAX_CHUNK_SIZE)]
                num_chunks = len(chunks)
                
                # Generate temporary audio files for each chunk
                temp_files = []
                for i, chunk in enumerate(chunks):
                    temp_filename = f"temp_{uuid.uuid4()}.mp3"
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
                    generate_speech(chunk, temp_path, voice=voice, model=model)
                    temp_files.append(temp_path)
                
                # Combine audio files
                combine_audio_files(temp_files, output_path)
                
                # Clean up temporary files
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            # Save to history
            source_type = "PDF" if pdf_file and pdf_file.filename else "Text"
            original_filename = pdf_file.filename if pdf_file and pdf_file.filename else "Direct text input"
            
            save_to_history(text, voice, model, filename, file_size, source_type=source_type, original_filename=original_filename)
            
            # Store the text in session for cases where it's too long for URL
            session['last_generated_text'] = text
            session['last_generated_filename'] = filename
            
            # Redirect to result page - now including text parameter
            return redirect(url_for('result', 
                                   filename=filename, 
                                   voice=voice, 
                                   model=model, 
                                   text=text,  # Add text to URL params
                                   text_length=len(text),
                                   num_chunks=num_chunks,
                                   source_type=source_type,
                                   original_filename=original_filename,
                                   processing_time=f"{processing_time:.2f} seconds"))
            
        except Exception as e:
            flash(f"Error generating speech: {str(e)}", "danger")
            return redirect(url_for('index'))
    
    return render_template('index.html', form=form)


@app.route('/result')
def result():
    filename = request.args.get('filename')
    voice = request.args.get('voice')
    model = request.args.get('model')
    source_type = request.args.get('source_type', 'Text')
    original_filename = request.args.get('original_filename', 'Direct text input')
    show_success = request.args.get('show_success', 'true').lower() != 'false'  # Default to true
    
    # Try to get text from URL params first, then fallback to session if URL param is empty
    text = request.args.get('text', '')
    if not text and 'last_generated_text' in session:
        text = session.get('last_generated_text', '')
        app.logger.info(f"Retrieved full text from session, length: {len(text)} characters")
        # Clear from session after use to save space
        session.pop('last_generated_text', None)
    
    # If still no text, try to get from history
    if not text:
        history_data = get_history()
        for item in history_data:
            if item['filename'] == filename:
                history_text = item['text']
                app.logger.info(f"Found history entry for {filename}")
                
                # Check if history text is truncated by looking for trailing "..."
                if history_text.endswith('...'):
                    app.logger.warning(f"Text for {filename} from history is truncated! " +
                                   f"Only found {len(history_text)} characters in history.")
                
                text = history_text
                break
    
    text_length = request.args.get('text_length', '0')
    num_chunks = request.args.get('num_chunks', '1')
    processing_time = request.args.get('processing_time', '0 seconds')
    
    # Get file size
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    file_size_formatted = humanize.naturalsize(file_size)
    
    # Log if text is still empty for debugging
    if not text:
        app.logger.error(f"Text is still empty for result page with filename {filename}")
    else:
        app.logger.info(f"Text for result page has {len(text)} characters")
    
    return render_template('result.html', 
                          filename=filename,
                          voice=voice,
                          model=model,
                          text=text,
                          text_length=text_length,
                          num_chunks=num_chunks,
                          processing_time=processing_time,
                          file_size_formatted=file_size_formatted,
                          source_type=source_type,
                          original_filename=original_filename,
                          show_success=show_success)


@app.route('/history')
def history():
    """Display generation history"""
    history_data = get_history()
    return render_template('history.html', history=history_data)


@app.route('/preview', methods=['POST'])
def preview():
    """Calculate and return a cost/resource preview"""
    text = request.form.get('text', '')
    model = request.form.get('model', 'tts-1')
    
    # Check if a PDF file was uploaded
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        
        # Check if it's a valid file with a filename
        if pdf_file and pdf_file.filename:
            # Check if it's a PDF file
            if pdf_file.filename.lower().endswith('.pdf'):
                try:
                    # Extract text from the PDF
                    pdf_text = extract_text_from_pdf(pdf_file)
                    
                    # Combine with any text input
                    if text:
                        text += "\n\n" + pdf_text
                    else:
                        text = pdf_text
                except Exception as e:
                    return jsonify({'error': f'Error processing PDF: {str(e)}'})
    
    # If there's no text after processing, return an error
    if not text:
        return jsonify({'error': 'No text provided'})
    
    text_length = len(text)
    num_chunks = (text_length // MAX_CHUNK_SIZE) + (1 if text_length % MAX_CHUNK_SIZE > 0 else 0)
    
    # Calculate approximate cost
    cost_per_char = COST_PER_CHAR_STANDARD if model == 'tts-1' else COST_PER_CHAR_HD
    cost = text_length * cost_per_char
    
    return jsonify({
        'text_length': text_length,
        'num_chunks': num_chunks,
        'cost': cost
    })


@app.route('/get-audio/<filename>')
def get_audio(filename):
    """Stream audio file to the browser"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, mimetype='audio/mpeg', as_attachment=False)


@app.route('/download/<filename>')
def download_audio(filename):
    """Download audio file"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, mimetype='audio/mpeg', as_attachment=True)


@app.route('/delete/<filename>')
def delete_audio(filename):
    """Delete an audio file and its history entry"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from history
        remove_from_history(filename)
        
        flash("Audio file deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting file: {str(e)}", "danger")
    
    return redirect(url_for('history'))


@app.route('/delete-all')
def delete_all_audio():
    """Delete all audio files and clear history"""
    try:
        if clear_all_history():
            flash("All audio files deleted successfully", "success")
        else:
            flash("Error clearing history", "danger")
    except Exception as e:
        flash(f"Error deleting files: {str(e)}", "danger")
    
    return redirect(url_for('history'))


# API endpoints for testing
@app.route('/api/health')
def api_health():
    """Health check endpoint for testing"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route('/api/preview-cost', methods=['POST'])
def api_preview_cost():
    """API endpoint for cost preview"""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
    
    text = data.get('text', '')
    model = data.get('model', 'tts-1')
    
    text_length = len(text)
    estimated_cost = calculate_cost(text_length, model)
    
    return jsonify({
        "text_length": text_length,
        "estimated_cost": estimated_cost,
        "model": model
    })


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint for generating speech"""
    # For JSON data
    if request.is_json:
        data = request.json
        if not data or ('text' not in data and 'pdf_base64' not in data):
            return jsonify({"error": "Either text or PDF data is required"}), 400
        
        # Extract text from PDF if provided
        if 'pdf_base64' in data and data['pdf_base64']:
            try:
                # Decode base64 PDF data
                pdf_data = base64.b64decode(data['pdf_base64'])
                pdf_file = io.BytesIO(pdf_data)
                
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(pdf_file)
                
                # Use extracted text or append to provided text
                if 'text' in data and data['text']:
                    text = data['text'] + "\n\n" + pdf_text
                else:
                    text = pdf_text
                    
                source_type = "PDF"
                original_filename = data.get('filename', 'API PDF upload')
            except Exception as e:
                return jsonify({"error": f"Error processing PDF: {str(e)}"}), 400
        else:
            text = data.get('text', '')
            source_type = "Text"
            original_filename = "API text input"
    # For multipart form data
    else:
        text = request.form.get('text', '')
        pdf_file = request.files.get('pdf_file')
        
        # Extract text from PDF if provided
        if pdf_file and pdf_file.filename:
            try:
                pdf_text = extract_text_from_pdf(pdf_file)
                
                # Use extracted text or append to provided text
                if text:
                    text = text + "\n\n" + pdf_text
                else:
                    text = pdf_text
                    
                source_type = "PDF"
                original_filename = pdf_file.filename
            except Exception as e:
                return jsonify({"error": f"Error processing PDF: {str(e)}"}), 400
        else:
            source_type = "Text"
            original_filename = "API text input"
    
    # Validate final text
    if not text:
        return jsonify({"error": "No text could be extracted from the provided sources"}), 400
    
    # Get other parameters
    voice = request.json.get('voice', 'alloy') if request.is_json else request.form.get('voice', 'alloy')
    model = request.json.get('model', 'tts-1') if request.is_json else request.form.get('model', 'tts-1')
    
    # Generate a unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp3"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Generate the speech
        generate_speech(text, output_path, voice=voice, model=model, client=client)
        file_size = os.path.getsize(output_path)
        save_to_history(text, voice, model, filename, file_size, source_type=source_type, original_filename=original_filename)
        
        return jsonify({
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "text_length": len(text),
            "source_type": source_type,
            "original_filename": original_filename,
            "url": url_for('get_audio', filename=filename, _external=True)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history')
def api_history():
    """API endpoint for getting generation history"""
    history_data = get_history()
    # Convert datetime objects to ISO format for JSON serialization
    for item in history_data:
        if isinstance(item['timestamp'], datetime):
            item['timestamp'] = item['timestamp'].isoformat()
        # Add file_id from filename
        if 'filename' in item:
            item['file_id'] = os.path.splitext(item['filename'])[0]
    
    return jsonify(history_data)


@app.route('/api/check-environment')
def api_check_environment():
    """API endpoint to check if environment variables are set"""
    return jsonify({
        "openai_api_key_set": bool(os.environ.get('OPENAI_API_KEY')),
        "secret_key_set": bool(os.environ.get('SECRET_KEY')),
        "docker_env": bool(os.environ.get('DOCKER_ENV'))
    })


@app.route('/generate-voice-samples')
def generate_voice_samples():
    """Generate sample audio files for each available voice"""
    # Only admin or developers should be able to access this route
    if not os.environ.get('ALLOW_SAMPLE_GENERATION') == 'true':
        flash('Sample generation is disabled.', 'danger')
        return redirect(url_for('index'))
    
    # Voice-specific introduction messages
    voice_intros = {
        "alloy": "Hello, I'm Alloy. I'm a versatile, general-purpose voice that's great for explanations, presentations, and everyday content.",
        "echo": "Hi there, I'm Echo. My smooth, natural delivery is perfect for narration, storytelling, and educational material.",
        "fable": "Greetings, I'm Fable. My authoritative tone is ideal for documentaries, podcasts, and more formal content.",
        "onyx": "Hello, I'm Onyx. My deep, engaging voice works well for announcements, marketing, and professional presentations.",
        "nova": "Hi, I'm Nova. My warm, pleasant tone is great for friendly content, customer service, and approachable narratives.",
        "shimmer": "Hello, I'm Shimmer. My clear, articulate delivery is excellent for instructional content, tutorials, and detailed explanations."
    }
    
    samples_dir = os.path.join(app.static_folder, 'audio', 'samples')
    os.makedirs(samples_dir, exist_ok=True)
    
    generated_samples = []
    
    for voice in SUPPORTED_VOICES:
        output_path = os.path.join(samples_dir, f"{voice}.mp3")
        # Always regenerate to ensure the latest introduction is used
        try:
            intro_text = voice_intros.get(voice, f"Hello, I'm the {voice} voice.")
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=intro_text
            )
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            generated_samples.append(f"{voice}.mp3 (generated)")
            app.logger.info(f"Generated sample for {voice}")
        except Exception as e:
            app.logger.error(f"Error generating sample for {voice}: {str(e)}")
            generated_samples.append(f"{voice}.mp3 (error: {str(e)})")
    
    return render_template(
        'result.html', 
        title='Voice Samples Generated', 
        text="Voice samples generated successfully.", 
        files=generated_samples
    )


def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file"""
    text = ""
    try:
        # If pdf_file is a tuple (from a test), extract the BytesIO object
        if isinstance(pdf_file, tuple):
            pdf_file = pdf_file[0]
        
        # Use PyPDF2 to read the PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:  # Only add if text was extracted
                text += page_text + "\n\n"
        
        return text.strip()
    except Exception as e:
        app.logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


@app.route('/download-text/<filename>')
def download_text(filename):
    """Download the input text as a txt file"""
    try:
        # First, try to get text from session if it's a recent generation
        original_text = None
        title = "text"
        is_truncated = False
        
        if 'last_generated_text' in session and session.get('last_generated_filename') == filename:
            original_text = session.get('last_generated_text')
            app.logger.info(f"Found text in session for {filename}, length: {len(original_text)} chars")
        
        # If not found in session, try to get from history
        if not original_text:
            history_data = get_history()
            for item in history_data:
                if item['filename'] == filename:
                    # Try to use the text from history (may be truncated)
                    history_text = item['text']
                    if history_text.endswith('...'):
                        app.logger.warning(f"Text for {filename} from history is truncated")
                        original_text = history_text
                        is_truncated = True
                    else:
                        app.logger.info(f"Found text in history for {filename}, text length: {len(history_text)}")
                        original_text = history_text
                    
                    title = item.get('original_filename', 'text').replace(' ', '_')
                    if title.lower().endswith('.pdf'):
                        title = title[:-4]
                    break
        
        if not original_text:
            app.logger.error(f"Text not found for {filename} in session or history")
            flash("Text not found", "danger")
            return redirect(url_for('history'))
        
        # Add a note if the text is truncated
        if is_truncated:
            download_text = f"Note: This text is truncated to {HISTORY_TEXT_PREVIEW_LENGTH} characters as the full original text was not saved.\n\n{original_text}"
        else:
            download_text = original_text
            
        app.logger.info(f"Preparing text download for {filename}, text length: {len(download_text)} chars")
        
        # Create a BytesIO object to store the text
        text_file = io.BytesIO(download_text.encode('utf-8'))
        text_file.seek(0)
        
        # Generate a filename for the text file
        text_filename = f"{title}_{filename.split('.')[0]}.txt"
        
        return send_file(text_file, mimetype='text/plain', as_attachment=True, download_name=text_filename)
    except Exception as e:
        app.logger.error(f"Error downloading text for {filename}: {str(e)}")
        flash(f"Error downloading text: {str(e)}", "danger")
        return redirect(url_for('history'))


@app.context_processor
def inject_constants():
    """Make constants available to all templates"""
    return {
        'MAX_TEXT_LENGTH': MAX_TEXT_LENGTH,
        'MAX_UPLOAD_SIZE_MB': MAX_UPLOAD_SIZE_MB,
        'HISTORY_TEXT_PREVIEW_LENGTH': HISTORY_TEXT_PREVIEW_LENGTH,
    }


if __name__ == '__main__':
    # Listen on all interfaces in Docker, but only localhost in development
    host = '0.0.0.0' if os.environ.get('DOCKER_ENV') else '127.0.0.1'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host=host, port=port) 