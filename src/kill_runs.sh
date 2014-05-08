#!/bin/bash

ps aux | grep get_all_stats | grep python  
kill -9 $(ps aux | grep get_all_stats | grep python | awk '{print $2}')
ps aux | grep calculate_stats | grep python
kill -9 $(ps aux | grep calculate_stats | grep python | awk '{print $2}')
ps aux | grep run | grep bash 
kill -9 $(ps aux | grep run | grep bash | awk '{print $2}')
