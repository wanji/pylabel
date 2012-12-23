#!/usr/bin/env python
# coding: utf-8

################################################################################
# Tool for image concepts labeling. 
#  ** Implemented in the Python language with OpenCV highgui.
#-------------------------------------------------------------------------------
# Working Mode
#  ** Currently support two working mode: single(1), double(2).
#  ** Working mode indicated by the label_num variable.
#  Single: labeling only one concept at a timei, controled by d/f.
#  Double: labeling two concepts at a time, controled by a/s/d/f.
# Arguments:
#   1~2 concepts, corresponds to single mode and double mode.
#-------------------------------------------------------------------------------
# TIP: This tool support autoplay mode. 
#   That means after you press key 'f', it will automaticly moving forward, 
#   and label the concepts as FALSE by default.
#  ** This feature could be turn off in the configuration file by set the 
#     'interval' option in [cv] section to 0.
################################################################################

import os
import sys
import ConfigParser

import sqlite3

import cv2
import label_common as lc

def help(prog):
  lc.perr("Usage: %s label1 [label2]\n" % prog);

  lc.perr("Control: \n");
  lc.perr("\tj: next image\n");
  lc.perr("\tk: previous image\n");
  lc.perr("\ta: only true on label1\n");
  lc.perr("\ts: only true on label2\n");
  lc.perr("\td: true label / true on both labels\n");
  lc.perr("\tf: false label / false on both labels\n");
  lc.perr("\t0~9: interval(100ms); 0 indicates infinite wait time\n");
  lc.perr("\tESC: quit the program\n");

def main(argv):
  try:
    label1 = sys.argv[1];
    try:
      label2 = sys.argv[2];
    except:
      label_num = 1;
  except:
    help(argv[0]);
    sys.exit(1);

  # Load configuration
  (db_path, tb_name, imlist, labels) = lc.load_cfg(lc.cfg_path);
  (default_interval) = lc.load_cv_cfg(lc.cfg_path);

  # Check if the database exists
  lc.check_db(db_path, tb_name, imlist, labels);

  # Check if the labels are from the label list
  if (label1 not in labels.split()):
    print "Error: '%s' is not in the label list!" % label1;
    lc.perr("\tSupported labels are: %s\n" % labels);
    sys.exit(1);

  if (2 == label_num and label2 not in labels.split()):
    print "Error: '%s' is not in the label list!" % label2;
    lc.perr("\tSupported labels are: %s\n" % labels);
    sys.exit(1);

  # Adapt workint model
  print "Working mode: %d" % label_num;
  # SQLs for update label information.
  a_ = 1048673; s_ = 1048691; d_ = 1048676; f_ = 1048678;
  
  update_sql = {};
  if (1 == label_num):
    print "\tLabel: %s" % label1;
    # SQL for fetch labeled images
    prev_sql  = "select img from %s where %s!='0'" % (tb_name, label1);
    # SQL for fetch unlabeled image
    fetch_sql = "select img, %s from %s where %s='0'" % (label1, tb_name, label1);
    # SQL for view labeled image
    view_sql  = "select img, %s from %s where img=?" % (label1, tb_name);
    # SQLs for update label information
    update_sql[d_] = "update %s set %s='t' where img=?" % (tb_name, label1);
    update_sql[f_] = "update %s set %s='f' where img=?" % (tb_name, label1);
    # Window Title for imshow
    imshow_title = label1;
  elif (2 == label_num):
    print "\tLabel: %s %s" % (label1, label2);
    # SQL for fetch labeled images
    prev_sql  = "select img from %s where %s!='0' and %s!='0'" % (tb_name, label1, label2);
    # SQL for fetch unlabeled image
    fetch_sql = "select img, %s, %s from %s where %s='0' or %s='0'" % (label1, label2, tb_name, label1, label2);
    # SQL for view labeled image
    view_sql  = "select img, %s, %s from %s where img=?" % (label1, label2, tb_name);
    # SQLs for update label information
    update_sql[a_] = "update %s set %s='t', %s='f' where img=?" % (tb_name, label1, label2);
    update_sql[s_] = "update %s set %s='f', %s='t' where img=?" % (tb_name, label1, label2);
    update_sql[d_] = "update %s set %s='t', %s='t' where img=?" % (tb_name, label1, label2);
    update_sql[f_] = "update %s set %s='f', %s='f' where img=?" % (tb_name, label1, label2);
    # Window Title for imshow
    imshow_title = "a: " + label1 + "    s: " + label2;

  # Connect to the database
  conn = sqlite3.connect(db_path)
  c = conn.cursor();

  interval = 0;
  proclst = [];
  idx = -1;

  c.execute(prev_sql);
  items = c.fetchall();
  proclst = [item[0] for item in items];
  idx = len(proclst) - 1;
  
  prenum = len(proclst);

  c.execute(fetch_sql);
  item = c.fetchone();
  if (None  == item):
    lc.perr("Labeling is finished, please choose other labels!\n");
    return;
  proclst.append(item[0]); idx += 1;
  while (None != item):
    print idx, [str(x) for x in item];

    cv2.imshow(imshow_title, cv2.imread(item[0]));
    key = cv2.waitKey(interval);
    if (-1 == key):
      key = 1048678;
    elif (key >= 1048624 and key <= 1048633):
      interval = 100 * (key - 1048624);
      continue;
      

    # Esc pressed
    if (1048603 == key):
      conn.commit();
      break;
    # j pressed, move forward
    elif (1048682 == key):
      interval = 0;
      idx += 1;
      print "up", idx;
      if (idx >= len(proclst)):
        idx -= 1;
        lc.perr("Last image!\n");
      else:
        c.execute(view_sql, (proclst[idx], ));
        item = c.fetchone();
      continue;
    # k pressed, move backward
    elif (1048683 == key):
      interval = 0;
      idx -= 1;
      print "down", idx;
      if (idx < 0):
        idx += 1;
        lc.perr("First image!\n");
      else:
        c.execute(view_sql, (proclst[idx], ));
        item = c.fetchone();
      continue;
    # a/s/d/f pressed
    elif (2 == label_num and key in [a_, s_, d_, f_]) or  \
         (1 == label_num and key in [d_, f_]):
      if (key == f_):
        interval = default_interval;
      c.execute(update_sql[key],  (item[0], ));
      # conn.commit();
      if (idx < len(proclst) - 1):
        idx += 1;
        c.execute(view_sql, (proclst[idx], ));
        item = c.fetchone();
        continue;
    else:
      print "Invalid op: %d" % key;
      continue;

    c.execute(fetch_sql);
    item = c.fetchone();
    if (None == item):
      break;
    proclst.append(item[0]); idx += 1;

  print "You have labeled %d images this time!" % (len(proclst) - prenum)
  return;

if __name__ == '__main__':
  main(sys.argv);

