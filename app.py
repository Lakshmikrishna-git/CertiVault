from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certivault.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    issuer = db.Column(db.String(200))
    date = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return "CertiVault Backend Running Successfully!"

# Register User
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"], password=data["password"]).first()
    
    if user:
        return jsonify({"message": "Login successful", "user_id": user.id})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Add Certificate
@app.route("/add-certificate", methods=["POST"])
def add_certificate():
    data = request.json
    new_cert = Certificate(
        title=data["title"],
        issuer=data["issuer"],
        date=data["date"],
        user_id=data["user_id"]
    )
    db.session.add(new_cert)
    db.session.commit()
    return jsonify({"message": "Certificate added successfully!"})

# View Certificates
@app.route("/certificates/<int:user_id>", methods=["GET"])
def get_certificates(user_id):
    certs = Certificate.query.filter_by(user_id=user_id).all()
    
    result = []
    for cert in certs:
        result.append({
            "id": cert.id,
            "title": cert.title,
            "issuer": cert.issuer,
            "date": cert.date
        })
    
    return jsonify(result)

# Delete Certificate
@app.route("/delete-certificate/<int:id>", methods=["DELETE"])
def delete_certificate(id):
    cert = Certificate.query.get(id)
    if cert:
        db.session.delete(cert)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"message": "Certificate not found"}), 404

# ------------------ MAIN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
