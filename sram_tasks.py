from config import DATA_DIR
import logging
import os
from datetime import datetime
import json
from sramdata import SramData
import pandas as pd

today = datetime.now()
today_str = today.strftime('%Y%m%d')
year = today.strftime('%Y')
week = today.strftime('%U')

def _store(filename, data):
    """
    Store the data dict as a json file

    :param data: dict
    :param filename: string
    :return:
    """
    logger.info(f"Storing {filename}")
    with open(filename, "w") as f:
        json.dump(data, f, indent=1)

def setup_logging():
    LOGFILE = f'{DATA_DIR}log/sram-tasks_{today.year}{today.strftime("%m")}.log'
    logger = logging.getLogger('sram_tasks')
    hdlr = logging.FileHandler(LOGFILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    return logger

def collect():
    sramdata = SramData()
    logger.info(f'start script {os.path.realpath(__file__)}')
    report_filename = f'{DATA_DIR}/{year}{week}-sram_report.xlsx'
    
    if os.path.exists(report_filename):
        logger.info(f"Report already exists: {report_filename}")
    else:
        logger.info(f"start data collection")
    
        sramdata.logger = logger
        sramdata.collect()
        _store(data=sramdata.orgdata, filename=f"{DATA_DIR}/{year}{week}-sram_organisation.json")
        _store(data=sramdata.users, filename=f"{DATA_DIR}/{year}{week}-sram_members.json")    
        _store(data=sramdata.collaborations, filename=f"{DATA_DIR}/{year}{week}-sram_collaboration_membercount.json")

        logger.info(f"Creating report: {report_filename}")
        writer = pd.ExcelWriter(report_filename, engine="xlsxwriter")
        
        user_list = {"email": [], "invitation_count": [], "membership_count": []}
        for email, data in sramdata.users.items():
            user_list["email"].append(email)
            user_list["invitation_count"].append(data["invitations"])
            user_list["membership_count"].append(data["memberships"])
        dfg = pd.DataFrame.from_dict(data=user_list)
        dfg.to_excel(writer, sheet_name="users", index=False)

        co_list = {"link": [], "name": [], "members": [], "open invitations": []}
        for co_id, data in sramdata.collaborations.items():
            co_list["link"].append(f"https://sram.surf.nl/collaborations/{co_id}/members")
            co_list["name"].append(data["name"])
            co_list["members"].append(data["membership_count"])
            co_list["open invitations"].append(data["invitation_count"])
        dfg = pd.DataFrame.from_dict(data=co_list)
        dfg.to_excel(writer, sheet_name="collaboration", index=False)

        writer.close()
    logger.info('script finished')
    
logger = setup_logging()
collect()