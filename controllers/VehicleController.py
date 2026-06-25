from flask import Blueprint, jsonify
from services.VehicleService import VehicleService

vehicle_bp = Blueprint("vehicle", __name__)

service = VehicleService()


@vehicle_bp.route("/api/vehicle/<placa>", methods=["GET"])
def get_vehicle(placa):

    data = service.find_by_placa(placa)

    return jsonify({
        "ok": True,
        "data": data
    })