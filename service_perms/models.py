import math

import requests
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from requests import JSONDecodeError, Response

from service_perms.utils import UserRep, user_rep_factory


class AbstractRemoteUser(AbstractBaseUser):
    user_id = models.IntegerField()

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
            return user_rep_factory(res.json(), cls)
        except JSONDecodeError:
            raise JSONDecodeError("The remote service did not return a valid JSON response")

    def perform_request(self) -> Response:
        """
        Perform the request to the remote service.
        """

        return requests.get(f"{settings.SAFETY_USER_REMOTE_URL}/{self.user_id}/")
