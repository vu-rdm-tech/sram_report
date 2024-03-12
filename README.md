## Goals
- Report on acceptance of (Yoda) CO invitations. 
- Provide SRAM invitation and membership status information for https://github.com/vu-rdm-tech/adminyoda

## Usage
Rename `config.template.py` to `config.py` and set an SRAM organization API key and an absolute path to the `data` directory as `DATA_DIR`.

Add `<path to python>/python <path to script>/sram_tasks.py` to you crontab. You can schedule the script to run multiple times a day. The script produces output with a weeknumber in the name. If output is already present data collection is skipped, so you will end up with weekly output.

## Ouput
1. `data/202410-sram_organisation.json` output of `/api/organisations/v1`.
2. `data/202410-sram_members.json` membership and open invitation count per user email address.
3. `data/202410-sram_collaboration_membercount.json` membership and open invitation count per CO.
4. `data/202410-sram_report.xlsx` 2 and 3 in excel format.
