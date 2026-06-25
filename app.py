from flask import Flask, jsonify, render_template, request
   # Controllers
from controllers.config_controller import config_bp
from controllers.telemetria_controller import telemetria_bp
from controllers.VehicleController import vehicle_bp
from services.BluetoothService import BluetoothService
from utils.perfis_montadoras import PERFIS_MONTADORAS, LeitorOdometroOBD
from services.OBDTelemetry import OBDTelemetry
from services.MonitoringService import MonitoringService

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
    
    @app.route('/scanner')
    def scanner_page():
        return render_template('provision.html') # Certifique-se de que o arquivo esteja na pasta /templates


    @app.route('/api/scanner/bind', methods=['POST'])
    async def bind_vehicle():
        global bt
        data = request.get_json()
        modelo = data.get('modelo')
        
        # --- Sua lógica preservada ---
        telemetria = OBDTelemetry(bt)
        leitor = LeitorOdometroOBD(PERFIS_MONTADORAS)
        monitor = MonitoringService(bt, telemetria, leitor)
        
        # Inicia a sessão e o monitoramento em background
        await telemetria.start_session()
        
        # IMPORTANTE: Usamos o asyncio para não bloquear o servidor Flask
        asyncio.create_task(monitor.run_monitor(modelo, PERFIS_MONTADORAS[modelo]))
        
        # Salva o vínculo para o sistema saber que já está configurado
        with open('vinculo_atual.json', 'w') as f:
            json.dump({"modelo": modelo, "status": "bound"}, f)
        
        return jsonify({"status": "success"})

    # Rota para conectar e retornar a lista de perfis
    @app.route('/api/scanner/connect', methods=['POST'])
    async def connect_scanner():
        global bt
        try:
            bt = BluetoothService()
            print("Buscando scanner...")
            # Tenta conectar
            if await bt.find_and_connect_by_name(["OBDII", "ELM327"]):
                # Retorna a lista de perfis assim que conectar
                return jsonify({
                    "status": "connected",
                    "profiles": list(PERFIS_MONTADORAS.keys())
                })
            return jsonify({"status": "error", "message": "Scanner não encontrado"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500



    app.register_blueprint(config_bp)
    app.register_blueprint(telemetria_bp)
    app.register_blueprint(vehicle_bp)

    return app

