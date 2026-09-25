import logging

log = logging.getLogger(__name__)
log.setLevel(20)
file_handler = logging.FileHandler("shuna.log", mode="a", encoding="utf-8")
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )
console_handler.setFormatter(formatter)
log.addHandler(console_handler)
log.addHandler(file_handler)