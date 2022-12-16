from flask import Blueprint, jsonify, request, abort, current_app

from leaktopus.factory import create_notification_service
from leaktopus.usecases.notification_test import NotificationTestUseCase

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


@alerts_api.route("/api/alerts/<integration_type>/test", methods=['GET'])
def notification_test(integration_type):
    """API For sending a notification test alert (to verify integration).
    ---
    parameters:
      - name: integration_type
        in: path
        type: string
        required: true
    responses:
      200:
        description: Operation result with confirmation/error message.
    """
    use_case = NotificationTestUseCase(
        create_notification_service(integration_type)
    )
    use_case.execute()

    # @todo Return more informative response in case of errors.
    return jsonify(results={"success": True})
