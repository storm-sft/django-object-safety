import math

import requests
from django.conf import settings
from django.db import models
from requests import JSONDecodeError, Response, HTTPError

from service_perms.utils import UserRep


def get_user_rep_class():
    return getattr(settings, "SAFETY_USER_REP_CLASS", UserRep)


class AbstractRemoteUser(models.Model):
    # Required by Django
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'user_id'

    user_id = models.IntegerField(unique=True)

    class Meta:
        abstract = True

    def fetch(self) -> UserRep:
        """
        Fetch the user from the remote service `settings.SAFETY_USER_REMOTE_URL` and
        return a `settings.SAFETY_USER_REP_CLASS` object or a default UserRep object.

        Throws:
            ConnectionError: The remote service cannot be reached
            HttpError: The remote service returns an error (not 2xx)
            HttpError: The remote service returns an invalid json response
        """

        try:
            res = self.perform_request()
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to the remote service")

        # Ensure a 2xx status code.
        # res.ok is not sufficient as it includes 3xx codes
        if math.floor(res.status_code / 100) != 2:
            raise HTTPError("The remote service did not return a 2xx status code")

        cls = get_user_rep_class()

        try:
            self.data = res.json()
            return self.user_factory(cls)
        except JSONDecodeError:
            raise HTTPError("The remote service returned an invalid JSON response")

    def perform_request(self) -> Response:
        """
        Perform the request to the remote service.
        """

        if not hasattr(settings, "SAFETY_USER_REMOTE_URL"):
            raise ValueError("The SAFETY_USER_REMOTE_URL setting is not set")

        return requests.get(f"{settings.SAFETY_USER_REMOTE_URL}/{self.user_id}/")

    def user_factory(self, cls):
        """Set the user's data from a dictionary"""

        try:
            user = cls(**self.extract_data())
        except TypeError as e:
            raise ValueError("Missing required fields in the remote service response: " + str(e))

        return user

    def extract_data(self):
        return {key: value for key, value in self.data.items() if key in get_user_rep_class().__annotations__}
