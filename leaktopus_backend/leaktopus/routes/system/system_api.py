from flask import Blueprint, jsonify, request, abort, current_app

system_api = Blueprint("system_api", __name__)


@system_api.errorhandler(500)
def custom500(error):
    return jsonify(results={"success": False, "message": error.description})


@system_api.route("/up")
def up():
    """Health check endpoint
    ---
    responses:
      200:
        description: Returns the string Healthy when up and running correctly.
    """
    from leaktopus.common.elasticsearch_handler import es
    from leaktopus.extensions import redis

    redis.ping()
    es.ping()

    return "Healthy"


@system_api.route("/api/install", methods=["GET"])
def system_install():
    """API for performing the initial installation of the system.
    ---
    responses:
      200:
        description: Operation result (success).

      500:
        description: Generic error.
    """
    try:
        from leaktopus.common.db_handler import get_db

        get_db()
    except Exception as e:
        print(e)
        abort(500)

    return jsonify(results="success")


@system_api.route("/api/updatedb", methods=["GET"])
def run_updates():
    """Internal API for DB update (after version updates).
    ---
    responses:
      200:
        description: Operation result (success).

      500:
        description: Generic error.
    """
    try:
        from leaktopus.common.db_updates import apply_db_updates

        apply_db_updates(False)
    except Exception as e:
        print(e)
        abort(500)

    return jsonify(results="success")
