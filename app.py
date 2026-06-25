from flask import Flask, jsonify, render_template
   # Controllers
from controllers.config_controller import config_bp
from controllers.telemetria_controller import telemetria_bp
from controllers.VehicleController import vehicle_bp

def create_app():

    app = Flask(__name__)
    
    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    # HTML
    @app.route("/config")
    def home():
        return render_template("index.html")
    
    
    # No seu app.py, a rota do vehicle precisa agora receber a placa opcionalmente
    @app.route("/vehicle", defaults={'placa': None})
    @app.route("/vehicle/<placa>")
    def vehicle_page(placa):
        return render_template("vehicle.html", placa=placa)


    app.register_blueprint(config_bp)
    app.register_blueprint(telemetria_bp)
    app.register_blueprint(vehicle_bp)

    return app

