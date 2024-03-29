import logging
import os
import json
import traceback
from typing import Any


class ResponseBase:

    statusCode: int
    body: Any
    headers: dict

    def __init__(self, event, add_cors_headers: bool) -> None:

        self.statusCode = 0
        self.body = None
        self.headers = {}

        if(add_cors_headers):
            source_origin = None
            allowed_origins = os.environ['CORS_ALLOW_ORIGIN'].split(',')

            if 'headers' in event and event['headers'] is not None:
                if 'Origin' in event['headers']:
                    source_origin = event['headers']['Origin']
                if 'origin' in event['headers']:
                    source_origin = event['headers']['origin']

                if source_origin and source_origin in allowed_origins:
                    self.headers['Access-Control-Allow-Origin'] = source_origin

    def to_json_string(self):
        logging.info("Returning response:")
        logging.info(self.__dict__)
        return self.__dict__


class InternalError(ResponseBase):

    def __init__(self, event, message: str = None, exception: Exception = None, add_cors_headers: bool = True):
        super().__init__(event, add_cors_headers)

        self.statusCode = 500

        if(message is None and exception is None):
            self.body = "An unexpected error occured."
            return

        if(message is not None and exception is None):
            self.body = message
            return

        if(message is None and exception is not None):
            self.body = traceback.format_exception_only(
                type(exception), exception)  # exception
            return

        self.body = {}
        self.body['message'] = message
        self.body['exception'] = traceback.format_exception_only(
            type(exception), exception)


class BadRequest(ResponseBase):
    def __init__(self, event, message: str = None, add_cors_headers: bool = True):
        super().__init__(event, add_cors_headers)

        self.statusCode = 400

        if(message is not None):
            self.body = message
            return


class NotFound(ResponseBase):
    def __init__(self, event, message: str = None, add_cors_headers: bool = True) -> None:
        super().__init__(event, add_cors_headers)

        self.statusCode = 404
        if(message is not None):
            self.body = message
            return


class Success(ResponseBase):
    def __init__(self, event, content=None, message: str = None, add_cors_headers: bool = True):
        super().__init__(event, add_cors_headers)

        self.statusCode = 200

        if(content is not None):
            self.body = content

        if(message is not None):
            self.body = message
            return


class Created(ResponseBase):
    def __init__(self, event, content=None, message: str = None, add_cors_headers: bool = True):
        super().__init__(event, add_cors_headers)

        self.statusCode = 201

        if(content is not None):
            self.body = content

        if(message is not None):
            self.body = message
            return


class NoContent(ResponseBase):
    def __init__(self, event, message: str = None, add_cors_headers: bool = True):
        super().__init__(event, add_cors_headers)

        self.statusCode = 204

        if(message is not None):
            self.body = message
            return


class Forbidden(ResponseBase):
    def __init__(self, event, message: str = None, add_cors_headers: bool = True) -> None:
        super().__init__(event, add_cors_headers)

        self.statusCode = 403

        if message is not None:
            self.body = message
