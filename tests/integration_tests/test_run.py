#!/usr/bin/env python3
"""
"""

import json
import logging
import os
import shutil
from pathlib import Path
from pprint import pprint
from unittest import TestCase
import pytest
from zipfile import ZipFile

import flywheel

import run


def install_gear(zip_name):
    """unarchive initial gear to simulate running inside a real gear.

    This will delete and then install: config.json input/ output/ work/

    Args:
        zip_name (str): name of zip file that holds simulated gear.
    """

    gear_tests = "/src/tests/data/gear_tests/"
    gear = "/flywheel/v0/"
    os.chdir(gear)  # Make sure we're in the right place (gear works in "work/" dir)

    print("\nRemoving previous gear...")

    if Path(gear + "config.json").exists():
        Path(gear + "config.json").unlink()

    for dir_name in ["input", "output", "work"]:
        path = Path(gear + dir_name)
        if path.exists():
            shutil.rmtree(path)

    print(f'\ninstalling new gear, "{zip_name}"...')
    input_zip = ZipFile(gear_tests + zip_name, "r")
    input_zip.extractall(gear)

    # swap in user's api-key if there is one (fake) in the config
    config_json = Path("./config.json")
    if config_json.exists():
        print(f"Found {str(config_json)}")
        api_dict = None
        with open(config_json) as cjf:
            config_dict = json.load(cjf)
            pprint(config_dict["inputs"])
            if "api_key" in config_dict["inputs"]:
                print(f'Found "api_key" in config_dict["inputs"]')

                user_json = Path(Path.home() / ".config/flywheel/user.json")
                if user_json.exists():
                    with open(user_json) as ujf:
                        api_dict = json.load(ujf)
                    config_dict["inputs"]["api_key"]["key"] = api_dict["key"]
                    print(f"installing api-key...")
                else:
                    print(f"{str(user_json)} not found.  Can't get api key.")
            else:
                print(f'No "api_key" in config_dict["inputs"]')

        if api_dict:
            with open(config_json, "w") as cjf:
                json.dump(config_dict, cjf)
    else:
        print(f"{str(config_json)} does not exist.  Can't set api key.")


def print_caplog(caplog):

    print("\nmessages")
    for ii, msg in enumerate(caplog.messages):
        print(f"{ii:2d} {msg}")
    print("\nrecords")
    for ii, rec in enumerate(caplog.records):
        print(f"{ii:2d} {rec}")


def search_caplog(caplog, find_me):
    """Search caplog message for find_me, return message"""

    for msg in caplog.messages:
        if find_me in msg:
            return msg
    return ""


def search_caplog_contains(caplog, find_me, contains_me):
    """Search caplog message for find_me, return true if it contains contins_me"""

    for msg in caplog.messages:
        if find_me in msg:
            if contains_me in msg:
                return True
    return False


def print_captured(captured):

    print("\nout")
    for ii, msg in enumerate(captured.out.split("\n")):
        print(f"{ii:2d} {msg}")
    print("\nerr")
    for ii, msg in enumerate(captured.err.split("\n")):
        print(f"{ii:2d} {msg}")


#
#  Tests
#


def test_dry_run_works(caplog):

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")
    with open(user_json) as json_file:
        data = json.load(json_file)
        if "ga" not in data["key"]:
            TestCase.skipTest("", "Not logged in to ga.")


    caplog.set_level(logging.DEBUG)

    install_gear("dry_run.zip")

    with pytest.raises(SystemExit) as pytest_wrapped_e:

        context = flywheel.GearContext()

        log = run.initialize(context)

        run.create_command(context, log)

        if len(context.gear_dict['errors']) == 0:
            run.set_up_data(context, log)

        run.execute(context, log)

    print(pytest_wrapped_e)

    print_caplog(caplog)

    #assert "gear-dry-run is set" in caplog.messages[59]
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    msg = search_caplog(caplog, "Command: /usr/bin/python3.4")
    for ii, item in enumerate(msg.split()):
        if "n_cpus" in item:
            print(item)
            num = int(item.split("=")[1])
            print(num)
            assert num > 0
            break
