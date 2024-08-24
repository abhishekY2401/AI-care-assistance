import logging
from app import create_app

# config class


class DevConfig:
    debug = True
    port = 9000


class ProdConfig:
    debug = False


# trigger app factory
app = create_app()

# setup loggers
app.logger.setLevel(logging.INFO)
app.logger.info('App Started')

if __name__ == '__main__':
    app.run(port=9000)
