import os

import pytest
from click.testing import CliRunner
from path import Path

from trnslator import settings, copy_file, log, load_idf
from trnslator.cli import cli
from tests.test_trnsys import get_platform


class TestCli:
    """Defines tests for usage of the trnslator Command Line Interface"""

    @pytest.fixture(
        params=[
            [
                1,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                2,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "-i",
                "-t",
                "-d",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                3,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--window_lib",
                "trnslator/ressources/W74-lib.dat",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                4,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--template",
                "trnslator/ressources/NewFileTemplate.d18",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                5,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--log_clear_names",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                6,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--window",
                1.5,
                0.6,
                0.81,
                0.1,
                0.13,
                5.6,
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                7,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--ordered",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                8,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--nonum",
                "-N",
                "--geofloor",
                0.6,
                "--refarea",
                "--volume",
                "--capacitance",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
            [
                9,
                "--use-cache",
                "--cache-folder",
                "tests/.temp/cache",
                "--data-folder",
                "tests/.temp/data",
                "--imgs-folder",
                "tests/.temp/images",
                "--logs-folder",
                "tests/.temp/logs",
                "--verbose",
                "convert",
                "--ep_version",
                "9-2-0",
                "--schedule_as_input",
                "tests/input_data/trnsys/simple_2_zone.idf",
                "tests/input_data/CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw",
                "--trnsidf_exe",
                "docker/trnsidf/trnsidf.exe",
            ],
        ]
    )
    def cli_args(config, request):
        if request.param[0] == 1:
            print("Runs convert cli with EnergyPlus version 9-1-0")
        elif request.param[0] == 2:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND returns paths to "
                "modified IDF, T3D file and the DCK file"
            )
        elif request.param[0] == 3:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND a given window library"
            )
        elif request.param[0] == 4:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND a given d18 template"
            )
        elif request.param[0] == 5:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND without logging "
                "in console the equivalence between"
                " old and new names"
            )
        elif request.param[0] == 6:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND given window parameters "
                "(u-value, shgc, t_vis, etc.) to find in default window library"
            )
        elif request.param[0] == 7:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND the ordered option "
                "(sorting the idf object names)"
            )
        elif request.param[0] == 8:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND trnsidf.exe arguments:"
                "1) Will not renumber surfaces"
                "2) Does BatchJob Modus"
                "3) 60% of solar radiation is directed to the floor"
                "4) Updates floor reference area of airnodes"
                "5) Updates volume of airnodes"
                "6) Updates the capacitance of airnodes"
            )
        elif request.param[0] == 9:
            print(
                "Runs convert cli with EnergyPlus version 9-1-0 AND writing the "
                "schedules as SCHEDULES"
            )
        else:
            print("Runs convert cli with EnergyPlus version 9-1-0 AND other parameters")

        yield request.param[1:]

    @pytest.mark.skipif(
        os.environ.get("CI", "False").lower() == "true",
        reason="Skipping this test on CI environment.",
    )
    @pytest.mark.skipif(
        get_platform() > (10, 15, 0),
        reason="Skipping since wine 32bit can't run on MacOs >10.15 (Catalina)",
    )
    def test_convert(self, config, cli_args):
        """Tests the 'reduce' method"""
        runner = CliRunner()
        args = cli_args
        result = runner.invoke(cli, args, catch_exceptions=False)
        print(result.stdout)
        assert result.exit_code == 0

    def test_transition(self, config):
        """Tests the transition method for the CLI"""
        file = copy_file(
            "tests/input_data/problematic/ASHRAE90.1_ApartmentHighRise_STD2016_Buffalo.idf"
        )
        runner = CliRunner()
        result = runner.invoke(cli, ["transition", file], catch_exceptions=False)
        log(result.stdout)
        assert result.exit_code == 0
