#!/bin/bash

#########################################################################
# File Name: upgrade_to_8413512.sh
# Author: Wan Ji
# mail: wanji@live.com
# Created Time: 2015年07月14日 星期二 17时16分00秒
#########################################################################
#########################################################################

if [ $# -ne 1 ]; then 
  echo "This script is used for upgrading the sqlite database generated before commit '8413512'."
  echo "  Changes of database:"
  echo "    1. Change label data type from TEXT to INT"
  echo "    2. Denote positive/negative/unlabelled as +1/-1/0 instead of 't'/'f'/'0'"
  echo "Usage: $0 sqlite_db"
  exit 1
fi

DATE=`date "+%y-%m-%d_%H.%M.%S"`
mv $1 $1.bak.$DATE
sqlite3 $1.bak.$DATE .dump \
  | sed "s/'f'/-1/g" | sed "s/'t'/+1/g" | sed "s/'0'/0/g" \
  | sed "s/ \<TEXT\>/ INT/g" | sed "s/\<img INT\>/img TEXT/g" \
  | sqlite3 $1
