from flask import Blueprint, request, jsonify
from services.TelemetryService import TelemetryService

config_bp = Blueprint("config", __name__)

service = TelemetryService()

@config_bp.route("/api/config", methods=["POST"])
def config():

    data = request.get_json()

    saved = service.save_config({
        "codigo_empresa": data.get("codigo_empresa"),
        "placa": data.get("placa"),
        "device_id": data.get("device_id")
    })

    return jsonify({
        "ok": True,
        "data": saved
    })