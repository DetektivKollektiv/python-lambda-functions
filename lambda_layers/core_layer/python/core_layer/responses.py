class InternalError:
    def __init__(self, message: str = None, exception: Exception = None):
        self.statusCode = 500

        if(message is None and exception is None):
            self.body = "An unexpected error occured."
            return

        if(message is not None and exception is None):
            self.body = message
            return

        self.body.message = message
        self.body.exception = exception


class BadRequest:
    def __init__(self, message: str = None):
        self.statusCode = 400

        if(message is not None):
            self.body = message
            return


class Success:
    def __init__(self, content=None, message: str = None):
        self.statusCode = 200

        if(content is not None):
            self.body = content

        if(message is not None):
            self.body = message
            return


class Created:
    def __init__(self, content=None, message: str = None):
        self.statusCode = 201

        if(content is not None):
            self.body = content

        if(message is not None):
            self.body = message
            return


class NoContent:
    def __init__(self, message: str = None):
        self.statusCode = 204

        if(message is not None):
            self.body = message
            return
