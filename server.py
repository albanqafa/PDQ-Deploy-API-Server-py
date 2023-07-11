from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import re
import win32security
import win32process
import win32con
import win32event
import datetime

ct = datetime.datetime.now()

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.startswith("/deploy/"):
			package_name, computer_name = self.path.split("/")[2:4]

			if not self.validate_parameters(package_name, computer_name):
				self.send_response(400)
				self.end_headers()
				return

			command_output = self.run_command_with_different_user(package_name, computer_name)

			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			#self.wfile.write(pdq_output.encode())

			log_entry = f"{ct} Request from: {self.client_address[0]}, Package: {package_name}, Computer: {computer_name}, Errors: {command_output}\n"
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
		command = "pdqdeploy.exe deploy -package {} -targets {}".format(package_name, computer_name)

		try:
			# Obtain a handle to the user's token
			user_handle = win32security.LogonUser(
				self.config["username"],
				".",  # Use the local computer
				self.config["password"],
				win32con.LOGON32_LOGON_INTERACTIVE,  # Logon type
				win32con.LOGON32_PROVIDER_DEFAULT  # Logon provider
			)

			# Use the token to execute the command
			process_info = win32process.CreateProcessAsUser(
				user_handle,  # Token
				None,  # ApplicationName (None to use CommandLine)
				command,  # CommandLine
				None,  # ProcessAttributes
				None,  # ThreadAttributes
				0,  # bInheritHandles
				win32con.NORMAL_PRIORITY_CLASS,  # dwCreationFlags
				None,  # Environment (None to inherit from parent)
				None,  # CurrentDirectory (None to inherit from parent)
				win32process.STARTUPINFO()  # StartupInfo
			)

			# Wait for the process to complete
			win32event.WaitForSingleObject(process_info[0], win32event.INFINITE)
		except Exception as e:
			return f"Error executing command: {str(e)}"
		else:
			return "Command executed successfully"

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

