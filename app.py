from flask import Flask, request, jsonify, abort
from utils import generate_random_string
from background import process_pdf_in_background
import threading
import traceback
# Import our MongoDB service
from send_email import send_via_smtp
from mongodb_service import MongoDBService

app = Flask(__name__)
mongo_service = MongoDBService()

@app.route("/")
def home():
    return "Hello, Flask is working!", 200

@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Get analysis_id from form data
        analysis_id = request.form.get('analysis_id')
        if not analysis_id:
            return jsonify({'error': 'No analysis ID provided'}), 400
        
        region = request.form.get('region')
        if not region:
            return jsonify({'error': 'No region provided'}), 400
        
        specialty = request.form.get('specialty')
        if not specialty:
            return jsonify({'error': 'No specialty provided'}), 400
        
        # Save the PDF
        temp_pdf_path = f"temp_{generate_random_string()}.pdf"
        pdf_file.save(temp_pdf_path)
        
        # Start background processing thread
        thread = threading.Thread(
            target=process_pdf_in_background,
            args=(temp_pdf_path, analysis_id, region, specialty)
        )
        thread.daemon = True  # Allow the main program to exit even if thread is running
        thread.start()
        
        # Return immediately
        return jsonify({
            'status': 'processing',
            'message': 'PDF processing started in background',
            'analysis_id': analysis_id
        })
    
    except Exception as e:
        # Log the full error with traceback
        print(f"Error initiating PDF processing: {e}")
        traceback.print_exc()
            
        return jsonify({'error': str(e)}), 500


@app.route("/send-register", methods=["POST"])
def send_register():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        token = data.get("token")
        NEXTAUTH_URL = "https://oposconia.com"
        if not email or not token:
            abort(400, "Missing email or token")

        verify_url = f"{NEXTAUTH_URL}/api/verify-email?token={token}"
        subject    = "Verifica tu correo electrónico"
        body_plain = f"Visita {verify_url} para verificar tu correo (expira en 24h)."
        body_html  = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
            <h2>Verifica tu correo electrónico</h2>
            <p>Gracias por registrarte. Haz clic en el botón para verificar tu correo:</p>
            <p style="text-align:center;margin:30px 0;">
            <a href="{verify_url}" style="background-color:#4CAF50;color:#fff;
                padding:12px 20px;text-decoration:none;border-radius:4px;font-weight:bold;">
                Verificar correo
            </a>
            </p>
            <p>Si no lo solicitaste, ignora este correo. Expira en 24h.</p>
        </div>"""

        send_via_smtp(email, subject, body_plain, body_html)
        return jsonify(status="ok"), 200
    except Exception as e:
        # Log the full error with traceback
        # print(f"Error sending register email: {e}")
        # traceback.print_exc()
        
        return jsonify({'error': str(e)}), 500

@app.route("/send-waitlist", methods=["POST"])
def send_waitlist():
    try:
        data = request.get_json() or {}
        email     = data.get("email")
        region    = data.get("region")
        specialty = data.get("specialty")
        ADMIN_EMAIL = "info@oposconia.com"
        if not all([email, region, specialty]):
            abort(400, "Missing email, region, or specialty")

        subject    = "Nuevo usuario en la lista de espera"
        body_plain = f"Email: {email}\nRegión: {region}\nEspecialidad: {specialty}"
        body_html  = f"""
        <div style="font-family:Arial,sans-serif;">
            <h2>Nuevo usuario en la lista de espera</h2>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Comunidad Autónoma:</strong> {region}</p>
            <p><strong>Especialidad:</strong> {specialty}</p>
        </div>"""

        send_via_smtp(ADMIN_EMAIL, subject, body_plain, body_html)
        return jsonify(status="ok"), 200
    except Exception as e:
        # Log the full error with traceback
        # print(f"Error sending waitlist email: {e}")
        # traceback.print_exc()
        
        return jsonify({'error': str(e)}), 500

@app.route("/send-reset", methods=["POST"])
def send_reset():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        token = data.get("token")
        NEXTAUTH_URL = "https://oposconia.com"
        if not email or not token:
            abort(400, "Missing email or token")

        reset_url  = f"{NEXTAUTH_URL}/auth/reset-password?token={token}"
        subject    = "Recuperación de contraseña - OPOSconIA"
        body_plain = f"Restablece tu contraseña aquí: {reset_url} (expira en 1h)."
        body_html  = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Recuperación de contraseña</h2>
            <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
            <p style="margin:20px 0;">
            <a href="{reset_url}" style="background-color:#22c55e;color:#fff;
                padding:10px 15px;text-decoration:none;border-radius:4px;display:inline-block;">
                Restablecer contraseña
            </a>
            </p>
            <p>Si no lo solicitaste, ignora este mensaje. Expira en 1 hora.</p>
            <p>Saludos,<br>El equipo de OPOSconIA</p>
        </div>"""

        send_via_smtp(email, subject, body_plain, body_html)
        return jsonify(status="ok"), 200
    except Exception as e:
        # Log the full error with traceback
        # print(f"Error sending reset email: {e}")
        # traceback.print_exc()
        
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok'})

@app.teardown_appcontext
def teardown_db(exception=None):
    """Close MongoDB connection when app context ends"""
    print('CLOSING MONGO CONN')
    mongo_service.close_connection()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)