#!/usr/bin/env python3
"""Helper script to run all steps of a `Cosmic Ray`_ analysis automatically.

Per the `tutorial`_, this will:

* Ensure the tests can pass *without* mutations
* Create DB and populate with mutations to apply
* Work through the mutations and re-run the tests for each one
* Show report in text and HTML formats

.. _Cosmic Ray: https://cosmic-ray.readthedocs.io/en/latest/index.html
.. _tutorial: https://cosmic-ray.readthedocs.io/en/latest/tutorials/intro/index.html

"""

import glob
import logging
import pathlib
import sys

import tqdm
import yattag
from cosmic_ray import commands
from cosmic_ray.config import ConfigDict, load_config
from cosmic_ray.plugins import get_distributor
from cosmic_ray.tools.html import _generate_html_report
from cosmic_ray.tools.survival_rate import kills_count, survival_rate
from cosmic_ray.work_db import WorkDB, use_db
from cosmic_ray.work_item import TestOutcome, WorkItem

REPO = (pathlib.Path(__file__).parent / "..").resolve()

config_dict = load_config(REPO / "cosmic-ray.toml")
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
modules = [
    REPO / config_dict["module-path"] / module
    for module in glob.glob("*.py", root_dir=REPO / config_dict["module-path"])
]


def baseline(config: ConfigDict, /):
    """Ensure the tests can pass via Cosmic Ray before mutating."""
    with use_db(REPO / "mutation" / "baseline.sqlite", mode=WorkDB.Mode.create) as db:
        db.clear()
        db.add_work_item(
            WorkItem(
                mutations=[],  # type: ignore[invalid-argument-type] -- library definition is wrong
                job_id="baseline",
            )
        )
        commands.execute(db, config=config)
        if next(db.results)[1] == TestOutcome.KILLED:
            raise RuntimeError("test baseline failed")


baseline(config_dict)

with use_db(REPO / "mutation" / "state.sqlite", mode=WorkDB.Mode.create) as work_db:
    commands.init(
        module_paths=modules,
        operator_cfgs=config_dict.operators_config,
        work_db=work_db,
    )
    distributor = get_distributor(config_dict.distributor_name)

    with tqdm.tqdm(total=work_db.num_work_items) as progress:

        def on_task_complete(job_id, work_result):
            work_db.set_result(job_id, work_result)
            progress.update(work_db.num_results)

        distributor(
            work_db.pending_work_items,
            config_dict.test_command,
            config_dict.timeout,
            config_dict.distributor_config,
            on_task_complete=on_task_complete,
        )

    print(
        f"killed {kills_count(work_db):,} / {work_db.num_results:,} mutants (survival rate: {survival_rate(work_db):.1f}%)",
        file=sys.stderr,
    )

    report_path = REPO / "mutation" / "index.html"
    with open(report_path, mode="w") as report:
        doc: yattag.Doc = _generate_html_report(
            work_db, only_completed=False, skip_success=False
        )
        report.write(doc.getvalue())
        print(f"HTML report written to {str(report_path)}", file=sys.stderr)
