# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging
from typing import Dict, List

import boto3
from mypy_boto3_dynamodb import ServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from crhelper import CfnResource


logger = logging.getLogger(__name__)
helper = CfnResource()
try:
    ## Init code goes here
    ddb: ServiceResource = boto3.resource('dynamodb')
except Exception as e:
    helper.init_failure(e)


@helper.create
@helper.update
def populate_data(event: Dict, _):
    """
    Create DynamoDB Items from Event.

    Parameters
    ----------
    event : CloudFormation Custom Resource event dict.
        
        event[TableName]: (Required) (String)        Name of DynamoDB Table
        event[Items]:     (Required) (List[Dict]) Items to be added to DynamoDB

    context : AWS Lambda Context.

    Returns
    -------
    NumChangedItems : (Int) Number of Items affected by the resource

    """
    logger.info('Creating Resource')

    # Create DynamoDB item over here
    resource_id = event['LogicalResourceId']
    event_detail = event['ResourceProperties']
    event_detail['status'] = 'NEW'
    data = event_detail['Items']
    logger.info(f"data: {data}")
    table_name = event_detail['TableName']
    logger.info(f"table_name: {table_name}")

    ddb_table: Table = ddb.Table(table_name)

    # TODO: Implement option to load from S3 instead
    num_items = load_from_items(ddb_table, data)

    helper.Data.update({"NumChangedItems": num_items})
    return resource_id


@helper.delete
def no_op(event: dict, _):
    """Delete handler is not implemented yet;
    """
    resource_id = event['LogicalResourceId']

    return resource_id


def load_from_items(ddb_table: Table, data: List[Dict]):
    num_items = len(data)

    # TODO: Add check for success adding item, count failues and report to helper.Data
    for i, item in enumerate(data, start=1):
        logger.info(f"Adding item {i} of {num_items} to DynamoDB")

        response = ddb_table.put_item(Item=item)
        http_status_code = response['ResponseMetadata']['HTTPStatusCode']

        logger.info(f"Stored item in DynamoDB; responded with status code {http_status_code}")

    return num_items


def lambda_handler(event: dict, _):
    logger.info(event)
    helper(event, _)
