from flask import jsonify


def success(data=None, message="Success", status=200, meta=None):
    body = {"success": True, "message": message, "data": data}
    if meta:
        body["meta"] = meta
    return jsonify(body), status


def created(data=None, message="Created successfully"):
    return success(data, message, 201)


def error(message="Error", status=400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status


def not_found(message="Resource not found"):
    return error(message, 404)


def unauthorized(message="Unauthorized. Please log in."):
    return error(message, 401)


def forbidden(message="Access denied. Insufficient permissions."):
    return error(message, 403)


def server_error(message="Internal server error"):
    return error(message, 500)
