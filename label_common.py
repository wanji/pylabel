#!/usr/bin/env python
# coding: utf-8

############################################################
# global variables and common functions
############################################################

import os
import sys
import ConfigParser

import sqlite3

cfg_path  = 'label.cfg';

def perr(errmsg):
  sys.stderr.write(errmsg);

# Initialize the database
def initdb(db_path, tb_name, imlist, labels):
  conn = sqlite3.connect(db_path);
  curs = conn.cursor();
  sqlstr = "CREATE TABLE %s (img TEXT" % tb_name;
  for label in labels:
    sqlstr += ", %s TEXT" % label;
  sqlstr += ");"
  print sqlstr;
  curs.execute(sqlstr);

  to_db = [tuple([line]) + tuple(['0'] * len(labels)) for line in imlist];

  fields = "img";
  poses  = "?";
  for label in labels:
    fields += ", %s" % label;
    poses  += ", ?";
  sqlstr = "INSERT INTO " + tb_name + " (" + fields + ") VALUES (" + poses + ");";
  print sqlstr;
  curs.executemany(sqlstr, to_db)
  conn.commit()

# Check if the database exists(create if not)
def check_db(db_path, tb_name, imlist, labels):
  if not os.path.exists(db_path):
    print "Initializing Database..."
    initdb(db_path, tb_name, imlist, labels.split());
    print "Database Initialized!"

# Load configuration
def load_cfg(cfg_path):
  config = ConfigParser.RawConfigParser()
  try:
    config.read(cfg_path);
    db_path  = config.get('common', 'db_path');
    tb_name  = config.get('common', 'tb_name');
    lst_path = config.get('common', 'lst_path');
    labels   = config.get('common', 'labels');
  except:
    perr("Invalid Configuration File!\n");
    sys.exit(1);
  
  with open(lst_path) as lst_file:
    imlist = [line.strip() for line in lst_file if len(line.strip()) > 0];

  return (db_path, tb_name, imlist, labels);

