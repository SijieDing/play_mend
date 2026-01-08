#!/bin/sh

########################################################################################
# Validate libs/aiops_unite_pkg/aiops_unite/sample-config.yaml KPI list

SCRIPT_PATH=$(dirname "$0")
ROOT_PATH=$(cd "${SCRIPT_PATH}" && cd ../.. && pwd)
CONFIG_PATH="${ROOT_PATH}/libs/aiops_unite_pkg/aiops_unite/sample-config.yaml"

###################### Calculate size of KPIs ######################
KPI_LENGTH=$(yq -r '.metrics | length' < "${CONFIG_PATH}")
echo ">>>> There are total ${KPI_LENGTH} KPIs"
echo

###################### Get duplicated entries ######################
FULL_KPIS=$(yq -r '.metrics[] .name' < "${CONFIG_PATH}")
echo ">>>> These KPIs have duplicated entries:"
echo "${FULL_KPIS}" | sort | uniq -d
echo

# current output:
# - attributes.com.ibm.zou.metrics.MAX_CSA_FREE: fixed
# - attributes.com.ibm.zou.metrics.allocation
# - attributes.com.ibm.zou.metrics.average_cpu_percent: fixed
# - attributes.com.ibm.zou.metrics.cpc_dispatch_time
# - attributes.com.ibm.zou.metrics.four_hour_msus: fixed
# - attributes.com.ibm.zou.metrics.in_use
# - attributes.com.ibm.zou.metrics.sos
# - attributes.com.ibm.zou.metrics.storage_in_use_8
# - attributes.com.ibm.zou.metrics.total_srb_pct: fixed
# - attributes.com.ibm.zou.metrics.total_tcb_pct: fixed
# - attributes.com.ibm.zou.metrics.total_times_sos


