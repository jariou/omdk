#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
``generate_losses.py`` is an executable script which, given Oasis files,
model analysis settings JSON file, model data, and some other
parameters, can generate losses using the installed ktools framework.
The script can be called directly from the command line given the
following arguments (in no particular order)

::

    ./generate_losses.py -o /path/to/oasis/files
                         -j /path/to/analysis/settings/json/file
                         -m /path/to/model/data
                         -r /path/to/model/run/directory
                         [-s <ktools script name (without file extension)>]
                         [-n <number of ktools calculation processes to use>]
                         [--execute | --no-execute]

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The ktools script name should not contain any filetype
extension, and the model run directory can be placed anywhere in the
parent folder common to ``omdk`` and the model keys server repository.

The script creates a time-stamped folder in the model run directory and
sets that as the new model run directory, copies the analysis settings
JSON file into the run directory and creates the following folder
structure

::

    ├── analysis_settings.json
    ├── fifo/
    ├── input/
    ├── output/
    ├── static/
    └── work/

Depending on the OS type the model data is symlinked (Linux, Darwin) or
copied (Cygwin, Windows) into the ``static`` subfolder. The input files
are kept in the ``input`` subfolder and the losses are generated as CSV
files in the ``output`` subfolder.

By default executing ``generate_losses.py`` will automatically execute
the ktools losses script it generates. If you don't want this provide
the (optional) ``--no-execute`` argument. The default here is automatic
execution.

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script using the path to this
file using the option ``-f``. In this case the paths should be given
relative to the parent folder in which the model keys server repository
is located.

::

    ./generate_losses.py -f /path/to/model/resources/JSON/config/file'

The JSON file should contain the following keys (in no particular order)

::

    "oasis_files_path"
    "analysis_settings_json_file_path"
    "model_data_path"
    "model_run_dir_path"
    "ktools_script_name"
    "ktools_num_processes"
    "execute"

