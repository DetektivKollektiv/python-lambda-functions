#!/bin/bash

pip install awscli-local
pip install localstack

localstack start
awslocal ses verify-email-identity --email-address no-reply@codetekt.org