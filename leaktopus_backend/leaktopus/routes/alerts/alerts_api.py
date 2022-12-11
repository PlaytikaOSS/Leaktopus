from flask import Blueprint, jsonify, request, abort, current_app

from leaktopus.factory import create_notification_service
from leaktopus.usecases.ms_teams_notification_test import MSTeamsNotificationTestUseCase

alerts_api = Blueprint('alerts_api', __name__)


@alerts_api.errorhandler(500)
def custom500(error):
    return jsonify(results={"success": False, "message": error.description})


@alerts_api.route("/api/alerts/send", methods=['GET'])
def send_alerts():
    """API For manually send pending alerts.
    ---
    responses:
      200:
        description: Action confirmation with the number of sent alerts..
        examples:
          {"results": {"message": "Sent X new alertsֿ","success": true}}
    """
    import leaktopus.common.teams_alerter as teams_alerter
    results = {
        "success": True,
        "message": teams_alerter.alert()
    }

    return jsonify(results=results)


@alerts_api.route("/api/alerts/teams/test", methods=['GET'])
def teams_webhook_test():
    """API For sending an MS Teams test alert (to verify integration).
    ---
    responses:
      200:
        description: Operation result with confirmation/error message.
    """
    use_case = MSTeamsNotificationTestUseCase(
        create_notification_service()
    )
    use_case.execute()

    # @todo Return more informative response in case of errors.
    return jsonify(results={"success": True})
