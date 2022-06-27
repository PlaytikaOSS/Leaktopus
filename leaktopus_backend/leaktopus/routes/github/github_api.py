from flask import Blueprint, jsonify, request, abort, current_app
import leaktopus.common.db_handler as dbh

github_api = Blueprint('github_api', __name__)


@github_api.errorhandler(500)
def custom500(error):
    return jsonify(results={"success": False, "message": error.description})


def response_github_ignored():
    results = {
        "success": True,
        "ignored_repos": dbh.get_config_github_ignored()
    }
    return jsonify(results=results)


@github_api.route("/api/preferences/github", methods=['GET'])
def get_github_prefs():
    """API For getting GitHub preferences.
    ---

    responses:
      200:
        description: GitHub preferences, e.g., a list of GitHub ignored repositories (regexes).
        examples:
          {"results": {"ignored_repos": [{"id": 1, "pattern": "^https://github.com/foo/bar"}],"success": true}}

    """
    return response_github_ignored()


@github_api.route("/api/preferences/github", methods=['PUT'])
def udpate_github_prefs():
    """API For updating GitHub preferences.
    ---
    parameters:
      - name: pattern
        in: body
        type: string
        required: true
    responses:
      200:
        description: GitHub preferences, e.g., a list of GitHub ignored repositories (regexes).
        examples:
          {"results": {"ignored_repos": [{"id": 1, "pattern": "^https://github.com/foo/bar"}],"success": true}}

      422:
        description: Content is invalid or pattern is missing.
    """
    content = request.get_json(silent=True)

    if not content or not content["pattern"]:
        abort(422)

    dbh.add_config_github_ignored(content["pattern"])
    dbh.delete_leak_by_url(content["pattern"])

    return response_github_ignored()


@github_api.route("/api/preferences/github", methods=['DELETE'])
def delete_github_prefs():
    """API For deleting a GitHub preference.
    ---
    parameters:
      - name: id
        in: body
        type: integer
        required: true
    responses:
      200:
        description: GitHub preferences, e.g., a list of GitHub ignored repositories (regexes).
        examples:
          {"results": {"ignored_repos": [{"id": 1, "pattern": "^https://github.com/foo/bar"}],"success": true}}

      422:
        description: Content is invalid or preference id is missing.
    """
    content = request.get_json(silent=True)

    if not content or not content["id"]:
        abort(422)

    dbh.delete_config_github_ignored(int(content["id"]))

    return response_github_ignored()
