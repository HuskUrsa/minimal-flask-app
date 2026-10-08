from flask import Flask, render_template, request, session, jsonify
from openai import OpenAI, OpenAIError
import os, secrets, sqlite3, threading, hmac
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config.update(MAX_CONTENT_LENGTH=20000, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
ORIGINAL_INSTRUCTIONS = 'You are a psychedelic AI that speaks in Oulipian constraints. Your responses are short, surreal, and witty. Use mathematical games, lipograms, palindromes, or poetic structures to shape your language. Avoid predictable phrasing. Let logic slip through the cracks like liquid geometry.'
DEFAULT_INSTRUCTIONS = 'Respond clearly and directly to the user. Follow any requested tone, format, or creative constraint.'
STYLES = {
    'snapshot': 'An unpolished early digital-camera snapshot: direct flash, imperfect framing, muted color, ordinary light. Avoid glossy commercial lighting.',
    'scan': 'A faded photocopied zine image: rough halftone, uneven ink, paper texture, limited tones. No decorative typography.',
    'dream': 'A low-fidelity photograph of an ordinary place made slightly uncanny: soft detail, faded colors, awkward framing, quiet empty space. Avoid cinematic polish.',
    'none': '',
}
# A conservative experiment allowance, shared across visitors and concurrent requests.
# Free Render storage is ephemeral: this resets after a redeploy/restart, not a billing-account limit.
LEDGER = os.getenv('IMAGE_LEDGER_PATH', '/tmp/sam-flask-images.sqlite3')
IMAGE_ALLOWANCE = 5
IMAGE_RESERVE_USD = 0.01
image_lock = threading.Lock()

def reserve_image():
    with sqlite3.connect(LEDGER, timeout=5) as db:
        db.execute('CREATE TABLE IF NOT EXISTS allowance (id INTEGER PRIMARY KEY, used INTEGER NOT NULL)')
        db.execute('INSERT OR IGNORE INTO allowance VALUES (1,0)')
        db.execute('BEGIN IMMEDIATE') if not db.in_transaction else None
        used = db.execute('SELECT used FROM allowance WHERE id=1').fetchone()[0]
        if used >= IMAGE_ALLOWANCE:
            raise ValueError('The five-image experiment allowance is used. No more image calls will be made until the server is restarted.')
        db.execute('UPDATE allowance SET used=used+1 WHERE id=1')

def image_remaining():
    try:
        with sqlite3.connect(LEDGER) as db:
            row = db.execute('SELECT used FROM allowance WHERE id=1').fetchone()
            return max(0, IMAGE_ALLOWANCE-row[0]) if row else IMAGE_ALLOWANCE
    except sqlite3.OperationalError:
        return IMAGE_ALLOWANCE

@app.route('/', methods=['GET','POST'])
def index():
    session.setdefault('csrf', secrets.token_urlsafe(32))
    values = dict(prompt='', instructions=DEFAULT_INSTRUCTIONS, model='gpt-4.1-mini', temperature='1.2', max_tokens='150', image_prompt='', style='snapshot')
    result = image = error = None
    if request.method == 'POST':
        values.update({k:request.form.get(k, v) for k,v in values.items()})
        try:
            if not hmac.compare_digest(request.form.get('csrf',''), session['csrf']):
                raise ValueError('The page expired. Refresh and try again.')
            if not os.getenv('OPENAI_API_KEY'):
                raise ValueError('The server needs its OpenAI API key before it can generate anything.')
            client = OpenAI(timeout=180, max_retries=0)
            if request.form.get('action') == 'image':
                prompt = values['image_prompt'].strip()
                if not prompt or len(prompt)>1200 or values['style'] not in STYLES:
                    raise ValueError('Enter an image prompt of 1 to 1,200 characters and choose a listed style.')
                # Only one pending image per server. Failed calls still consume an attempt.
                if not image_lock.acquire(blocking=False):
                    raise ValueError('An image is already being made. Wait for it to finish.')
                try:
                    reserve_image()
                    response = client.images.generate(model='gpt-image-1-mini', prompt=prompt+'\n'+STYLES[values['style']], quality='low', size='1024x1024', n=1)
                    image = response.data[0].b64_json
                    if not image:
                        raise ValueError('No image came back. Try another prompt if you have attempts remaining.')
                finally:
                    image_lock.release()
            else:
                temperature = float(values['temperature'])
                max_tokens = int(values['max_tokens'])
                if values['model'] not in ('gpt-4.1-mini','gpt-4.1') or not 0<=temperature<=2 or not 50<=max_tokens<=500:
                    raise ValueError('Use a listed model, temperature from 0 to 2, and a response limit from 50 to 500 tokens.')
                if not values['prompt'].strip() or len(values['prompt'])>2000 or len(values['instructions'])>2000:
                    raise ValueError('Enter a prompt; keep each text field below 2,000 characters.')
                response = client.responses.create(model=values['model'], instructions=values['instructions'], input=values['prompt'], temperature=temperature, max_output_tokens=max_tokens, store=False)
                result = response.output_text
                if response.status == 'incomplete':
                    result += '\n[Stopped at the response length limit.]'
        except (ValueError, OverflowError) as exc:
            error = str(exc)
        except OpenAIError:
            error = 'OpenAI could not complete this request. Check model access, credit, or the prompt. No automatic retry was made.'
    if request.method == 'POST' and request.headers.get('Accept') == 'application/json':
        return jsonify(result=result, image=image, error=error, remaining=image_remaining()), (400 if error else 200)
    return render_template('index.html', values=values, result=result, image=image, error=error, original_instructions=ORIGINAL_INSTRUCTIONS, styles=STYLES, remaining=image_remaining(), csrf=session['csrf'])

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False)
