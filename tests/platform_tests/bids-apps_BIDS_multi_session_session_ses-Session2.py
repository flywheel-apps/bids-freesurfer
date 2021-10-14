#! /usr/bin/env python3
"""Run bids-freesurfer on session "ses-Session2"

    This script was created to run Job ID 61672224ed5fcc2ee72d8458
    In project "bids-apps/BIDS_multi_session"
    On Flywheel Instance https://ga.ce.flywheel.io/api
"""

import os
import argparse
from datetime import datetime


import flywheel


input_files = {}


def main(fw):

    gear = fw.lookup("gears/bids-freesurfer")
    print("gear.gear.version for job was = 1.0.4_6.0.1-5")
    print(f"gear.gear.version now = {gear.gear.version}")
    print("destination_id = 6151e91f3d956a115c4ec87e")
    print("destination type is: session")
    destination = fw.lookup("bids-apps/BIDS_multi_session/sub-TOME3024/ses-Session2")

    inputs = dict()
    for key, val in input_files.items():
        container = fw.lookup(val["container_path"])
        inputs[key] = container.get_file(val["location_name"])

    config = {
        "3T": False,
        "acquisition_label": "",
        "gear-FREESURFER_LICENSE": "andyworth@flywheel.io 43847  *C9loVmePt98.  "
        "FSogusF81tuks",
        "gear-abort-on-bids-error": False,
        "gear-analysis-level": "participant",
        "gear-dry-run": False,
        "gear-keep-output": False,
        "gear-log-level": "INFO",
        "gear-run-bids-validation": False,
        "hires_mode": "auto",
        "measurements": "thickness",
        "multiple_sessions": "longitudinal",
        "n_cpus": 0,
        "parcellations": "aparc",
        "participant_label": "",
        "refine_pial": "T2",
        "refine_pial_acquisition_label": "",
        "session_label": "",
        "skip_bids_validator": False,
        "stages": "autorecon-all",
        "steps": "",
        "template_name": "average",
    }

    now = datetime.now()
    analysis_label = (
        f'{gear.gear.name} {now.strftime("%m-%d-%Y %H:%M:%S")} SDK launched'
    )
    print(f"analysis_label = {analysis_label}")

    analysis_id = gear.run(
        analysis_label=analysis_label,
        config=config,
        inputs=inputs,
        destination=destination,
    )
    print(f"analysis_id = {analysis_id}")
    return analysis_id


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    fw = flywheel.Client("")
    print(fw.get_config().site.api_url)

    analysis_id = main(fw)

    os.sys.exit(0)
