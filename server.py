from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import re
import subprocess
import os

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.startswith("/deploy/"):
			package_name, computer_name = self.path.split("/")[2:4]

			if not self.validate_parameters(package_name, computer_name):
				self.send_response(400)
				self.end_headers()
				return

			pdq_output = self.run_command_with_different_user(package_name, computer_name)

			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			#self.wfile.write(pdq_output.encode())

			log_entry = f"Request from: {self.client_address[0]}, Package: {package_name}, Computer: {computer_name}, PDQ Deploy output: {pdq_output}\n"
			try:
				with open(self.config["logfile"], "a") as log_file:
					log_file.write(log_entry)
			except Exception as e:
				print(f"Error writing to log file: {e}")

			print(log_entry)

		else:
			self.send_response(404)
			self.end_headers()

	def validate_parameters(self, package_name, computer_name):
		package_whitelist = self.config["whitelistedPackages"]
		package_regex = r"^[a-zA-Z0-9_-]+$"

		if not re.match(package_regex, package_name) or package_name not in package_whitelist:
			return False

		computer_regex = r"^[a-zA-Z0-9_-]+$"
		if not re.match(computer_regex, computer_name):
			return False

		return True

	def run_command_with_different_user(self, package_name, computer_name):
		command = [
			"psexec.exe",
			"-nobanner",
			"-r", "pdq_api_backend",
			"-u", self.config["username"],
			"-p", self.config["password"],
			"pdqdeploy.exe",
			"deploy",
			"-package", package_name,
			"-targets", computer_name
		]

		try:
			runas_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output, error = runas_process.communicate()

			if runas_process.returncode != 0:
				return f"Error executing command: {error.decode()}"

			return output.decode()
		except subprocess.CalledProcessError as e:
			return f"Error executing command: {e.output.decode()}"
		except FileNotFoundError:
			return "psexec.exe or pdqdeploy.exe not found"

def load_config(file_path):
	config = {}
	with open(file_path, "r") as config_file:
		for line in config_file:
			if line.strip() == "":
				continue
			key, value = line.strip().split("=", 1)
			config[key.strip()] = value.strip()
	return config

def run_server(config_file):
	config = load_config(config_file)

	server_address = ("", 8080)
	httpd = ThreadingHTTPServer(server_address, MyHTTPRequestHandler)
	MyHTTPRequestHandler.config = config
	httpd.serve_forever()

if __name__ == "__main__":
	run_server("config.txt")

