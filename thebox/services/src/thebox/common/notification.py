from dataclasses import dataclass


@dataclass
class NotificationData(object):
    # category of the notification
    category_path: str = None

    # identifier of the notification
    notification_id: str = None


@dataclass
class NotificationRule(object):

    # name of this notification rule
    rule_name: str = None

    # the expression of the rule that if evaluate to true,
    # would trigger the notification
    rule_content: str = None

    # what notification to trigger
    notification_id: str = None
