import config
from app import app
from pathlib import Path
import shutil
import os

filename = "index.html"
BACKEND_URL = "test"

@app.route("/admin", method="GET")
def admin_page():
	shutil.copyfile(f"{filename}", f"{filename}-dup")
	page = Path(f"{filename}-dup")
	content = page.read_text(encoding="utf-8")
	content = content.replace("API_CHANGE_TEXT", config.BACKEND_URL)
	page.write_text(content, encoding="utf-8")
	del content

	file = open(f"{filename}-dup", "r")
	content = file.read()
	os.remove(f"{filename}-dup")
	log.debug("Showing content of duplicated modified file:\n" + content)
	return content

