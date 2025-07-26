from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.schemas.validation import InspectionSchema
from app.models.inspection import Inspection
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import log_request
import re

inspection_bp = Blueprint("inspection", __name__)

# def is_valid_image_url(url):  //improvised using validation schema 
#     return re.match(r".*\.(jpg|jpeg|png)$", url, re.IGNORECASE)

@inspection_bp.route("/inspection", methods=["POST"])
@jwt_required()
def create_inspection():
    log_request(request.path)
    try:
        schema = InspectionSchema()
        data = schema.load(request.json)

        inspection = Inspection(
            vehicle_number=data["vehicle_number"],
            damage_report=data["damage_report"],
            image_url=data["image_url"],
            inspected_by=int(get_jwt_identity())
        )
        db.session.add(inspection)
        db.session.commit()
        return {"message": "Inspection created"}, 201
    
    except ValidationError as ve:
        return {"error": "Validation failed", "messages": ve.messages}, 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Database error", "details": str(e)}, 500
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500

@inspection_bp.route("/inspection/<int:id>", methods=["GET"])
@jwt_required()
def get_inspection(id):
    log_request(request.path)
    try:
        inspection = Inspection.query.get_or_404(id)
        if inspection.inspected_by != int(get_jwt_identity()):
            return {"error": "Forbidden"}, 403
        return {
            "id": inspection.id,
            "vehicle_number": inspection.vehicle_number,
            "status": inspection.status
        }
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500

@inspection_bp.route("/inspection/<int:id>", methods=["PATCH"])
@jwt_required()
def update_status(id):
    log_request(request.path)
    try:
        data = request.json
        if data.get("status") not in ["reviewed", "completed"]:
            return {"error": "Invalid status"}, 400

        inspection = Inspection.query.get_or_404(id)
        if inspection.inspected_by != int(get_jwt_identity()):
            return {"error": "Unauthorized"}, 403

        inspection.status = data["status"]
        db.session.commit()
        return {"message": "Status updated"}

    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500

@inspection_bp.route("/inspection", methods=["GET"])
@jwt_required()
def get_all():
    log_request(request.path)
    try:
        status = request.args.get("status")
        query = Inspection.query.filter_by(inspected_by=int(get_jwt_identity()))
        if status:
            query = query.filter_by(status=status)
        inspections = query.all()
        return jsonify([{
            "id": i.id,
            "vehicle_number": i.vehicle_number,
            "status": i.status
        } for i in inspections])
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500