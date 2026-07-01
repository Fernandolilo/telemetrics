import asyncio
import json
import os
from flask import Flask, jsonify, render_template, request

# Importações dos seus módulos
from controllers.config_controller import config_bp
from controllers.telemetria_controller import telemetria_bp
from controllers.VehicleController import vehicle_bp
from services.BluetoothService import BluetoothService
from utils.perfis_montadoras import PERFIS_MONTADORAS, LeitorOdometroOBD
from services.OBDTelemetry import OBDTelemetry
from services.MonitoringService import MonitoringService

def create_app():
    # Define explicitamente a pasta de templates
    template_dir = os.path.abspath('templates')
    app = Flask(__name__, template_folder=template_dir)

    # --- Rotas Síncronas (Wrapper para lógica assíncrona) ---
    
    bt_service = None

    def get_bt_service():
        global bt_service
        if bt_service is None:
            bt_service = BluetoothService()
        return bt_service

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/config")
    def home():
        return render_template("index.html")

    @app.route("/vehicle", defaults={'placa': None})
    @app.route("/vehicle/<placa>")
    def vehicle_page(placa):
        return render_template("vehicle.html", placa=placa)
    
    @app.route('/scanner')
    def scanner_page():
        return render_template('provision.html')

    @app.route('/api/scanner/connect', methods=['POST'])
    def connect_scanner():
        # Wrapper síncrono para lógica Bluetooth
        async def _connect():
            bt = BluetoothService()
            if await bt.find_and_connect_by_name(["OBDII", "ELM327"]):
                print("Conectado")
                return {"status": "connected", "profiles": list(PERFIS_MONTADORAS.keys())}
                
            return None

        try:
            result = asyncio.run(_connect())
            if result:
                return jsonify(result)
            return jsonify({"status": "error", "message": "Scanner não encontrado"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/scanner/bind', methods=['POST'])
    def bind_vehicle():
        data = request.get_json()
        modelo = data.get('modelo')
        
        async def _bind():
            bt = BluetoothService()
            telemetria = OBDTelemetry(bt)
            leitor = LeitorOdometroOBD(PERFIS_MONTADORAS)
            monitor = MonitoringService(bt, telemetria, leitor)
            await telemetria.start_session()
            asyncio.create_task(monitor.run_monitor(modelo, PERFIS_MONTADORAS[modelo]))
            return True

        asyncio.run(_bind())
        with open('vinculo_atual.json', 'w') as f:
            json.dump({"modelo": modelo, "status": "bound"}, f)
        return jsonify({"status": "success"})

    # Registro de Blueprints
    app.register_blueprint(config_bp)
    app.register_blueprint(telemetria_bp)
    app.register_blueprint(vehicle_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)