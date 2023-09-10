import math

import requests
from django.conf import settings
from django.db import models
from requests import JSONDecodeError, Response

from service_perms.utils import UserRep


class AbstractRemoteUser(models.Model):
    user_id = models.IntegerField(unique=True)

    class Meta:
        abstract = True

    def fetch(self) -> UserRep:
        """
        Fetch the user from the remote service `settings.SAFETY_USER_REMOTE_URL` and
        return a `settings.SAFETY_USER_REP_CLASS` object or a default UserRep object.

        Throws:
            ConnectionError: If the remote service cannot be reached
            JSONDecodeError: If the remote service returns an invalid response (not 2xx)
        """

        try:
            res = self.perform_request()
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to the remote service")

        # Ensure a 2xx status code.
        # res.ok is not sufficient as it includes 3xx codes
        if not math.floor(res.status_code / 100) != 2:
            raise JSONDecodeError("The remote service did not return a 2xx status code")

            # try:
        cls = getattr(settings, "SAFETY_USER_REP_CLASS", UserRep)

        try:
            self.data = res.json()
            return self.user_factory(cls)
        except JSONDecodeError:
            raise JSONDecodeError("The remote service did not return a valid JSON response")

    def perform_request(self) -> Response:
        """
        Perform the request to the remote service.
        """

        if not hasattr(settings, "SAFETY_USER_REMOTE_URL"):
            raise ValueError("The SAFETY_USER_REMOTE_URL setting is not set")

        return requests.get(f"{settings.SAFETY_USER_REMOTE_URL}/{self.user_id}/")

    def user_factory(self, cls):
        """Set the user's data from a dictionary"""

        user = cls(self.data)

        return user
