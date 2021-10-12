SCHDULED_ENDPOINT = '/user/scheduled_sends'
CONTACT_LIST_ENDPOINT = '/marketing/lists'
ALERT_ENDPOINT = '/alerts'
CREATE_BATCH_ENDPOINT = '/mail/batch'


PARAM_MAPPING = {
    "Phone": "phone",
    "Tablet": "tablet",
    "Webmail": "webmail",
    "Desktop": "desktop",
    "Pause": "pause",
    "Cancel": "cancel"
}

ENDPOINTS_DICT = {
    "Global Email Statistics": "/stats",
    "Country And State Province": "/geo/stats",
    "Device Type": "/devices/stats",
    "Client Type": "/clients/stats",
    "Mailbox Provider": "/mailbox_providers/stats",
    "Browser": "/browsers/stats"
}

ERROR_CODES = {
    "200": "No error",
    "201": "Successfully created",
    "204": "Successfully deleted",

}