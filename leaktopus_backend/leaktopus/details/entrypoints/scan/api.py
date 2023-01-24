from flask import Blueprint, jsonify, request, abort, current_app
from loguru import logger

scans_api = Blueprint("scans_api", __name__)


@scans_api.errorhandler(500)
def custom500(error):
    logger.error("Error in scans API - {}", error)
    return jsonify(results={"success": False, "message": error.description})


@scans_api.route("/api/scan", methods=["GET"])
def start_scan():
    """API For scanning for leaks (async).
    ---
    parameters:
      - name: q
        in: query
        type: string
        required: true
    responses:
      200:
        description: Scan information.

      422:
        description: Search query is missing.

      500:
        description: Generic error.
    """
    q = request.args.get("q")
    if not q:
        abort(422)

    import leaktopus.common.scanner_async as scanner
    import leaktopus.common.scans as scans

    try:
        # Scan (in an async way with Celery)
        scan_id = scanner.scan(q)

        # Get the new scan's information.

        scan = scans.get_scans(scan_id=scan_id)
    except Exception as e:
        abort(500)

    return jsonify(results=scan)


def is_valid_sensitive_keywords(sensitive_keywords):
    blacklisted_characters = r';&|"`\\!<>$'

    for keyword in sensitive_keywords:
        if any(elem in blacklisted_characters for elem in keyword):
            return False

    return True


@scans_api.route("/api/scan", methods=["POST"])
def start_scan_extended():
    """API For scanning for leaks (async).
    ---
    parameters:
      - name: q
        in: body
        type: string
        required: true
      - name: enhancement_modules
        in: body
        description: List of enhancement modules to use for the scan.

            Sending an empty array will disable all modules.

            Not sending the parameter will enable all modules.
        schema:
            type: array
            items:
              type: string
              enum:
                - domains
                - sensitive_keywords
                - contributors
                - secrets
              examples:
                - domains
                - sensitive_keywords
                - contributors
                - secrets
        required: false
      - name: organization_domains
        in: body
        schema:
            type: array
            items:
              type: string
        required: false
      - name: sensitive_keywords
        in: body
        schema:
            type: array
            items:
              type: string
        required: false
    responses:
      200:
        description: Scan information.

      422:
        description: Search query is missing.

      500:
        description: Generic error.
    """
    content = request.get_json(silent=True)

    if not content or not content["q"]:
        abort(422)

    # Get the organization domains from the request body.
    org_domains = []
    if "organization_domains" in content:
        org_domains = content["organization_domains"]

    # Get the sensitive keywords from the request body.
    sensitive_keywords = []
    if "sensitive_keywords" in content:
        if not is_valid_sensitive_keywords(content["sensitive_keywords"]):
            return jsonify(
                results={
                    "success": False,
                    "error": "blacklisted characters in sensitive_keywords",
                }
            )

        sensitive_keywords = content["sensitive_keywords"]

    if "enhancement_modules" in content:
        enhancement_modules = content["enhancement_modules"]
    else:
        # Use the default enhancement modules if the parameter is not sent.
        from leaktopus.common.leak_enhancer import get_enhancement_modules

        enhancement_modules = get_enhancement_modules()

    # Scan (in an async way with Celery)
    import leaktopus.common.scanner_async as scanner

    scan_id = scanner.scan(
        content["q"], org_domains, sensitive_keywords, enhancement_modules
    )

    # Get the new scan's information.
    try:
        import leaktopus.common.scans as scans

        scan = scans.get_scans(scan_id=scan_id)
    except Exception as e:
        abort(500)

    return jsonify(results=scan)


@scans_api.route("/api/scans", methods=["GET"])
def get_scans():
    """API For getting all scans.
    ---
    responses:
      200:
        description: Scans data.
    """
    scans = None
    try:
        import leaktopus.common.scans as scans

        # @todo Add limits and pagination.
        scans = scans.get_scans()

    except Exception as e:
        abort(500)

    return jsonify(results=scans)


