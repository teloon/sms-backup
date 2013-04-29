#!/usr/bin/env python
#-*- coding:utf8 -*-

"""
    crawl sms backup from 123.163.com
    output format:
                DAY
                NAME\tPHONE\tTIME\tTYPE\tMSG
                NAME\tPHONE\tTIME\tTYPE\tMSG
                ...
                DAY
                ...
        TYPE: 0 for send, 1 for reveive

    TODO: wait for page to finish loading
"""

import re
import time
from splinter import Browser

URL_LOGIN = 'http://123.163.com/webmail/home/'
URL_SMS = 'http://123.163.com/webmail/main/#mid=7'

def get_page_num(bsr):
    txt = bsr.find_by_tag("select")[-1].text
    #print txt.encode("utf8")
    return len(txt.split("/")) - 1

def crawl(usr, pswd, out_path, driver="firefox"):
    bsr = Browser(driver)
    bsr.visit(URL_LOGIN)
    bsr.find_by_id("phone1").fill(usr)
    bsr.find_by_id("pswd").fill(pswd)
    bsr.find_by_id("login").click()
    if bsr.is_element_present_by_css("span.fw1.fs0.acnt"):
        print "Successfully login!"
    else:
        print "Login failed, bye!"
    bsr.visit("http://123.163.com/webmail/main/#mid=7")
    while bsr.is_element_not_present_by_css("div.list-time"):
        print "sleeping"
        time.sleep(1)
    bsr.find_by_css("span.iblock.icn-msg.list-icon.potr")[0].click()
    page_num = get_page_num(bsr)
    with open(out_path, "w") as out_f:
        for pi in xrange(page_num):
            print "Page %d/%d" % (pi+1, page_num)
            date_lst = bsr.find_by_css("div.list-time")
            date_msgs_lst = bsr.find_by_css("div.sms-item")
            #HACK for scrolling the sms list down because of AJAX-style of showing sms
            date_lst[-1].right_click()
            msg_i = 0
            for di in xrange(len(date_lst)):
                date = date_lst[di].text.strip().split()[0]
                msg_num_mat = re.findall(r"\(\s*(\d+).\s*\)", date_lst[di].text)
                msg_num = int(msg_num_mat[0])
                out_f.write("%s\t%d\n" % (date, msg_num))
                for _ in range(msg_num):
                    name_obj = date_msgs_lst[msg_i].find_by_css("span.js-cnt.name")[0]
                    phone_obj = date_msgs_lst[msg_i].find_by_css("span.js-cnt.fc2")[0]
                    time_obj = date_msgs_lst[msg_i].find_by_css("div.fr.w6.js-cnt.bm-hack-w6")[0]
                    msg_obj = date_msgs_lst[msg_i].find_by_css("div.w4")[0]
                    type_obj = date_msgs_lst[msg_i].find_by_css("div.fl.w3.thide.fc5")[0]
                    out_f.write("%s\t%s\t%s\t%s\t%s\n" % (name_obj.html.encode("utf8"), \
                                                            phone_obj.html.strip("() ").encode("utf8"), \
                                                            time_obj.text.encode("utf8"), \
                                                            "0" if type_obj.visible else "1", \
                                                            msg_obj.text.encode("utf8")))
                    msg_i += 1
            #next page
            next_page_link = bsr.find_by_css("div.fr.pager")[0].find_by_tag("a")[2]
            next_page_link.click()

if __name__ == '__main__':
    usr = raw_input("User name:")
    pswd = raw_input("Password:")
    out_path = raw_input("Backup output path:")
    crawl(usr, pswd, out_path)

