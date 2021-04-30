from datadog import initialize, api
import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
import os
import logging
import requests
import boto3
import json
from premailer import transform
logging.basicConfig(format='%(levelname)s - %(message)s')
logger=logging.getLogger()
logger.setLevel(logging.INFO)
email_template_dictionary = {}

def initialize_datadog_api_module():
    options = {
        'api_key': os.environ["DD_API_KEY"],
        'app_key': os.environ["DD_APP_KEY"],
        'api_host': 'https://api.datadoghq.eu/'
    }
    initialize(**options)
    logger.info("Initialized and configured datadog api module")

def sli_report():
    now=int(time.time())
    environ=os.environ["ENVIRONMENT_NAME"]
    metrics=[{
        "title": "Success Rate",
        "query": "100-((count:ambassador_access_logs.distribution{status_code:4*,*,*,*,*,environment:"+environ+"}.as_count()+count:ambassador_access_logs.distribution{status_code:5*,*,*,*,*,environment:"+environ+"}.as_count())/count:ambassador_access_logs.distribution{status_code:*,*,*,*,*,environment:"+environ+"}.as_count())"
    },{
        "title": "Percentage of 2XX requests",
        "query": "count:ambassador_access_logs.distribution{status_code:2*,*,*,*,*,environment:"+environ+"}.as_count()/count:ambassador_access_logs.distribution{status_code:*,*,*,*,*,environment:"+environ+"}.as_count()*100"
    },{
         "title": "Percentage of 5XX requests",
         "query": "count:ambassador_access_logs.distribution{status_code:5*,*,*,*,*,environment:"+environ+"}.as_count()/count:ambassador_access_logs.distribution{status_code:*,*,*,*,*,environment:"+environ+"}.as_count()*100"
    },{
        "title": "Percentage of 4XX requests",
        "query": "count:ambassador_access_logs.distribution{status_code:4*,*,*,*,*,environment:"+environ+"}.as_count()/count:ambassador_access_logs.distribution{status_code:*,*,*,*,*,environment:"+environ+"}.as_count()*100"
    },{
        "title": "Percentage of 3XX requests",
        "query": "count:ambassador_access_logs.distribution{status_code:3*,*,*,*,*,environment:"+environ+"}.as_count()/count:ambassador_access_logs.distribution{status_code:*,*,*,*,*,environment:"+environ+"}.as_count()*100"
    } ]
    for metric in metrics:
        result = api.Metric.query(start=now - 2592000, end=now, query=metric["query"])
        total_len = len(result['series'][0]["pointlist"])
        total = sum(pointlist[1] for pointlist in result['series'][0]["pointlist"])
        value = total / total_len
        metric["result"]=round(value, 2)
    return metrics

def render_email_template(email_template_dictionary):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    template = env.get_template('email_template.html')
    html_template = template.render(email_template_dict=email_template_dictionary)
    logger.info("Rendered email template successfully!!")
    html_template = transform(html_template)
    return html_template

def send_email(html_template):
    SENDER = os.environ["FROM_EMAIL"]
    RECIPIENT = os.environ["TO_EMAIL"]
    SUBJECT = "SLI Compliance Report"
    BODY_HTML = html_template
    SMTP_USERNAME = os.environ["USERNAME"]
    SMTP_PASSWORD = os.environ["PASSWORD"]
    HOST = os.environ["HOST"]         
    PORT = 587 
    CHARSET = "UTF-8"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    part1 = MIMEText(BODY_HTML, 'html')
    msg.attach(part1)
    try:
        #Provide the contents of the email.
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        #stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()
    except ClientError as e:
        logger.error("Error: ", e)
    else:
        logger.info("Email sent! Message ID:")

def lambda_handler(event,context):
    try:
        initialize_datadog_api_module()
        template_dictionary=sli_report()
        template=render_email_template(template_dictionary)
        send_email(template)
        return True
    except Exception as error:
        logger.error("An error occurred while sending a monthly SLI compliance status report: {}".format(error))
        return False