###################### Get duplicated entries ######################
# This list should be synced with:
# https://github.ibm.com/z-aiops-unite/agent-controller/blob/develop/src/agent-deploy/otel-collector/processors/cumulative-to-interval-processort.ts
ACCUMULATIVE_KPIS="com.ibm.zou.metrics.SCH_SMB_LOOKED_AT
com.ibm.zou.metrics.SCH_SMB_OTHER
com.ibm.zou.metrics.SCH_SMB_PGM_CONFL
com.ibm.zou.metrics.LOGL_AWES_ON_WRITE
com.ibm.zou.metrics.LOGL_CHKW_REQUESTS
com.ibm.zou.metrics.LOGL_CURR_SEQ_NO
com.ibm.zou.metrics.LOGL_WTBF_CHKPT
com.ibm.zou.metrics.LOGL_WTBF_NOTCHKPT
com.ibm.zou.metrics.LOGL_WTWT_REQUESTS
com.ibm.zou.metrics.PHYL_INTERNAL_CHKW
com.ibm.zou.metrics.PHYL_OLDS_READS
com.ibm.zou.metrics.PHYL_OLDS_WRITES
com.ibm.zou.metrics.PHYL_WADS_EXCPVR
com.ibm.zou.metrics.PHYL_WADS_2K_SEG
com.ibm.zou.metrics.PHYL_WTWT_TIME
com.ibm.zou.metrics.QP_BUFFER_REPOS
com.ibm.zou.metrics.QP_BUFFER_LOCKED
com.ibm.zou.metrics.QP_BUFFER_UNLOCK
com.ibm.zou.metrics.QP_BUFFER_WAITS
com.ibm.zou.metrics.QP_DECB_READ_WAITS
com.ibm.zou.metrics.QP_DECB_WRITEWAITS
com.ibm.zou.metrics.QP_ENQDEQ_BFRWAITS
com.ibm.zou.metrics.QP_ILOG_WAITS
com.ibm.zou.metrics.QP_IO_ERROR_NORET
com.ibm.zou.metrics.QP_MSG_CANCELS
com.ibm.zou.metrics.QP_MSG_DEQUEUES
com.ibm.zou.metrics.QP_MSG_ENQUEUES
com.ibm.zou.metrics.QP_PCB_UNCHAINS
com.ibm.zou.metrics.QP_PURGE_REQUESTS
com.ibm.zou.metrics.QP_PURGE_WAITS
com.ibm.zou.metrics.QP_PURGE_WRITES
com.ibm.zou.metrics.QP_QMGR_LOC_ALTERS
com.ibm.zou.metrics.QP_QMGR_LOCATES
com.ibm.zou.metrics.QP_QMGR_RELEASES
com.ibm.zou.metrics.QP_READ_REQUESTS
com.ibm.zou.metrics.QP_TRANSLATE_REQ
com.ibm.zou.metrics.QP_WAIT_REQUESTS
com.ibm.zou.metrics.QP_WRITE_REQUESTS
com.ibm.zou.metrics.DDF_SRB_TIME
com.ibm.zou.metrics.DDF_TCB_TIME
com.ibm.zou.metrics.DSAS_SRB_TIME
com.ibm.zou.metrics.DSAS_TCB_TIME
com.ibm.zou.metrics.IRLM_SRB_TIME
com.ibm.zou.metrics.IRLM_TCB_TIME
com.ibm.zou.metrics.PRMPT_SRB
com.ibm.zou.metrics.PRMPT_SRB_ZIIP
com.ibm.zou.metrics.SSAS_SRB_TIME
com.ibm.zou.metrics.SSAS_TCB_TIME
com.ibm.zou.metrics.ACC_QU_INAC_THR_T2
com.ibm.zou.metrics.CONV_DEALLOC
com.ibm.zou.metrics.DBAT_QUEUED
com.ibm.zou.metrics.DBATS_INACTIVE
com.ibm.zou.metrics.TERM_COUNT
com.ibm.zou.metrics.LATCH_LC01
com.ibm.zou.metrics.LATCH_LC02
com.ibm.zou.metrics.LATCH_LC03
com.ibm.zou.metrics.LATCH_LC04
com.ibm.zou.metrics.LATCH_LC05
com.ibm.zou.metrics.LATCH_LC06
com.ibm.zou.metrics.LATCH_LC07
com.ibm.zou.metrics.LATCH_LC08
com.ibm.zou.metrics.LATCH_LC09
com.ibm.zou.metrics.LATCH_LC10
com.ibm.zou.metrics.LATCH_LC11
com.ibm.zou.metrics.LATCH_LC12
com.ibm.zou.metrics.LATCH_LC13
com.ibm.zou.metrics.LATCH_LC14
com.ibm.zou.metrics.LATCH_LC15
com.ibm.zou.metrics.LATCH_LC16
com.ibm.zou.metrics.LATCH_LC17
com.ibm.zou.metrics.LATCH_LC18
com.ibm.zou.metrics.LATCH_LC19
com.ibm.zou.metrics.LATCH_LC20
com.ibm.zou.metrics.LATCH_LC21
com.ibm.zou.metrics.LATCH_LC22
com.ibm.zou.metrics.LATCH_LC23
com.ibm.zou.metrics.LATCH_LC24
com.ibm.zou.metrics.LATCH_LC25
com.ibm.zou.metrics.LATCH_LC254
com.ibm.zou.metrics.LATCH_LC26
com.ibm.zou.metrics.LATCH_LC27
com.ibm.zou.metrics.LATCH_LC28
com.ibm.zou.metrics.LATCH_LC29
com.ibm.zou.metrics.LATCH_LC30
com.ibm.zou.metrics.LATCH_LC31
com.ibm.zou.metrics.LATCH_LC32
com.ibm.zou.metrics.CHANGE_REQ
com.ibm.zou.metrics.CLAIM_REQUESTS
com.ibm.zou.metrics.CLAIMS_FAILED
com.ibm.zou.metrics.DEADLOCK
com.ibm.zou.metrics.DRAIN_REQUESTS
com.ibm.zou.metrics.DRAINS_FAILED
com.ibm.zou.metrics.LOCK_REQUESTS
com.ibm.zou.metrics.OTHER_REQ
com.ibm.zou.metrics.QUERY_REQ
com.ibm.zou.metrics.SUSPENSION_LOCK
com.ibm.zou.metrics.SUSPENSION_OTHER
com.ibm.zou.metrics.SUSP_IRLM_LATCH
com.ibm.zou.metrics.TIMEOUT
com.ibm.zou.metrics.ACTIVE_CI_CREATED
com.ibm.zou.metrics.LOG_CI_WRITTEN
com.ibm.zou.metrics.LOG_WRITE_IO_REQ
com.ibm.zou.metrics.PAR_GROUPS_EXEC
com.ibm.zou.metrics.timeouts"

echo ">>>> These accumulative KPIs are used with \"_NORMALIZED\" suffix:"
found=false
while IFS= read -r KPI; do
    FIND_KPI=$(yq -r ".metrics[] | select(.name == \"attributes.${KPI}\")" < "${CONFIG_PATH}")
    if [ -n "${FIND_KPI}" ]; then
        echo "- ${KPI}"
        found=true
    fi
done <<< "${ACCUMULATIVE_KPIS}"
if [ "${found}" == "false" ]; then
    echo "- <None>"
fi
echo

