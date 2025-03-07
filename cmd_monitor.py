import psutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Log level: INFO, DEBUG, ERROR, etc.
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler("database_module.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)


class CmdMonitor:
    def __init__(self):
        """
        Initialize the CmdMonitor class to handle Command Prompt (cmd.exe) processes.
        """
        self.process_name = 'cmd.exe'

    def list_cmd_processes(self):
        """
        List all active Command Prompt (cmd.exe) processes.
        
        Returns:
            list: A list of dictionaries containing process details.
        """
        cmd_processes = []
        for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
            try:
                if process.info['name'] == self.process_name:
                    cmd_processes.append({
                        'pid': process.info['pid'],
                        'cmdline': process.info['cmdline']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return cmd_processes

    def close_idle_cmd_windows(self):
        """
        Close all idle Command Prompt (cmd.exe) windows (those without active commands running).
        """
        cmd_processes = self.list_cmd_processes()
        #print(cmd_processes)
        for process in cmd_processes:
            if len(process['cmdline']) == 1:  # Only "cmd.exe" is running
                try:
                    logging.info(f"Closing idle Command Prompt with PID: {process['pid']}")
                    psutil.Process(process['pid']).terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logging.info(f"Failed to terminate PID {process['pid']}: {e}")
            else:
                logging.info(f"Active Command Prompt with PID {process['pid']} is running: {process['cmdline']}")

#if __name__ == "__main__":
    