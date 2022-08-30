#!/usr/bin/env bash

set -e -u -x

SB=~/sandbox/sandbox
GOAL="${SB} goal"

# Get two prefunded accounts from sandbox
ACCT1=$(${GOAL} account list \
    | head -n 1 \
    | awk '{print $3}' \
    | tr -d '\r')
ACCT2=$(${GOAL} account list \
    | head -n 2 \
    | tail -n 1 \
    | awk '{print $3}' \
    | tr -d '\r')

# Populate existing IDs if you don't want to deploy new apps
APP_ID=
TARGET_ID=

# Generate Main App and Target TEAL
python3 contracts.py

if [ -z ${APP_ID:+x} ]; then
    ${SB} copyTo approval.teal
    ${SB} copyTo clear.teal

    # Deploy Main App
    APP_ID=$(${GOAL} app method \
        --create \
        --from ${ACCT1} \
        --method "deploy()void" \
        --approval-prog approval.teal \
        --clear-prog clear.teal \
        --global-byteslices 0 --global-ints 0 \
        --local-byteslices 0 --local-ints 0 \
        | grep 'Created app with app index' \
        | awk '{print $6}' \
        | tr -d '\r')
fi;

if [ -z ${TARGET_ID:+x} ]; then
    ${SB} copyTo target_approval.teal
    ${SB} copyTo target_clear.teal

    # Deploy Target
    TARGET_ID=$(${GOAL} app method \
        --create \
        --from ${ACCT1} \
        --method "target_deploy()void" \
        --approval-prog target_approval.teal \
        --clear-prog target_clear.teal \
        --global-byteslices 0 --global-ints 0 \
        --local-byteslices 0 --local-ints 0 \
        | grep 'Created app with app index' \
        | awk '{print $6}' \
        | tr -d '\r')
fi

# "message" using Main App
${GOAL} app method \
--from ${ACCT1} \
--app-id ${APP_ID} \
--method "message(account,string)void" \
--arg ${ACCT2} \
--arg '"Hello World"' \
--fee 2000

# "call" Target App using Main App
${GOAL} app method \
    --from ${ACCT1} \
    --app-id ${APP_ID} \
    --method "call(application)void" \
    --arg ${TARGET_ID} \
    --fee 2000
