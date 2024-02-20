# chat/consumers.py
import fcntl
import json
import logging
import os
import pty
import select
import struct
import subprocess
import termios
import threading

from channels.generic.websocket import WebsocketConsumer


class TerminalConsumer(WebsocketConsumer):
    child_pid = None
    fd = None
    shell = None

    def connect(self):
        self.accept()

        if self.child_pid is not None:
            return

        master_fd, slave_fd = pty.openpty()

        self.fd = master_fd

        self.subprocess = subprocess.Popen(
            ["bash"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid,
        )
        self.child_pid = self.subprocess.pid

        thread = threading.Thread(target=self.read_from_pty)
        thread.daemon = True  # Daemonize the thread so it automatically dies when the main thread exits
        thread.start()

    def read_from_pty(self):
        while True:
            select.select([self.fd], [], [])
            output = os.read(self.fd, 1024)
            if not output:
                break
            message = output.decode(errors="ignore")
            self.send(text_data=json.dumps({"message": message}))

    def resize(self, row, col, xpix=0, ypix=0):
        logging.info(f"Resizing terminal to {row}x{col}")
        winsize = struct.pack("HHHH", row, col, xpix, ypix)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def write_to_pty(self, message):
        os.write(self.fd, message.encode())

    def kill_pty(self):
        if self.subprocess is not None:
            self.subprocess.kill()
            self.subprocess = None
            self.child_pid = None

    def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        self.subprocess.terminate()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        if text_data_json["action"] == "resize":
            self.resize(text_data_json["data"]["rows"], text_data_json["data"]["cols"])
        elif text_data_json["action"] == "input":
            message = text_data_json["data"]["message"]
            self.write_to_pty(message)
        elif text_data_json["action"] == "kill":
            self.kill_pty()
            self.send(text_data=json.dumps({"message": "Terminal killed"}))
        else:
            logging.info(f"Unknown action: {text_data_json['action']}")
