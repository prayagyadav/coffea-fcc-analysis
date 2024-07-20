#!/usr/bin/bash
condor_submit submit_0.sh
sleep 5
condor_submit submit_1.sh
sleep 5
condor_submit submit_2.sh
sleep 5
condor_submit submit_3.sh
sleep 5
