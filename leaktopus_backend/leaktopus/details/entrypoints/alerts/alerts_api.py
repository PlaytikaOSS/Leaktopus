from flask import Blueprint, jsonify, current_app

from leaktopus.factory import (
    create_notification_service,
    create_leak_service,
    create_alert_service,
)
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.domain.alerts.usecases.notification_test import NotificationTestUseCase
from leaktopus.utils.common_imports import logger

alerts_api = Blueprint("alerts_api", __name__)


@alerts_api.errorhandler(500)
def custom500(error):
    return jsonify(results={"success": False, "message": error.description})


@alerts_api.route("/api/alerts/send", methods=["GET"])
def send_notifications():
    """API For manually send pending alerts.
    ---
    responses:
      200:
        description: Action confirmation with the number of sent alerts..
        examples:
          {"results": {"message": "Sent X new alertsֿ","success": true}}
    """
    notification_providers_sent = []

    leak_service = create_leak_service()
    alert_service = create_alert_service()
    for notification_provider in current_app.config["NOTIFICATION_CONFIG"].keys():
        try:
            notification_service = create_notification_service(notification_provider)
            leaks_notified = SendAlertsNotificationTask(
                leak_service, alert_service, notification_service
            ).run()

            notification_providers_sent.append(notification_service.get_provider_name())
        except NotificationException as e:
            logger.warning(
                "Cannot send alerts notification via send_notifications route. Message: {}",
                e,
            )
        except Exception as e:
            logger.error(
                "Error sending alerts notification via send_notifications route. Message: {}",
                e,
            )

    if len(notification_providers_sent) > 0:
        message = "Sent new alerts via {}".format(",".join(notification_providers_sent))
    else:
        message = "No alerts were sent."

    results = {"success": True, "message": message}

    return jsonify(results=results)


@alerts_api.route("/api/alerts/<integration_type>/test", methods=["GET"])
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
    use_case = NotificationTestUseCase(create_notification_service(integration_type))
    use_case.execute()

    # @todo Return more informative response in case of errors.
    return jsonify(results={"success": True})