and the values of the path-related keys should be string paths, given
relative to the parent folder in which the model keys server repository
is located. The JSON file is usually placed in the model keys server
repository. The value of the (optional) ``"exectute"`` key should be
either ``true`` or ``false`` depending on whether you want the generated
ktools losses scripts to be automatically executed or not. The default
here is automatic execution.
"""

import argparse
import io
import json
import logging
import os
import subprocess
import sys

from oasis_utils import (
    create_binary_files,
    get_utctimestamp,
    OasisException,
    oasis_log_utils,
    prepare_model_run_directory,
    prepare_model_run_inputs,
)

import utils as mdk_utils

pid_monitor_count = 0
apid_monitor_count = 0
lpid_monitor_count = 0
kpid_monitor_count = 0
command_file = ""


def print_command(cmd):
    with io.open(command_file, "a", encoding='utf-8') as myfile:
        myfile.writelines(cmd.decode() + "\n")


def leccalc_enabled(lec_options):
    for option in lec_options["outputs"]:
        if lec_options["outputs"][option]:
            return True
    return False


def do_post_wait_processing(runtype, analysis_settings):
    global apid_monitor_count
    global lpid_monitor_count
    summary_set = 0
    if "{}_summaries".format(runtype) not in analysis_settings:
        return

    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            summary_set = summary["id"]
            if summary.get("aalcalc"):
                apid_monitor_count = apid_monitor_count + 1
                print_command(
                    "aalsummary -K{0}_S{1}_aalcalc > output/{0}_S{1}_aalcalc.csv & apid{2}=$!".format(
                        runtype, summary_set, apid_monitor_count))
            if summary.get("lec_output"):
                if "leccalc" in summary:
                    if leccalc_enabled(summary["leccalc"]):
                        return_period_option = ""
                        if summary["leccalc"]["return_period_file"]:
                            return_period_option = "-r"
                        cmd = "leccalc {} -K{}_S{}_summaryleccalc".format(return_period_option, runtype, summary_set)
                        lpid_monitor_count = lpid_monitor_count + 1
                        for option in summary["leccalc"]["outputs"]:
                            switch = ""
                            if summary["leccalc"]["outputs"][option]:
                                if option == "full_uncertainty_aep":
                                    switch = "-F"
                                if option == "wheatsheaf_aep":
                                    switch = "-W"
                                if option == "sample_mean_aep":
                                    switch = "-S"
                                if option == "full_uncertainty_oep":
                                    switch = "-f"
                                if option == "wheatsheaf_oep":
                                    switch = "-w"
                                if option == "sample_mean_oep":
                                    switch = "-s"
                                if option == "wheatsheaf_mean_aep":
                                    switch = "-M"
                                if option == "wheatsheaf_mean_oep":
                                    switch = "-m"
                                cmd = cmd + " {} output/{}_S{}_leccalc_{}.csv".format(switch, runtype, summary_set, option)
                        cmd = cmd + "  &  lpid{}=$!".format(lpid_monitor_count)
                        print_command(cmd)


def do_fifos(action, runtype, analysis_settings, process_id):

    summary_set = 0
    if "{}_summaries".format(runtype) not in analysis_settings:
        return

    print_command("{} fifo/{}_P{}".format(action, runtype, process_id))
    print_command("")
    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            summary_set = summary["id"]
            print_command(
                "{} fifo/{}_S{}_summary_P{}".format(
                    action, runtype, summary_set, process_id))
            if summary.get("eltcalc"):
                print_command(
                    "{} fifo/{}_S{}_summaryeltcalc_P{}".format(
                        action, runtype, summary_set, process_id))
                print_command(
                    "{} fifo/{}_S{}_eltcalc_P{}".format(
                        action, runtype, summary_set, process_id))
            if summary.get("summarycalc"):
                print_command(
                    "{} fifo/{}_S{}_summarysummarycalc_P{}".format(
                        action, runtype, summary_set, process_id))
                print_command(
                    "{} fifo/{}_S{}_summarycalc_P{}".format(
                        action, runtype, summary_set, process_id))
            if summary.get("pltcalc"):
                print_command(
                    "{} fifo/{}_S{}_summarypltcalc_P{}".format(
                        action, runtype, summary_set, process_id))
                print_command(
                    "{} fifo/{}_S{}_pltcalc_P{}".format(
                        action, runtype, summary_set, process_id))
            if summary.get("aalcalc"):
                print_command(
                    "{} fifo/{}_S{}_summaryaalcalc_P{}".format(
                        action, runtype, summary_set, process_id))

    print_command("")


def create_workfolders(runtype, analysis_settings):

    if "{}_summaries".format(runtype) not in analysis_settings:
        return
    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            summary_set = summary["id"]
            if summary.get("lec_output"):
                if leccalc_enabled(summary["leccalc"]):
                    print_command(
                        "mkdir work/{}_S{}_summaryleccalc".format(
                            runtype, summary_set))
            if summary.get("aalcalc") is True:
                print_command("mkdir work/{}_S{}_aalcalc".format(runtype, summary_set))


def remove_workfolders(runtype, analysis_settings):
    print_command("rm -rf work/kat")
    if "{}_summaries".format(runtype) not in analysis_settings:
        return
    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            summary_set = summary["id"]
            if summary.get("lec_output"):
                if leccalc_enabled(summary["leccalc"]):
                    print_command(
                        "rm work/{}_S{}_summaryleccalc/*".format(
                            runtype, summary_set))
                    print_command(
                        "rmdir work/{}_S{}_summaryleccalc".format(
                            runtype, summary_set))
            if summary.get("aalcalc"):
                print_command(
                    "rm work/{}_S{}_aalcalc/*".format(
                        runtype, summary_set))
                print_command("rmdir work/{}_S{}_aalcalc".format(
                    runtype, summary_set))


def do_make_fifos(runtype, analysis_settings, process_id):
    do_fifos("mkfifo", runtype, analysis_settings, process_id)


def do_remove_fifos(runtype, analysis_settings, process_id):
    do_fifos("rm", runtype, analysis_settings, process_id)


def do_kats(runtype, analysis_settings, max_process_id):
    global kpid_monitor_count
    anykats = False
    if "{}_summaries".format(runtype) not in analysis_settings:
        return anykats

    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            summary_set = summary["id"]
            if summary.get("eltcalc"):
                anykats = True
                cmd = "kat "
                for process_id in range(1, max_process_id + 1):
                    cmd = cmd + "work/kat/{}_S{}_eltcalc_P{} ".format(
                        runtype, summary_set, process_id)
                kpid_monitor_count = kpid_monitor_count + 1
                cmd = cmd + "> output/{}_S{}_eltcalc.csv & kpid{}=$!".format(
                    runtype, summary_set, kpid_monitor_count)
                print_command(cmd)
            if summary.get("pltcalc"):
                anykats = True
                cmd = "kat "
                for process_id in range(1, max_process_id + 1):
                    cmd = cmd + "work/kat/{}_S{}_pltcalc_P{} ".format(
                        runtype, summary_set, process_id)
                kpid_monitor_count = kpid_monitor_count + 1
                cmd = cmd + "> output/{}_S{}_pltcalc.csv & kpid{}=$!".format(
                    runtype, summary_set, kpid_monitor_count)
                print_command(cmd)
            if summary.get("summarycalc"):
                anykats = True
                cmd = "kat "
                for process_id in range(1, max_process_id + 1):
                    cmd = cmd + "work/kat/{}_S{}_summarycalc_P{} ".format(
                        runtype, summary_set, process_id)
                kpid_monitor_count = kpid_monitor_count + 1
                cmd = cmd + "> output/{}_S{}_summarycalc.csv & kpid{}=$!".format(
                    runtype, summary_set, kpid_monitor_count)
                print_command(cmd)

    return anykats


def do_summarycalcs(runtype, analysis_settings, process_id):
    summarycalc_switch = "-g"
    if runtype == "il":
        summarycalc_switch = "-f"
    if "{}_summaries".format(runtype) in analysis_settings:
        cmd = "summarycalc {} ".format(summarycalc_switch)
        for summary in analysis_settings["{}_summaries".format(runtype)]:
            if "id" in summary:
                summary_set = summary["id"]
                cmd = cmd + "-{0} fifo/{1}_S{0}_summary_P{2} ".format(
                    summary_set, runtype, process_id)
        cmd = cmd + " < fifo/{}_P{} &".format(runtype, process_id)
        print_command(cmd)


def do_tees(runtype, analysis_settings, process_id):
    global pid_monitor_count
    summary_set = 0
    if "{}_summaries".format(runtype) not in analysis_settings:
        return

    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            pid_monitor_count = pid_monitor_count + 1
            summary_set = summary["id"]
            cmd = "tee < fifo/{}_S{}_summary_P{} ".format(
                runtype, summary_set, process_id)
            if summary.get("eltcalc"):
                cmd = cmd + "fifo/{}_S{}_summaryeltcalc_P{} ".format(
                    runtype, summary_set, process_id)
            if summary.get("pltcalc"):
                cmd = cmd + "fifo/{}_S{}_summarypltcalc_P{} ".format(
                    runtype, summary_set, process_id)
            if summary.get("summarycalc"):
                cmd = cmd + "fifo/{}_S{}_summarysummarycalc_P{} ".format(
                    runtype, summary_set, process_id)
            if summary.get("aalcalc"):
                cmd = cmd + "fifo/{}_S{}_summaryaalcalc_P{} ".format(
                    runtype, summary_set, process_id)
            if summary.get("lec_output") and leccalc_enabled(summary["leccalc"]):
                cmd = cmd + "work/{}_S{}_summaryleccalc/P{}.bin ".format(
                    runtype, summary_set, process_id)
            cmd = cmd + " > /dev/null & pid{}=$!".format(
                pid_monitor_count)
            print_command(cmd)


def do_any(runtype, analysis_settings, process_id):
    global pid_monitor_count

    summary_set = 0
    if "{}_summaries".format(runtype) not in analysis_settings:
        return

    for summary in analysis_settings["{}_summaries".format(runtype)]:
        if "id" in summary:
            summary_set = summary["id"]
            if summary.get("eltcalc"):
                cmd = "eltcalc -s"
                if process_id == 1:
                    cmd = "eltcalc"
                pid_monitor_count = pid_monitor_count + 1
                print_command(
                    "{3} < fifo/{0}_S{1}_summaryeltcalc_P{2} > work/kat/{0}_S{1}_eltcalc_P{2} & pid{4}=$!".format(
                        runtype, summary_set, process_id, cmd,pid_monitor_count))
            if summary.get("summarycalc"):
                cmd = "summarycalctocsv -s"
                if process_id == 1:
                    cmd = "summarycalctocsv"
                pid_monitor_count = pid_monitor_count + 1
                print_command(
                    "{3} < fifo/{0}_S{1}_summarysummarycalc_P{2} > work/kat/{0}_S{1}_summarycalc_P{2} & pid{4}=$!".format(
                        runtype, summary_set, process_id, cmd,pid_monitor_count))
            if summary.get("pltcalc"):
                cmd = "pltcalc -s"
                if process_id == 1:
                    cmd = "pltcalc"
                pid_monitor_count = pid_monitor_count + 1
                print_command(
                    "{3} < fifo/{0}_S{1}_summarypltcalc_P{2} > work/kat/{0}_S{1}_pltcalc_P{2} & pid{4}=$!".format(
                        runtype, summary_set, process_id, cmd,pid_monitor_count))
            if summary.get("aalcalc"):
                pid_monitor_count = pid_monitor_count + 1
                print_command(
                    "aalcalc < fifo/{0}_S{1}_summaryaalcalc_P{2} > work/{0}_S{1}_aalcalc/P{2}.bin & pid{3}=$!".format(
                        runtype, summary_set, process_id, pid_monitor_count))

        print_command("")


def do_il(analysis_settings, max_process_id):
    for process_id in range(1, max_process_id + 1):
        do_any("il", analysis_settings, process_id)

    for process_id in range(1, max_process_id + 1):
        do_tees("il", analysis_settings, process_id)

    for process_id in range(1, max_process_id + 1):
        do_summarycalcs("il", analysis_settings, process_id)


def do_gul(analysis_settings, max_process_id):
    for process_id in range(1, max_process_id + 1):
        do_any("gul", analysis_settings, process_id)

    for process_id in range(1, max_process_id + 1):
        do_tees("gul", analysis_settings, process_id)

    for process_id in range(1, max_process_id + 1):
        do_summarycalcs("gul", analysis_settings, process_id)


def do_il_make_fifo(analysis_settings, max_process_id):
    for process_id in range(1, max_process_id + 1):
        do_make_fifos("il", analysis_settings, process_id)


def do_gul_make_fifo(analysis_settings, max_process_id):
    for process_id in range(1, max_process_id + 1):
        do_make_fifos("gul", analysis_settings, process_id)


def do_il_remove_fifo(analysis_settings, max_process_id):
    for process_id in range(1, max_process_id + 1):
        do_remove_fifos("il", analysis_settings, process_id)


def do_gul_remove_fifo(analysis_settings, max_process_id):
    for process_id in range(1, max_process_id + 1):
        do_remove_fifos("gul", analysis_settings, process_id)


def do_waits(wait_variable, wait_count):
    if wait_count > 0:
        cmd = "wait "
        for pid in range(1, wait_count + 1):
            cmd = cmd + "${}{} ".format(wait_variable, pid)
        print_command(cmd)
        print_command("")


def do_pwaits():
    do_waits("pid", pid_monitor_count)


def do_awaits():
    do_waits("apid", apid_monitor_count)


def do_lwaits():
    do_waits("lpid", lpid_monitor_count)


def do_kwaits():
    do_waits("kpid", kpid_monitor_count)


def get_getmodel_cmd(
        process_id_, max_process_id,
        number_of_samples, gul_threshold,
        use_random_number_file,
        coverage_output, item_output):
    #pylint: disable=I0011, W0613
    cmd = "getmodel | gulcalc -S{} -L{}".format(number_of_samples, gul_threshold)

    if use_random_number_file:
        cmd = cmd + " -r"
    if coverage_output != "":
        cmd = cmd + " -c {}".format(coverage_output)
    if item_output != "":
        cmd = cmd + " -i {}".format(item_output)

    return cmd


@oasis_log_utils.oasis_log()
def genbash(
        max_process_id=None,
        analysis_settings=None,
        output_filename=None,
        get_getmodel_cmd=get_getmodel_cmd
    ):
    """
    Generates a bash script containing ktools calculation instructions for an
    Oasis model, provided its analysis settings JSON file, the number of processes
    to use, and the path and name of the output script.
    """
    #pylint: disable=I0011, W0621
    global pid_monitor_count
    pid_monitor_count = 0
    global apid_monitor_count
    apid_monitor_count = 0
    global lpid_monitor_count
    lpid_monitor_count = 0
    global kpid_monitor_count
    kpid_monitor_count = 0

    global command_file
    command_file = output_filename

    gul_threshold = 0
    number_of_samples = 0
    use_random_number_file = False
    gul_output = False
    il_output = False

    if "gul_threshold" in analysis_settings:
        gul_threshold = analysis_settings["gul_threshold"]

    if "number_of_samples" in analysis_settings:
        number_of_samples = analysis_settings["number_of_samples"]

    if "model_settings" in analysis_settings:
        if "use_random_number_file" in analysis_settings["model_settings"]:
            if analysis_settings["model_settings"]["use_random_number_file"]:
                use_random_number_file = True

    if "gul_output" in analysis_settings:
        gul_output = analysis_settings["gul_output"]

    if "il_output" in analysis_settings:
        il_output = analysis_settings["il_output"]

    print_command("#!/bin/bash")

    print_command("")

    print_command("rm -R -f output/*")
    print_command("rm -R -f fifo/*")
    print_command("rm -R -f work/*")
    print_command("")

    print_command("mkdir work/kat")

    if gul_output:
        do_gul_make_fifo(analysis_settings, max_process_id)
        create_workfolders("gul", analysis_settings)

    print_command("")

    if il_output:
        do_il_make_fifo(analysis_settings, max_process_id)
        create_workfolders("il", analysis_settings)

    print_command("")
    print_command("# --- Do insured loss computes ---")
    print_command("")
    if il_output:
        do_il(analysis_settings, max_process_id)

    print_command("")
    print_command("# --- Do ground up loss  computes ---")
    print_command("")
    if gul_output:
        do_gul(analysis_settings, max_process_id)

    print_command("")

    for process_id in range(1, max_process_id + 1):
        if gul_output and il_output:
            getmodel_cmd = get_getmodel_cmd(
                process_id, max_process_id,
                number_of_samples, gul_threshold, use_random_number_file,
                "fifo/gul_P{}".format(process_id),
                "-")
            print_command(
                "eve {0} {1} | {2} | fmcalc > fifo/il_P{0}  &".format(
                    process_id, max_process_id, getmodel_cmd))

        else:
            #  Now the mainprocessing
            if gul_output:
                if "gul_summaries" in analysis_settings:
                    getmodel_cmd = get_getmodel_cmd(
                        process_id, max_process_id,
                        number_of_samples, gul_threshold,
                        use_random_number_file,
                        "-",
                        "")
                    print_command(
                        "eve {0} {1} | {2} > fifo/gul_P{0}  &".format(
                            process_id, max_process_id, getmodel_cmd))

            if il_output:
                if "il_summaries" in analysis_settings:
                    getmodel_cmd = get_getmodel_cmd(
                        process_id, max_process_id,
                        number_of_samples, gul_threshold,
                        use_random_number_file,
                        "",
                        "-")
                    print_command(
                        "eve {0} {1} | {2} | fmcalc > fifo/il_P{0}  &".format(
                            process_id, max_process_id, getmodel_cmd))

    print_command("")

    do_pwaits()

    print_command("")
    print_command("# --- Do insured loss kats ---")
    print_command("")
    if il_output:
        do_kats("il", analysis_settings, max_process_id)


    print_command("")
    print_command("# --- Do ground up loss kats ---")
    print_command("")
    if gul_output:
        do_kats("gul", analysis_settings, max_process_id)

    do_kwaits()

    print_command("")
    do_post_wait_processing("il", analysis_settings)
    do_post_wait_processing("gul", analysis_settings)

    do_awaits()    # waits for aalcalc
    do_lwaits()    # waits for leccalc

    if gul_output:
        do_gul_remove_fifo(analysis_settings, max_process_id)
        remove_workfolders("gul", analysis_settings)

    print_command("")

    if il_output:
        do_il_remove_fifo(analysis_settings, max_process_id)
        remove_workfolders("il", analysis_settings)


SCRIPT_ARGS_METADICT = {
    'config_file_path': {
        'name': 'config_file_path',
        'flag': 'f',
        'type': str,
        'help_text': 'Model config path',
        'required_on_command_line': False,
        'required_for_script': False,
        'preexists': True
    },
    'oasis_files_path': {
        'name': 'oasis_files_path',
        'flag': 'o',
        'type': str,
        'help_text': 'Path to Oasis files',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': False
    },
    'analysis_settings_json_file_path': {
        'name': 'analysis_settings_json_file_path',
        'flag': 'j',
        'type': str,
        'help_text': 'Relative or absolute path of the model analysis settings JSON file',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_data_path': {
        'name': 'model_data_path',
        'flag': 'm',
        'type': str,
        'help_text': 'Model data source path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_run_dir_path': {
        'name': 'model_run_dir_path',
        'flag': 'r',
        'type': str,
        'help_text': 'Model run directory path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'ktools_script_name': {
        'name': 'ktools_script_name',
        'flag': 's',
        'type': str,
        'help_text': 'Relative or absolute path of the output file',
        'required_on_command_line': False,
        'required_for_script': True
    },
    'ktools_num_processes': {
        'name': 'ktools_num_processes',
        'flag': 'n',
        'type': int,
        'help_text': 'Number of ktools calculation processes to use',
        'required_on_command_line': False,
        'required_for_script': False
    },
    'execute': {
        'name': 'execute',
        'dest': 'execute',
        'type': bool,
        'default': True,
        'help_text': 'Whether to execute generated ktools script',
        'required_on_command_line': False,
        'required_for_script': False
    }
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('Console logging set')

    try:
        logger.info('Parsing script resources arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generate ktools script for model')

        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(SCRIPT_ARGS_METADICT, args['config_file_path']))
            args = mdk_utils.load_script_args_from_config_file(args['config_file_path'])
            logger.info('Script resources: {}'.format(args))
        else:
            args.pop('config_file_path')
            logger.info('Script resources arguments: {}'.format(args))

        di = SCRIPT_ARGS_METADICT
        missing = filter(lambda arg: not args[arg] if arg in args and di[arg]['required_for_script'] else None, di)

        if missing:
            raise OasisException('Not all required script resources arguments provided - missing {}'.format(missing))

        if not os.path.exists(args['model_run_dir_path']):
            os.mkdir(args['model_run_dir_path'])

        utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')
        model_run_dir_path = os.path.join(args['model_run_dir_path'], 'ProgOasis-{}'.format(utcnow))
        logger.info('Creating time-stamped model run folder {}'.format(model_run_dir_path))
        os.mkdir(model_run_dir_path)
        
        logger.info(
            'Preparing model run directory {} - '
            'copying Oasis files, analysis settings JSON file '
            'and linking model data'.
            format(model_run_dir_path)
        )
        prepare_model_run_directory(
            model_run_dir_path,
            args['oasis_files_path'],
            args['analysis_settings_json_file_path'],
            args['model_data_path']
        )

        logger.info('Converting Oasis files to ktools binary files')
        oasis_files_path = os.path.join(model_run_dir_path, 'input', 'csv')
        binary_files_path = os.path.join(model_run_dir_path, 'input')
        create_binary_files(oasis_files_path, binary_files_path)

        analysis_settings_json_file_path = os.path.join(model_run_dir_path, 'analysis_settings.json')
        try:
            logger.info('Reading analysis settings JSON file')
            with io.open(analysis_settings_json_file_path, 'r', encoding='utf-8') as f:
                analysis_settings = json.load(f)
                if 'analysis_settings' in analysis_settings:
                    analysis_settings = analysis_settings['analysis_settings']
        except (IOError, TypeError, ValueError):
            raise OasisException("Invalid analysis settings JSON file or file path: {}.".format(analysis_settings_json_file_path))

        logging.info('Loaded analysis settings JSON: {}'.format(analysis_settings))

        logger.info('Preparing model run inputs')
        model_data_path = os.path.join(model_run_dir_path, 'static')
        prepare_model_run_inputs(analysis_settings, model_run_dir_path, model_data_path)

        ktools_script_name = (
            args['ktools_script_name'] if 'ktools_script_name' in args and args['ktools_script_name']
            else 'run_ktools'
        )
        ktools_script_path = os.path.join(model_run_dir_path, '{}.sh'.format(ktools_script_name))

        ktools_num_processes = (
            args['ktools_num_processes'] if 'ktools_num_processes' in args and args['ktools_num_processes']
            else 2
        )
        try:
            logger.info('Generating ktools losses script')
            genbash(
                max_process_id=ktools_num_processes,
                analysis_settings=analysis_settings,
                output_filename=ktools_script_path
            )
        except Exception as e:
            raise OasisException(e)

        try:
            logger.info('Making ktools losses script executable')
            subprocess.check_call("chmod +x {}".format(ktools_script_path), stderr=subprocess.STDOUT, shell=True)
        except (OSError, IOError) as e:
            raise OasisException(e)

        logger.info('Generated ktools losses script {}'.format(ktools_script_path))

        try:
            if args['execute'] == False:
                sys.exit(0)
        except KeyError:
            pass

        try:
            os.chdir(model_run_dir_path)
            cmd_str = "bash {}.sh".format(ktools_script_name)
            logger.info('Running ktools losses script {}'.format(ktools_script_path))
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except (OSError, IOError, subprocess.CalledProcessError) as e:
            raise OasisException(e)

        logger.info('Loss outputs generated in {}'.format(os.path.join(model_run_dir_path, 'output')))
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)

    sys.exit(0)
