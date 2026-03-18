import socket
from multiprocessing import Process
from time import time

import pytest
import uvicorn
from fastapi import FastAPI


class Server:
    def __init__(self, app: FastAPI, port: int | None = None) -> None:
        self._app = app
        self._host = "localhost"
        self._port = port or self._get_random_port()
        self._process = Process(
            target=uvicorn.run, kwargs={"app": self._app, "host": self._host, "port": self._port}, daemon=True
        )

    def start(self) -> None:
        self._process.start()
        self._wait_for_port()

    def stop(self) -> None:
        self._process.kill()

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def url(self) -> str:
        return f"http://{self._host}:{self._port}"

    def _get_random_port(self) -> int:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        port: int = sock.getsockname()[1]
        sock.close()
        return port

    def _wait_for_port(self) -> None:
        start_time = time()
        timeout = 5

        while not self._can_connect():
            if time() > start_time + timeout:
                pytest.fail("Failed to start server")

    def _can_connect(self) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self._host, self._port))
            can_connect = True
        except socket.error:
            can_connect = False
        finally:
            sock.close()

        return can_connect
