from flask import Blueprint, request, jsonify

from models.TelemetriaModel import TelemetriaModel
from services.TelemetryService import TelemetryService

telemetria_bp = Blueprint(
    "telemetria",
    __name__
)

telemetry_service = TelemetryService()

@telemetria_bp.route('/telemetria', methods=['POST'])
def receber_telemetria():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "JSON vazio"
        }), 400

    model = TelemetriaModel(
        codigo_empresa=data.get("codigo_empresa"),
        placa=data.get("placa"),
        mac_scanner=data.get("mac_scanner", ""),
        mac_rasp=data.get("mac_rasp", ""),
        rpm=data.get("rpm", 0),
        velocidade=data.get("velocidade", 0),
        odometro=data.get("odometro", 0)
    )

    telemetry_service.save_telemetria(model)

    return jsonify({
        "success": True
    })