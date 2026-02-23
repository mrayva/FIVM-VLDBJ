#!/bin/bash

./run_f-ivm.sh twitter && notify "F-IVM Twitter done"
# ./run_1-ivm.sh twitter && notify "1-IVM Twitter done"
# ./run_dbt.sh twitter && notify "DBT Twitter done"
# ./run_left-deep.sh twitter && notify "LEFT-DEEP Twitter done"

./run_f-ivm.sh tiktok && notify "F-IVM TikTok done"
# ./run_dbt.sh tiktok && notify "DBT TikTok done"
# ./run_1-ivm.sh tiktok && notify "1-IVM TikTok done"
# ./run_left-deep.sh tiktok && notify "LEFT-DEEP TikTok done"