from flask import Blueprint, jsonify, request, abort, current_app
import leaktopus.common.db_handler as dbh
from leaktopus.domain.leak.usecases.get_leak_by_id_use_case import GetLeakByIdUseCase
from leaktopus.factory import create_leak_service, create_secret_service, create_domain_service, \
    create_contributor_service, create_sensitive_keyword_service

leaks_api = Blueprint('leaks_api', __name__)


@leaks_api.errorhandler(500)
def custom500(error):
    return jsonify(results={"success": False, "message": error.description})


@leaks_api.route("/api/secrets", methods=['GET'])
def secrets_scan():
    """API For scanning a repo for secrets (async).
    ---
    deprecated: true
    parameters:
      - name: repo
        in: query
        type: string
        required: true
    responses:
      200:
        description: Scan initialization confirmation (without the scan data).
        examples:
          {"results": {"message": "Scanning, results will be available soon.","success": true}}

      422:
        description: repo is missing.
    """
    repo = request.args.get('repo')
    if not repo:
        abort(422)

    # Scan (in an async way with Celery)
    # @todo make it work.
    # from leaktopus.common.secrets_scanner import secrets_scanner
    # secrets_scanner.delay([repo])
    #
    # results = {
    #     "success": True,
    #     "message": "Scanning, results will be available soon."
    # }
    results = {
        "success": False,
        "message": "Function not yet supported."
    }

    return jsonify(results=results)


@leaks_api.route("/api/leak/<int:id>", methods=['GET'])
def get_leak_by_id(id):
    """API For getting a specific leak by its id.
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true

    responses:
      200:
        description: The leak data.
    """
    leak_service = create_leak_service()
    secret_service = create_secret_service()
    domain_service = create_domain_service()
    contributor_service = create_contributor_service()
    sensitive_keyword_service = create_sensitive_keyword_service()

    use_case = GetLeakByIdUseCase(
        leak_service,
        secret_service,
        domain_service,
        contributor_service,
        sensitive_keyword_service
    )
    leak = use_case.execute(int(id))

    return jsonify({
        "success": True,
        "count": 1 if leak else 0,
        "data": [leak]
    })


@leaks_api.route("/api/leak/<int:id>", methods=['PATCH'])
def update_leak(id):
    """API For updating a leak.
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: acknowledged
        in: body
        type: Boolean
        required: false
    responses:
      200:
        description: Operation result (success).

      500:
        description: Generic error.
    """
    content = request.get_json(silent=True)

    if "acknowledged" in content:
        try:
            dbh.update_leak(int(id), acknowledged=bool(content["acknowledged"]))
        except Exception:
            # Throw error 500.
            abort(500)

    return jsonify(results='success')


@leaks_api.route("/api/leak", methods=['GET'])
def fetch_leaks():
    """API For getting all leaks.
    ---
    parameters:
      - name: q
        in: query
        type: string
        required: false
      - name: created_at
        in: query
        type: string
        required: false
        description: "Currently supports only greater than datetime. Date time format: YYYY-MM-DD%20HH:MM:SS"
    responses:
      200:
        description: The leaks data.
    """
    # Supported filters (query params).
    FILTERS = [
        'created_at'
    ]

    active_filters = {
        "acknowledged": False
    }

    # Add query if given.
    # @todo Add limits and pagination to protect from DOS.
    q = request.args.get('q')
    if q:
        active_filters["search_query"] = q

    for f in FILTERS:
        fval = request.args.get(f)
        if fval:
            active_filters[f] = fval

    import leaktopus.common.leak_handler as leak_handler
    results = leak_handler.fetch_leaks_from_db(active_filters)

    return jsonify(results=results)

