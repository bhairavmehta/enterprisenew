import json
import logging
from typing import List, Dict
import numpy as np

from thebox.common.scenario import NotificationDefinition, NotificationRule
from thebox.messages.predictionmessage import PredictionData
from thebox.messages.notificationmessage import NotificationMessage


class NotificationHandler(object):

    def __init__(self, notif_def: NotificationDefinition, logger: logging.Logger):
        self.notif_rules = notif_def.rules
        self.log = logger

    def __run_rule(self, rule: NotificationRule, preds: Dict[str, PredictionData]) -> bool:
        """call to evaluate a notification rule against prediction data
           and see if notification need to be raised or not
        """
        r_c = rule.rule_content
        self.log.debug(
            f"Evaluting rule {r_c} against prediction data: {'; '.join([ str(p) for p in preds])} ...")

        # In the eval rule environment, we provide
        #  - a variable named 'predicton' which is of type: Dict[str, PredictionData]
        #  - numpy imported as np
        #  - log variable is python logger
        globals = {
            'np': np,
            'log': self.log
        }
        locals = {
            'prediction': preds
        }
        is_rule_triggered = eval(r_c, globals, locals)
        self.log.debug(
            f"Evaluting rule {r_c} result is: {is_rule_triggered} ...")
        return is_rule_triggered

    def handle_prediction(self, preds: Dict[str, PredictionData]) -> List[str]:
        """Process a list of notificatinos by evaluating them against
           the notification rules. Return a list of notification triggered
           because of it
        """
        self.log.debug(
            f"Handling prediction against {len(self.notif_rules)} rule(s): " +
            f"{','.join([r.rule_name for r in self.notif_rules])} ...")
        notif_id_set = set()
        for r in self.notif_rules:
            if self.__run_rule(r, preds):
                notif_id_set.add(r.notification_id)

        if (len(notif_id_set) > 0):
            return list(notif_id_set)
        else:
            return None
