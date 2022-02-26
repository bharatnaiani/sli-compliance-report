# sli-compliance-status-report

## About
This repository contains code to generate and send the monthly status report of SLI.

## Setting up local environment

1. Install serverless framework
```
Refer [Serverless Installation Documentation](https://www.serverless.com/framework/docs/getting-started#install-as-a-standalone-binary) for installation instructions.

```
2. Install Required serverless plugins
```
serverless plugin install -n serverless-python-requirements

```
## Deployment into Development/Test Account


Now to open the serverless.yml file and, add datadog development account API Key, APP Key, TO_EMAIL. 

```yaml
    DD_API_KEY: ""
    DD_APP_KEY: ""
    TO_EMAIL: ""
```
To deploy into development account use following command:

```bash
sls deploy -s dev
```
## Deployment into Production Account


Now to open the serverless.yml file and at line 18, add datadog production account API Key

```yaml
    DD_API_KEY: ""
    DD_APP_KEY: ""
    TO_EMAIL: ""
```

To deploy into development account use following command:

```bash
sls deploy -s production
```


## Environment Variables
| Name            | Description                                 |
|-----------------|---------------------------------------------|
| DATADOG_API_KEY | API Key of Datadog                          |
| DATADOG_APP_KEY | APP Key of Datadog                          |
| FROM_EMAIL      | sender's email-id                           |
| TO_EMAIL        | comma-separated list of recipient email-ids |

