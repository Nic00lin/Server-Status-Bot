import paramiko

def list_files_and_directories(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command("ls -l")
        output = stdout.read().decode()
        return output
    except Exception as e:
        return str(e)
    finally:
        ssh.close()

def get_system_info(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command("cat /etc/*release")
        output = stdout.read().decode()
        return output
    except Exception as e:
        return str(e)
    finally:
        ssh.close()

def get_used_ports(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command("ss -tunpl")
        output = stdout.read().decode()
        return output
    except Exception as e:
        return str(e)
    finally:
        ssh.close()

def reboot_server(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command("sudo reboot")
        output = stdout.read().decode()
        return output
    except Exception as e:
        return str(e)
    finally:
        ssh.close()

def get_running_services(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command("service --status-all")
        output = stdout.read().decode()
        return output
    except Exception as e:
        return str(e)
    finally:
        ssh.close()

def get_available_memory(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command("free -h")
        output = stdout.read().decode()
        return output
    except Exception as e:
        return str(e)
    finally:
        ssh.close()