@scans_api.route("/api/scan/<int:id>", methods=["GET"])
def get_scan_status(id):
    """API For getting a scan.
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scan data (e.g., status).
    """
    scan = None
    try:
        import leaktopus.common.scans as scans

        scan = scans.get_scans(scan_id=int(id))

    except Exception as e:
        abort(500)

    return jsonify(results=scan)


@scans_api.route("/api/scan/<int:id>/abort", methods=["GET"])
def abort_scan(id):
    """API For aborting a scan.
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scan information.
      500:
        description: Generic error.
    """
    scan = None

    try:
        import leaktopus.common.scans as scans
        from leaktopus.models.scan_status import ScanStatus

        scans.update_scan_status(int(id), ScanStatus.SCAN_ABORTING)
        # The async tasks should abort once the scan status is "Aborting".

        scan = scans.get_scans(scan_id=int(id))

    except Exception as e:
        abort(500)

    return jsonify(results=scan)


@scans_api.route("/api/scan/<int:id>/kill", methods=["GET"])
def kill_scan(id):
    """API For killing a scan (UNGRACEFULLY), should only be used on rare cases.
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scan information.
      500:
        description: Generic error.
    """
    scan = None

    try:
        import leaktopus.common.scans as scans
        from leaktopus.models.scan_status import ScanStatus

        scans.update_scan_status(int(id), ScanStatus.SCAN_ABORTED)
        scan = scans.get_scans(scan_id=int(id))

    except Exception as e:
        abort(500)

    return jsonify(results=scan)


@scans_api.route("/api/repo/enhance", methods=["POST"])
def enhance_repo():
    """API For enhancing a repository known to Leaktopus (async).
    ---
    parameters:
      - name: repo_name
        in: body
        type: string
        description: Name of the repository - "OWNER/REPO". Use only repositories already known to Leaktopus (leaks).
        example: PlaytikaOSS/Leaktopus
        required: true
      - name: enhancement_modules
        in: body
        description: List of enhancement modules to use for the scan.

            Sending an empty array will disable all modules.

            Not sending the parameter will enable all modules.
        schema:
            type: array
            items:
              type: string
              enum:
                - domains
                - sensitive_keywords
                - contributors
                - secrets
              examples:
                - domains
                - sensitive_keywords
                - contributors
                - secrets
        required: false
      - name: organization_domains
        in: body
        schema:
            type: array
            items:
              type: string
        required: false
      - name: sensitive_keywords
        in: body
        schema:
            type: array
            items:
              type: string
        required: false
    responses:
      200:
        description: Enhancement task information.

      422:
        description: Repository name is missing.

      500:
        description: Generic error.
    """
    content = request.get_json(silent=True)
    if not content or not content["repo_name"]:
        abort(422)

    # Get the organization domains from the request body.
    org_domains = []
    if "organization_domains" in content:
        org_domains = content["organization_domains"]

    # Get the sensitive keywords from the request body.
    sensitive_keywords = []
    if "sensitive_keywords" in content:
        if not is_valid_sensitive_keywords(content["sensitive_keywords"]):
            return jsonify(
                results={
                    "success": False,
                    "error": "blacklisted characters in sensitive_keywords",
                }
            )

        sensitive_keywords = content["sensitive_keywords"]

    if "enhancement_modules" in content:
        enhancement_modules = content["enhancement_modules"]
    else:
        # Use the default enhancement modules if the parameter is not sent.
        from leaktopus.common.leak_enhancer import get_enhancement_modules

        enhancement_modules = get_enhancement_modules()

    # Scan (in an async way with Celery)
    from leaktopus.common.leak_enhancer import enhance_repo

    task = enhance_repo.s(
        content["repo_name"],
        organization_domains=org_domains,
        sensitive_keywords=sensitive_keywords,
        enhancement_modules=enhancement_modules,
    )
    task.apply_async()

    return jsonify(results={"success": True})
