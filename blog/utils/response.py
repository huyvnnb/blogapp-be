from flask import jsonify
from pydantic import BaseModel


def success(data=None, message="OK", status=200):
    if isinstance(data, BaseModel):
        data = data.model_dump(exclude_none=True)
    elif isinstance(data, list):
        data = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]

    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status


def error(message="Error", status=400, data=None):
    return jsonify({
        "success": False,
        "message": message,
        "data": data
    }), status