# This file should be exported from event.advisory table with pgAdmin
ADVISORY_TABLE_UPGRADE_FILE="${SCRIPT_PATH}/advisory_FP4_20251209.csv"
echo ">>>> Validate KPI advisory table (${ADVISORY_TABLE_UPGRADE_FILE}):"
advisory_lines=$(grep "Metric .\+ is .\+ than usual on" ${ADVISORY_TABLE_UPGRADE_FILE})
KPIs_UC=""
CDP_KPIs=""
KPIs_NORMALIZED=""
KPIs_NOT_DEFINED=""
FIX_SQLs=""
while IFS= read -r advisory_line; do
    # echo "- ${advisory_line}"
    pattern="\"Metric ([^\"]+) is (lower|higher) than usual on ([^\"]+)\""
    extracted_vars=$(echo "${advisory_line}" | grep -E "${pattern}" | sed -E "s/.*${pattern}.*/\1,\2,\3/")
    echo "- ${extracted_vars}"
    kpi=$(echo "${extracted_vars}" | awk -F ',' '{ print $1 }')
    anomaly_direction=$(echo "${extracted_vars}" | awk -F ',' '{ print $2 }')
    resource_type=$(echo "${extracted_vars}" | awk -F ',' '{ print $3 }')
    if [ -z "${kpi}" -o -z "${resource_type}" ]; then
        echo "  💔 Failed to parse ${advisory_line}"
    else
        kpi_uc=$(echo "${kpi}" | tr '[:lower:]' '[:upper:]')
        # yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi}\")" "${CONFIG_PATH}"
        kpi_object=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi}\")" < "${CONFIG_PATH}")
        kpi_normalized_object=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi}_NORMALIZED\")" < "${CONFIG_PATH}")
        kpi_object_uc=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi_uc}\")" < "${CONFIG_PATH}")
        kpi_normalized_object_uc=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi_uc}_NORMALIZED\")" < "${CONFIG_PATH}")
        if [ -n "${kpi_object}" ]; then
            # found exact match
            KPIs_UC="${KPIs_UC}\n${kpi_uc}"

            expected_resource_type=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi}\") | .conditions.[\"resource.com.ibm.zou.resource_type\"]" < "${CONFIG_PATH}")
            # resource_type = re.sub(r"(CICS|MQ|DB2|JVM|TCPIP|[A-Z][a-z])", r" \1", cond_val).lstrip()
            expected_resource_type_normalized=$(echo "${expected_resource_type}" | head -n 1 | sed 's/\([A-Z][a-z]\)/ \1/g' | sed 's/^[ \t]*//')
            if [ "${expected_resource_type_normalized}" != "${resource_type}" ]; then
                echo "  🛑 Resource type \"${resource_type}\" is not as expected to be \"${expected_resource_type_normalized}\""

                sql="UPDATE event.advisory SET situation_name='Metric ${kpi} is ${anomaly_direction} than usual on ${expected_resource_type_normalized}', description='Anomaly detected: Metric ${kpi} is ${anomaly_direction} than usual on ${expected_resource_type_normalized}' WHERE situation_name='Metric ${kpi} is ${anomaly_direction} than usual on ${resource_type}';"
                FIX_SQLs="${FIX_SQLs}\n${sql}"
            else
                echo "  ✅"
            fi
        elif [ -n "${kpi_object_uc}" ]; then
            # found but in wrong letter case
            KPIs_UC="${KPIs_UC}\n${kpi_uc}"
            CDP_KPIs="${CDP_KPIs}\n${kpi}"
            echo "  👎 CDP KPI with lower case"

            expected_resource_type=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi_uc}\") | .conditions.[\"resource.com.ibm.zou.resource_type\"]" < "${CONFIG_PATH}")
            # resource_type = re.sub(r"(CICS|MQ|DB2|JVM|TCPIP|[A-Z][a-z])", r" \1", cond_val).lstrip()
            expected_resource_type_normalized=$(echo "${expected_resource_type}" | head -n 1 | sed 's/\([A-Z][a-z]\)/ \1/g' | sed 's/^[ \t]*//')
            if [ "${expected_resource_type_normalized}" != "${resource_type}" ]; then
                echo "  🛑 Resource type \"${resource_type}\" is not as expected to be \"${expected_resource_type_normalized}\""
            fi

            sql="UPDATE event.advisory SET situation_name='Metric ${kpi_uc} is ${anomaly_direction} than usual on ${expected_resource_type_normalized}', description='Anomaly detected: Metric ${kpi_uc} is ${anomaly_direction} than usual on ${expected_resource_type_normalized}' WHERE situation_name='Metric ${kpi} is ${anomaly_direction} than usual on ${resource_type}';"
            FIX_SQLs="${FIX_SQLs}\n${sql}"
        elif [ -n "${kpi_normalized_object}" ]; then
            # found same KPI but it's normalized
            KPIs_UC="${KPIs_UC}\n${kpi_uc}_NORMALIZED"
            KPIs_NORMALIZED="${KPIs_NORMALIZED}\n${kpi}"
            echo "  🔶 KPI is normalized"
            
            expected_resource_type=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi}_NORMALIZED\") | .conditions.[\"resource.com.ibm.zou.resource_type\"]" < "${CONFIG_PATH}")
            # resource_type = re.sub(r"(CICS|MQ|DB2|JVM|TCPIP|[A-Z][a-z])", r" \1", cond_val).lstrip()
            expected_resource_type_normalized=$(echo "${expected_resource_type}" | head -n 1 | sed 's/\([A-Z][a-z]\)/ \1/g' | sed 's/^[ \t]*//')
            if [ "${expected_resource_type_normalized}" != "${resource_type}" ]; then
                echo "  🛑 Resource type \"${resource_type}\" is not as expected to be \"${expected_resource_type_normalized}\""
            fi

            sql="UPDATE event.advisory SET situation_name='Metric ${kpi}_NORMALIZED is ${anomaly_direction} than usual on ${expected_resource_type_normalized}', description='Anomaly detected: Metric ${kpi}_NORMALIZED is ${anomaly_direction} than usual on ${expected_resource_type_normalized}' WHERE situation_name='Metric ${kpi} is ${anomaly_direction} than usual on ${resource_type}';"
            FIX_SQLs="${FIX_SQLs}\n${sql}"
        elif [ -n "${kpi_normalized_object_uc}" ]; then
            # found but in wrong letter case
            KPIs_UC="${KPIs_UC}\n${kpi_uc}_NORMALIZED"
            CDP_KPIs="${CDP_KPIs}\n${kpi}"
            echo "  👎 CDP KPI with lower case"
            KPIs_NORMALIZED="${KPIs_NORMALIZED}\n${kpi}"
            echo "  🔶 KPI is normalized"

            expected_resource_type=$(yq -r ".metrics[] | select(.name == \"attributes.com.ibm.zou.metrics.${kpi_uc}_NORMALIZED\") | .conditions.[\"resource.com.ibm.zou.resource_type\"]" < "${CONFIG_PATH}")
            # resource_type = re.sub(r"(CICS|MQ|DB2|JVM|TCPIP|[A-Z][a-z])", r" \1", cond_val).lstrip()
            expected_resource_type_normalized=$(echo "${expected_resource_type}" | head -n 1 | sed 's/\([A-Z][a-z]\)/ \1/g' | sed 's/^[ \t]*//')
            if [ "${expected_resource_type_normalized}" != "${resource_type}" ]; then
                echo "  🛑 Resource type \"${resource_type}\" is not as expected to be \"${expected_resource_type_normalized}\""
            fi

            sql="UPDATE event.advisory SET situation_name='Metric ${kpi_uc}_NORMALIZED is ${anomaly_direction} than usual on ${expected_resource_type_normalized}', description='Anomaly detected: Metric ${kpi_uc}_NORMALIZED is ${anomaly_direction} than usual on ${expected_resource_type_normalized}' WHERE situation_name='Metric ${kpi} is ${anomaly_direction} than usual on ${resource_type}';"
            FIX_SQLs="${FIX_SQLs}\n${sql}"
        else
            # KPI not found
            KPIs_NOT_DEFINED="${KPIs_NOT_DEFINED}\n${kpi}"
            echo "  ❌ KPI doesn't exist in DS config"
        fi
    fi
done <<< "${advisory_lines}"
echo

echo "- Below are CDP KPIs with wrong letter case:"
echo "${CDP_KPIs}" | sort | uniq -d
echo

echo "- Below KPIs are not defined in DS config:"
echo "${KPIs_NOT_DEFINED}" | sort | uniq -d
echo

echo "- SQLs to fix issues:"
echo "${FIX_SQLs}"
echo

echo "- Below KPIs don't have advisory:"
ANOMALY_DETECTION_KPIs=$(yq -r ".metrics[] | .name" < "${CONFIG_PATH}")
while IFS= read -r kpi_full; do
    kpi=$(echo "${kpi_full}" | awk -F '.' '{ print $6 }')
    kpi_uc=$(echo "${kpi}" | tr '[:lower:]' '[:upper:]')
    kpi_match=$(echo "${KPIs_UC}" | grep -F -x "${kpi_uc}")
    if [ -z "${kpi_match}" ]; then
        echo "${kpi} ❌"
    # else
    #     echo "${kpi} ✅"
    fi
done <<< "${ANOMALY_DETECTION_KPIs}"
