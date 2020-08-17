
import logging
import os

from slack import WebClient
from slack.errors import SlackApiError

from utils import utc_now_timestamp


logger = logging.getLogger(__name__)


class SlackAlertManager:

    def __init__(self, api_key, channel):
        self.client = WebClient(api_key)
        self.channel = channel
        self.alerts = []

    def add(self, message, level, stack_trace=None):
        alert = self._prepare_alert(message, level, stack_trace)
        self.alerts.append(alert)

    def insert(self, position, message, level, stack_trace=None):
        alert = self._prepare_alert(message, level, stack_trace)
        self.alerts.insert(0, alert)

    def _prepare_alert(self, message, level, stack_trace=None):
        return AlertMessage(
            message,
            level,
            stack_trace=stack_trace
        )

    def send(self):
        #TODO: if level is info, send basic msg;
        # if error, send stack_trace as file
        for alert in self.alerts:
            try:
                response = self.send_message(alert)
            except SlackApiError as e:
                logger.error('Slack alert error: {}'.format(e.response['error']))

    def send_message(self, alert):
        return self.client.chat_postMessage(
            channel=self.channel,
            text=alert.msg
        )

    def send_stack_trace(self, alert):
        pass


class AlertMessage:

    def __init__(self, msg, level='INFO', stack_trace=None):
        self._msg = msg
        self.level = level.upper()
        self.stack_trace = stack_trace
        self.timestamp = utc_now_timestamp()

    @property
    def msg(self):
        return "warn-scraper ({} - {}) {}".format(
            self.timestamp,
            self.level,
            self._msg
        )