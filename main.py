import psutil
import configparser
from cam_sys_status_database import DatabaseModule
from db import DatabaseAwsModule
from cmd_monitor import CmdMonitor 
import logging
import json
import requests
from api_call import IcelandCamSysAPI
from json_handler import JsonHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Log level: INFO, DEBUG, ERROR, etc.
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler("database_module.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)

from ses_run import send_mail
def check_python_processes(target_scripts):
    """
    Checks if the specified Python scripts are running.
    
    Args:
        target_scripts (list): A list of script names to check (e.g., ["script1.py", "script2.py"]).
    """
    # Get a list of running processes
    running_processes = []
    output = {}
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Filter for Python processes
            if "python" in (process.info['name'] or '').lower() or \
               "python" in " ".join(process.info['cmdline'] or []).lower():
                running_processes.append(process.info)
            elif "cmd" in (process.info['name'] or '').lower() or \
               "cmd" in " ".join(process.info['cmdline'] or []).lower():
               running_processes.append(process.info)
               
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    #print(running_processes)
    # Check if target scripts are running
    for script in target_scripts:
        script_running = False
        for process in running_processes:
            if process.get('cmdline', []) in [None, []]:
                continue
            #print("--------> ", " ".join(process.get('cmdline', [])))
            if script in " ".join(process.get('cmdline', [])):
                script_running = True
                #print(f"{script}: Running (PID {process['pid']})")
                #output[script] = process['pid'] 
            
            
            
                
        if not script_running:
            output[script] = 'Not running'
            #print(f"{script}: Not running")
    return output

def insert_into_db(store_id, cam_no=None, script_name=None, company=None):
    try:
        aws_db_module.insert_status(store_id, cam_no, "Not Running", script_name, company=company)
    except Exception as e:
        print(str(e))
        logging.critical(f"Critical error in the main program: {e}")


def fetch_cam_status(api_client, store_id, cams, time_range_minutes):
    
    # Call 1: Recent Status Records
    recent_status_payload = {
        'store_id': store_id,
        'camera_num_list': cams,
        'time_range_minutes': time_range_minutes,
    }
    recent_status_response = api_client.make_request(
        "/status/recent-status-records", "POST", json_data=recent_status_payload
    )
    result = {status["camera_no"]:"Not Running" for status in recent_status_response if status["status_count"] < 4}
    
    print(f"{result = }")
    return result


def insert_api_call(api_client, store_id=None, cam_no=None, status="Not Running", script=None, company=None):
    
    if script is not None:
        script = repr(script)
    
    alert_status_payload = {
         'store_id': store_id,
         'cam_no': cam_no,
         'status': status,
         'script_name': script,
         'company': company,
     }
    #print("----------->", alert_status_payload)
    alert_status_response = api_client.make_request(
         "/status/alert-status", "PUT", json_data=alert_status_payload
     )
    print("Alert Status Response:", alert_status_response)
    

def send_mail_api_call(api_client, message=None, store_name=None):
    send_email_payload = {
        'message': message,
        'store_name': store_name,
    }
    send_email_response = api_client.make_request(
        "/email/send", "POST", json_data=send_email_payload
    )
    
    
    print("Send Email Response:", send_email_response)



if __name__ == "__main__":
    
    # Read configuration
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    # Database operations
    DB_URL = config.get("database", "db_url", raw=True)
    AWS_DB_URL = config.get("database", "aws_db_url", raw=True)
    TABLE_NAME = config["database"]["table_name"]
    STORE_ID = int(config["query"]["store_id"])
    CAMERA_NOs = config["query"]["camera_no"].split(', ')
    TIME_RANGE_MINUTES = int(config["query"]["time_range_minutes"])
    COMPANY_NAME = config["company_details"]["name"]
    STORE_NAME = config["company_details"]["store_name"]
    BASE_URL = config["company_details"]["base_url"]
    
    # Create a DatabaseModule instance
    #db_module = DatabaseModule(DB_URL, TABLE_NAME)
    #aws_db_module = DatabaseAwsModule(AWS_DB_URL)
    json_file_path = 'data.json'
    json_handler = JsonHandler(json_file_path)
    
    # Create or update the date in the JSON file
    json_handler.create_or_update_date()
    
    
    
    print("START")
    api_client = IcelandCamSysAPI(BASE_URL)
    
    message = f"This message is generate from Store_id {STORE_NAME},"

    '''# Fetch camera status
    cam_status_output = {}
    for CAMERA_NO in CAMERA_NOs:
        records = db_module.fetch_recent_records(STORE_ID, CAMERA_NO, TIME_RANGE_MINUTES)
        if len(records) < 4:
            # Insert Into Database When Error Occured
            insert_into_db(store_id = STORE_ID, cam_no = CAMERA_NO, script_name = config.get("cam_sys_status", "script_path"), company=COMPANY_NAME)
            cam_status_output[CAMERA_NO] = 'Not Running'
            
    if len(cam_status_output) > 0:
        message = message + "\n" +f""" 
        Application: cam_sys_status_api
        Cameras are not working, 
        {cam_status_output} 
        Please visit the Stort and Fix it, ASAP
        ------------------------------------------------------
                    """
        #send_mail(message)
    '''
    
    cam_status_output = fetch_cam_status(api_client, STORE_ID, CAMERA_NOs, TIME_RANGE_MINUTES)
    #print(f"{cam_status_output = }")
    saved_json = json_handler.fetch_json()
    cam_status_output = [x for x in list(cam_status_output.keys()) if str(x) not in list(saved_json.keys())]
    cam_status_output = dict.fromkeys(cam_status_output, "Not Running")
    
    if len(cam_status_output) > 0:
        json_handler.update_data(updates=cam_status_output)
        for cam in cam_status_output:
            insert_api_call(api_client, STORE_ID, cam, "Not Running", config.get("cam_sys_status", "script_path"), COMPANY_NAME)
        message = message + "\n" +f""" 
        Application: cam_sys_status_api
        Cameras are not working, 
        {cam_status_output} 
        Please visit the Store and Fix it, ASAP
        ------------------------------------------------------
                    """

    
    # Check FFMPEG scripts
    ffmpeg_scripts = config.get('ffmpeg', 'scripts_names').split(', ')
    ffmpeg_scripts_output = check_python_processes(ffmpeg_scripts)
    
    ffmpeg_scripts_output = [x for x in list(ffmpeg_scripts_output.keys()) if str(x).split(" ")[-1].split(".")[0]  not in list(saved_json.keys())]
    ffmpeg_scripts_output = dict.fromkeys(ffmpeg_scripts_output, "Not Running")
    
    if len(ffmpeg_scripts_output) > 0:
        for script in ffmpeg_scripts_output.keys():
            cam_no = script.split(" ")[-1].split(".")[0]
            # Insert Into Database When Error Occured
            #insert_into_db(store_id = STORE_ID, cam_no = cam_no, script_name = script, company=COMPANY_NAME )
            # API call insert into database
            insert_api_call(api_client, STORE_ID, cam_no, "Not Running", script, COMPANY_NAME)
            
        message = message + "\n" + f"""        
        Application: FFMPEG Video Scripts
        FFMPEG Video Scripts are not working, 
        {ffmpeg_scripts_output} 
        Please visit the Store and Fix it, ASAP
        ------------------------------------------------------
                    """
        #send_mail(message)
    

    # Check customer aisle interaction scripts
    customer_aisle_scripts = config.get('customer_aisle_interaction', 'scripts_names').splitlines()
    customer_aisle_script_path = config.get('customer_aisle_interaction', 'script_path')
    config = json.load(open(customer_aisle_script_path, 'r'))
    
    rtsp_urls = config["video_paths"]
       
    
    command = [f'python monitor_aisle.py --rtsp {url[0]} --cam_no {cam} --area_percentage {url[1]}' for cam, url in rtsp_urls.items() if cam not in list(saved_json.keys())]
    #print("command: ", command)
    customer_aisle_scripts.extend(command)
    
    customer_aisle_output = check_python_processes(customer_aisle_scripts)
    #print(f"{customer_aisle_output = }")
    if len(customer_aisle_output) > 0:
        for script in customer_aisle_output.keys():
            print(script)
            # Insert Into Database When Error Occured
            #insert_into_db(store_id = STORE_ID, script_name = script, company=COMPANY_NAME
            insert_api_call(api_client, store_id = STORE_ID, script = script, company=COMPANY_NAME)
            
        message = message + "\n" + f""" 
        Application: customer_aisle_interaction
        customer_aisle_interaction are not working, 
        {customer_aisle_output} 
        Please visit the Store and Fix it, ASAP
        ------------------------------------------------------
                    """
      
    message_checker = message.replace(f"This message is generate from Store_id {STORE_NAME},", "")
    #print(message, "---->", message_checker)
    if message_checker != "" or len(message_checker)>0:
        #send_mail(message, STORE_NAME)
        send_mail_api_call(api_client, message, STORE_NAME)

    
#######################################################################    
'''    # Create an instance of CmdMonitor
    cmd_monitor = CmdMonitor()

    # List all cmd processes
    logging.info("Listing all cmd.exe processes:")
    cmd_processes = cmd_monitor.list_cmd_processes()
    for proc in cmd_processes:
        logging.info(f"PID: {proc['pid']}, Command Line: {proc['cmdline']}")

    # Close idle cmd processes
    logging.info("\nClosing idle cmd.exe processes:")
    cmd_monitor.close_idle_cmd_windows()
    '''
    