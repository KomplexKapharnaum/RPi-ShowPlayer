# -*- coding: utf-8 -*-
#
#
# URL: https://highpush.hcnx.eu/api

import urllib
import urllib2
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom
from _classes import module
from modules import link, exposesignals
from engine.setting import settings
from engine.log import init_log
from engine.threads import patcher
from engine.fsm import Flag
from libs.unidecode import unidecode
log = init_log("sms")

URL = settings.get("sms", "server")
ACCOUNT = settings.get("sms", "account")
PASSWORD = settings.get("sms", "password")
DESTFILE = settings.get_path("sms_destlist")
SEND = settings.get("sms", "send")


############
## XML Maker
############
def makeXmlPush(destinataires, text, name="DO NOT CLEAN", mode=1, pretty=False):

    # PUSH
    push = Element('push', {'accountid':    ACCOUNT,
                            'password':     PASSWORD,
                            'email':        "pierre.hoezelle@gmail.com",
                            'class_type':   "{0}".format(mode),
                            'name':         "{0}".format(name),
                            'userdata':     "DNC",
                            'datacoding':   "8",            # 8: UTF-8
                            'start_date':   "2000-01-01",   # Avec une date dans le passé on tombe à ~ 5 secondes de délai d'envoi
                            'start_time':   "00:00"         # Avec une date dans le passé on tombe à ~ 5 secondes de délai d'envoi
                            })

    # COMMENT
    comment = Comment('Generated for DNC')
    push.append(comment)

    ## MESSAGE 
    message = SubElement(push, 'message', {'class_type': "{0}".format(mode)}) # Class Type : 0 = Flash // 1 = Normal
    content = SubElement(message, 'text')
    content.text = text.decode("ascii").encode("utf-8")
    for num in destinataires:
        to = SubElement(message, 'to', {'ret_id': "TO_"+num})
        to.text = num

    # ADD STUFFS
    rough_string = ElementTree.tostring(push, 'utf-8')

    if not pretty:
        return '<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE push SYSTEM "push.dtd">'+rough_string

    reparsed = minidom.parseString(rough_string).toprettyxml(indent="  ")
    return reparsed.replace('<?xml version="1.0" ?>',
                                  '<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE push SYSTEM "push.dtd">')


######################
## POST Request sender
######################
def post(url, xml):
    param_data = {'xml': xml}
    req = urllib2.Request(url, data=urllib.urlencode(param_data))
    return urllib2.urlopen(req).read()


def uniquify(seq): 
   # order preserving
   seen = {}
   result = []
   for item in seq:
       if item in seen: continue
       seen[item] = 1
       result.append(item)
   return result


##################
## MAIN SendSms function
##################
def sendSMS(message):
    with open(DESTFILE) as f:
        destinataires = [d.strip() for d in f.read().splitlines() if d.strip() and d[0] != '#' and d.strip()]
        destinataires = uniquify(destinataires)

    message = message.strip() if message is not None else ""
    if len(message) > 0:
        if len(destinataires) > 0:
            ans = ""
            if SEND:
                ans = post(URL, makeXmlPush(destinataires, message))
            else:
                ans = "disable"
            ans = '{0}'.format(ans)
            if ans.isdigit():
                log.log('important', 'SMS sent successfully with code: {0}'.format(ans))
                patcher.patch(Flag('SMS_SENT').get())
            else:
                log.warning('SMS failed to send: {0}'.format(ans))
                if ans == 'BAD PASSWORD':
                    log.warning('Don\'t forget to set password in the local config file! (sms->password)')
        else:
            log.warning('Can\'t send SMS, no dest found in {0}'.format(DESTFILE))
    else:
        log.warning('Can\'t send SMS with Empty message..')




exposesignals({'SMS_SENT': [True]}) 


# ETAPE AND SIGNALS
@module('SmsSender')
@link({"/sms/sendsms [message]": "sms_send"})
def sms_machine(flag, **kwargs):
    pass

@link({None: "sms_machine"})
def sms_send(flag, **kwargs):
    message = flag.args["message"] if 'message' in flag.args else ""
    sendSMS(message)

