import io
import os
import glob
import shutil

import pytest

import trnslator as tr

import pandas as pd

from path import Path

from copy import deepcopy

from trnslator import (
    convert_idf_to_trnbuild,
    parallel_process,
    trnbuild_idf,
    copy_file,
    load_idf,
    settings,
    choose_window,
    run_eplus,
    ReportData,
    get_eplus_dirs,
)

# Function round to hundreds
from trnslator.trnsys import (
    _assert_files,
    load_idf_file_and_clean_names,
    clear_name_idf_objects,
    get_idf_objects,
    _get_constr_list,
    _order_objects,
    _get_schedules,
    _yearlySched_to_csv,
    _remove_low_conductivity,
    _write_version,
    _write_building,
    _add_change_adj_surf,
    _write_location_geomrules,
    _is_coordSys_world,
    _change_relative_coords,
    _get_ground_vertex,
    _write_zone_buildingSurf_fenestrationSurf,
    _write_constructions,
    _write_constructions_end,
    _write_materials,
    _write_gains,
    _write_conditioning,
    _write_schedules,
    _write_window,
    _write_winPool,
    _save_t3d,
    _relative_to_absolute,
    infilt_to_b18,
    gains_to_b18,
    conditioning_to_b18,
    adds_sch_ground,
    adds_sch_setpoint,
    t_initial_to_b18,
    closest_coords,
)
from tests.conftest import get_platform


@pytest.fixture(
    scope="class", params=["tests/input_data/trnsys/simple_2_zone_sched.idf",],
)
def converttesteasy(request):
    file = request.param
    window_file = "W74-lib.dat"
    template_dir = os.path.join("trnslator", "ressources")
    window_filepath = os.path.join(template_dir, window_file)
    template_d18 = "tests/input_data/trnsys/NewFileTemplate.d18"
    trnsidf_exe = "docker/trnsidf/trnsidf.exe"  # 'docker/trnsidf/trnsidf.exe'

    # prepare args (key=value). Key is a unique id for the runs (here the
    # file basename is used). Value is a dict of the function arguments
    kwargs_dict = {
        "u_value": 2.5,
        "shgc": 0.6,
        "t_vis": 0.78,
        "tolerance": 0.05,
        "ordered": True,
    }
    idf = load_idf(file)

    weather_file = os.path.join(
        "tests", "input_data", "CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw"
    )

    output_folder = os.path.relpath(settings.data_folder)

    yield idf, file, weather_file, window_filepath, trnsidf_exe, template_d18, output_folder, kwargs_dict

    del idf


class TestConvertEasy:

    """Tests functions of trnsys.py using 1 simple/small IDF file"""

    def test_assert_files(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Tests assertion if idf_file is None
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(None, None, None, None, None, None)

        # Tests assertion if weather file is None
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(idf_file, None, None, None, None, None)

        # Tests assertion if window_lib is None
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(idf_file, weather_file, None, None, None, None)

        # Tests assertion if output_folder is None
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(idf_file, weather_file, window_lib, None, None, None)

        # Tests assertion if trnsidf_exe and template_d18 is None
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(
                idf_file, weather_file, window_lib, output_folder, None, None
            )

        # Tests assertion if idf_file is a string but not a path
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files("wrong_string", None, None, None, None, None)

        # Tests assertion if weather_file is a string but not a path
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(idf_file, "wrong_string", None, None, None, None)

        # Tests assertion if window_lib is a string but not a path
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(idf_file, weather_file, "wrong_string", None, None, None)

        # Tests assertion if window_lib is not a string AND not None
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(idf_file, weather_file, 2, None, None, None)

        # Tests assertion if trnsidf_exe is a string but not a path
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(
                idf_file, weather_file, window_lib, output_folder, "wrong_string", None
            )

        # Tests assertion if template_d18 is a string but not a path
        with pytest.raises(IOError):
            (
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                template,
            ) = _assert_files(
                idf_file,
                weather_file,
                window_lib,
                output_folder,
                trnsidf_exe,
                "wrong_string",
            )

        assert output_folder == os.path.relpath(settings.data_folder)

    def test_get_save_write_schedules_as_sched(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Gets all schedule from IDF
        schedule_names, schedules = _get_schedules(idf_2)
        # Save schedules in a csv file
        _yearlySched_to_csv(idf_file, output_folder, schedule_names, schedules)
        # Write schedules directly in T3D file (in lines)
        schedule_as_input = False
        schedules_not_written = _write_schedules(
            lines, schedule_names, schedules, schedule_as_input, idf_file
        )

        # Asserts csv with schedules exists and schedules are written in lines
        assert os.path.exists(glob.glob(settings.data_folder + "/*.csv")[0])
        assert "!-SCHEDULE " + schedule_names[0] + "\n" in lines

    def test_write_version_and_building(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Get objects from IDF
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Write VERSION and BUILDING info from IDF to lines (T3D)
        _write_version(lines, versions)
        _write_building(buildings, lines)

        # Asserts version and building information written in lines
        assert "Version," + settings.ep_version.replace("-", ".")[:3] + ";\n" in lines
        assert buildings[0] in lines

    def test_write_material(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Get objects from IDF
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Write LAYER from IDF to lines (T3D)
        _write_materials(lines, materialAirGap, materialNoMass, materials)

        # Asserts materials (material, AirGap, NoMass, etc.) are written in lines
        assert "!-LAYER " + materialAirGap[0].Name + "\n" in lines
        assert "!-LAYER " + materialNoMass[0].Name + "\n" in lines
        assert "!-LAYER " + materials[0].Name + "\n" in lines

    def test_relative_to_absolute(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Clean names of idf objects (e.g. 'MATERIAL')
        log_clear_names = False
        clear_name_idf_objects(idf_2, log_clear_names)

        # Get objects from IDF
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Getting surface to test, by copying it (like that object stay unchanged)
        # And can be used after for assertion
        surface_init = deepcopy(buildingSurfs[0])

        # Transform relative coords of a surface to absolute coords
        _relative_to_absolute(buildingSurfs[0], 1, 2, 3)

        # Asserts relative coords converted to absolute ones
        assert (
            buildingSurfs[0]["Vertex_" + str(1) + "_Xcoordinate"]
            == surface_init["Vertex_" + str(1) + "_Xcoordinate"] + 1
        )
        assert (
            buildingSurfs[0]["Vertex_" + str(1) + "_Ycoordinate"]
            == surface_init["Vertex_" + str(1) + "_Ycoordinate"] + 2
        )
        assert (
            buildingSurfs[0]["Vertex_" + str(1) + "_Zcoordinate"]
            == surface_init["Vertex_" + str(1) + "_Zcoordinate"] + 3
        )

    def test_save_t3d(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Save T3D file at output_folder
        output_folder, t3d_path = _save_t3d(idf_file, lines, output_folder)

        # Asserts path to T3D file exists
        assert t3d_path in glob.glob(settings.data_folder + "/*.idf")

    def test_t_initial_to_b18(self, config, converttesteasy):
        # Deletes cache folder
        if os.path.exists(settings.cache_folder):
            shutil.rmtree(settings.cache_folder)

        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            kwargs,
        ) = converttesteasy

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Clean names of idf objects (e.g. 'MATERIAL')
        log_clear_names = False
        clear_name_idf_objects(idf_2, log_clear_names)

        # Get objects from IDF
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Read a b18 file and write lines in variable (b18_lines)
        b18_path = "tests/input_data/trnsys/T3D_simple_2_zone.b18"
        with open(b18_path) as b18_file:
            b18_lines = b18_file.readlines()

        # Creates a constant schedule setpoint over the year
        schedules = {"sch_h_setpoint_" + zones[0].Name: {"all values": [18] * 8760}}
        zones = [zones[0]]

        # Writes initial temperature of zone in b18_lines (b18 file)
        t_initial_to_b18(b18_lines, zones, schedules)

        # Asserts initial temperature is written in b18_lines
        assert any("TINITIAL= 18" in mystring for mystring in b18_lines[200:])

    def test_closest_coords(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            kwargs,
        ) = converttesteasy

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Get objects from IDF
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Find closest surface to origin (0,0,0)
        x, y, z = closest_coords(buildingSurfs, to=[0, 0, 0])

        # Asserts closest coords
        assert x == -5
        assert y == 215
        assert z == 0

    def test_write_to_b18(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            kwargs,
        ) = converttesteasy

        # Runs EnergyPlus Simulation
        res = run_eplus(
            idf_file,
            weather_file,
            output_directory=None,
            ep_version=None,
            output_report="htm",
            prep_outputs=True,
            design_day=True,
        )

        # Copy IDF object, making sure we don't change/overwrite original IDF file
        idf_2 = deepcopy(idf)

        # Clean names of idf objects (e.g. 'MATERIAL')
        log_clear_names = False
        clear_name_idf_objects(idf_2, log_clear_names)

        # Get old:new names equivalence
        old_new_names = pd.read_csv(
            os.path.join(
                settings.data_folder,
                Path(idf_file).basename().stripext() + "_old_new_names_equivalence.csv",
            )
        ).to_dict()

        # Get objects from IDF
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Read a b18 file and write lines in variable (b18_lines)
        b18_path = "tests/input_data/trnsys/T3D_simple_2_zone.b18"
        with open(b18_path) as b18_file:
            b18_lines = b18_file.readlines()

        # initialize variable
        schedules_not_written = []

        # Gets conditioning (heating and cooling) info from simulation results
        heat_name = {}
        for i in range(0, len(res["Zone Sensible Heating"])):
            key = res["Zone Sensible Heating"].iloc[i, 0]
            name = "HEAT_z" + str(res["Zone Sensible Heating"].iloc[i].name)
            heat_name[key] = name
        cool_name = {}
        for i in range(0, len(res["Zone Sensible Cooling"])):
            key = res["Zone Sensible Cooling"].iloc[i, 0]
            name = "HEAT_z" + str(res["Zone Sensible Cooling"].iloc[i].name)
            cool_name[key] = name

        # Selects only 2 first zones
        zones = zones[0:2]
        peoples = peoples[0:2]
        equipments = equipments[0:2]
        lights = lights[0:2]

        # Writes infiltration in b18_lines (b18 file)
        infilt_to_b18(b18_lines, zones, res)

        # Tests both cases, whether schedules are taken as inputs or written in b18_lines
        for cond in [True, False]:
            schedule_as_input = cond
            gains_to_b18(
                b18_lines,
                zones,
                zonelists,
                peoples,
                lights,
                equipments,
                schedules_not_written,
                res,
                old_new_names,
                schedule_as_input,
            )

        # Writes conditioning (heating and cooling) in b18_lines (b18 file)
        conditioning_to_b18(b18_lines, heat_name, cool_name, zones, old_new_names)

        # Asserts infiltration, internal gains and conditioning are written in b18_lines
        assert "INFILTRATION Constant" + "\n" in b18_lines
        assert " INFILTRATION = Constant" + "\n" in b18_lines
        assert any(peoples[0].Name in mystring for mystring in b18_lines[200:])
        assert any(lights[0].Name in mystring for mystring in b18_lines[200:])
        assert any(equipments[0].Name in mystring for mystring in b18_lines[200:])
        assert any(
            heat_name[old_new_names[zones[0].Name.upper()][0]] in mystring
            for mystring in b18_lines[200:]
        )

    def test_load_idf_file_and_clean_names(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttesteasy

        # Clean names of idf objects (e.g. 'MATERIAL')
        log_clear_names = False
        idf_2 = load_idf_file_and_clean_names(idf_file, log_clear_names)

        # Makes sure material names are unique and are 8 characters long
        name = None
        unique = False
        length = False
        for liste in idf_2.idfobjects["MATERIAL"].list2:
            if liste[1] != name:
                unique = True
                name = liste[1]
            else:
                unique = False
            if len(liste[1]) == 8:
                length = True
            else:
                length = False

        assert isinstance(idf_2, tr.idfclass.IDF)
        assert unique
        assert length

    def test_add_object_and_run_ep(self, config, converttesteasy):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            kwargs,
        ) = converttesteasy

        ep_version = None
        # Adds Output variable in IDF
        outputs = [
            {
                "ep_object": "Output:Variable".upper(),
                "kwargs": dict(
                    Variable_Name="Zone Thermostat Heating Setpoint Temperature",
                    Reporting_Frequency="hourly",
                    save=True,
                ),
            },
            {
                "ep_object": "Output:Variable".upper(),
                "kwargs": dict(
                    Variable_Name="Zone Thermostat Cooling Setpoint Temperature",
                    Reporting_Frequency="hourly",
                    save=True,
                ),
            },
        ]

        # Runs EnergyPlus Simulation
        _, idf = run_eplus(
            idf_file,
            weather_file,
            output_directory=None,
            ep_version=ep_version,
            output_report=None,
            prep_outputs=outputs,
            design_day=False,
            annual=True,
            expandobjects=True,
            return_idf=True,
        )

        # Makes sure idf vriable is an IDF
        assert isinstance(idf, tr.idfclass.IDF)


@pytest.fixture(
    scope="class", params=["5ZoneGeometryTransform.idf",],
)
def converttest(request):
    file = get_eplus_dirs(settings.ep_version) / "ExampleFiles" / request.param
    # file = request.param
    window_file = "W74-lib.dat"
    template_dir = os.path.join("trnslator", "ressources")
    window_filepath = os.path.join(template_dir, window_file)
    template_d18 = "tests/input_data/trnsys/NewFileTemplate.d18"
    trnsidf_exe = "docker/trnsidf/trnsidf.exe"  # 'docker/trnsidf/trnsidf.exe'

    # prepare args (key=value). Key is a unique id for the runs (here the
    # file basename is used). Value is a dict of the function arguments
    kwargs_dict = {
        "u_value": 2.5,
        "shgc": 0.6,
        "t_vis": 0.78,
        "tolerance": 0.05,
        "ordered": True,
    }
    idf = load_idf(file)

    weather_file = os.path.join(
        "tests", "input_data", "CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw"
    )

    output_folder = os.path.relpath(settings.data_folder)

    yield idf, file, weather_file, window_filepath, trnsidf_exe, template_d18, output_folder, kwargs_dict

    del idf


class TestConvert:

    """Tests convert_idf_to_trnbuild() with several files"""

    def test_get_save_write_schedules_as_input(self, config, converttest):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttest

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Gets all schedule from IDF
        schedule_names, schedules = _get_schedules(idf)
        # Save schedules in a csv file
        _yearlySched_to_csv(idf_file, output_folder, schedule_names, schedules)
        # Write schedules as inputs in T3D file (in lines)
        schedule_as_input = True
        schedules_not_written = _write_schedules(
            lines, schedule_names, schedules, schedule_as_input, idf_file
        )

    def test_write_idf_objects(self, config, converttest):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            kwargs,
        ) = converttest

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Get objects from IDF file
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf)

        # Creates low thermal resistance construction and materials to be deleted
        # To improve coverage of test
        idf.newidfobject(
            "MATERIAL",
            Name="low_res_mat",
            Roughness="Smooth",
            Thickness=0.0008,
            Conductivity=45.28,
            Density=7824,
            Specific_Heat=500,
            Thermal_Absorptance=0.7,
            Solar_Absorptance=0.7,
            Visible_Absorptance=0.7,
        )
        idf.newidfobject(
            "CONSTRUCTION", Name="low_res_constr", Outside_Layer="low_res_mat"
        )

        # Changes Outside boundary of surface to adiabatic
        # To improve coverage of test
        buildingSurfs[0].Outside_Boundary_Condition = "Adiabatic"

        # Changes coords of zone
        # To improve coverage of test
        zones[0].X_Origin = ""
        zones[0].Y_Origin = ""
        zones[0].Z_Origin = ""
        zones[0].Multiplier = ""

        # Get all construction EXCEPT fenestration ones
        constr_list = _get_constr_list(buildingSurfs)

        # If ordered=True, ordering idf objects
        ordered = True
        (
            buildingSurfs,
            buildings,
            constr_list,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            zones,
            zonelists,
        ) = _order_objects(
            buildingSurfs,
            buildings,
            constr_list,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            zones,
            zonelists,
            ordered,
        )

        # Removes low conductivity material and constructions
        mat_name = _remove_low_conductivity(constructions, idf, materials)

        # Determine if coordsSystem is "World" (all zones at (0,0,0))
        coordSys = _is_coordSys_world("Relative", zones)

        # Changes Geom Rule to "Relative"
        # To improve coverage of test
        globGeomRules[0].Coordinate_System = "Relative"
        globGeomRules[0].Daylighting_Reference_Point_Coordinate_System = "Relative"
        globGeomRules[0].Rectangular_Surface_Coordinate_System = "Relative"

        # Change Outside boundary condition of surface to itself
        # To improve coverage of test
        buildingSurfs[5].Outside_Boundary_Condition_Object = "C5-1"

        # Change Outside boundary condition of surface to Zone and adjacent to Outdoors
        # To improve coverage of test
        buildingSurfs[0].Outside_Boundary_Condition = "Zone"
        buildingSurfs[0].Outside_Boundary_Condition_Object = buildingSurfs[6].Zone_Name
        buildingSurfs[6].Outside_Boundary_Condition = "Outdoors"

        # Change Outside boundary condition of surface to Zone and adjacent to Zone.Name
        # To improve coverage of test
        buildingSurfs[1].Outside_Boundary_Condition = "Zone"
        buildingSurfs[1].Outside_Boundary_Condition_Object = "SPACE3-1"

        # Write LOCATION and GLOBALGEOMETRYRULES from IDF to lines (T3D) and
        # define if coordinate system is "Relative"
        coordSys = _write_location_geomrules(globGeomRules, lines, locations)

        # Change coordinates from relative to absolute for building surfaces
        _change_relative_coords(buildingSurfs, coordSys, idf)

        # Adds or changes adjacent surface if needed
        _add_change_adj_surf(buildingSurfs, idf)
        buildingSurfs = idf.idfobjects["BUILDINGSURFACE:DETAILED"]

        # Get all surfaces having Outside boundary condition with the ground.
        # To be used to find the window's slopes
        n_ground = _get_ground_vertex(buildingSurfs)

        # Writing zones in lines
        schedule_as_input = True
        win_slope_dict = _write_zone_buildingSurf_fenestrationSurf(
            buildingSurfs,
            coordSys,
            fenestrationSurfs,
            idf,
            lines,
            n_ground,
            zones,
            schedule_as_input,
        )

        # Write CONSTRUCTION from IDF to lines (T3D)
        _write_constructions(constr_list, idf, lines, mat_name, materials)

        # Write CONSTRUCTION from IDF to lines, at the end of the T3D file
        _write_constructions_end(constr_list, idf, lines)

        # region Write WINDOWS chosen by the user (from Berkeley lab library) in
        # lines (T3D)
        # Get window from library
        # window = (win_id, description, design, u_win, shgc_win, t_sol_win,
        # rf_sol, t_vis_win, lay_win, width, window_bunches[win_id], and maybe tolerance)
        win_u_value = kwargs.get("u_value", 2.2)
        win_shgc = kwargs.get("shgc", 0.64)
        win_tvis = kwargs.get("t_vis", 0.8)
        win_tolerance = kwargs.get("tolerance", 0.05)
        window = choose_window(
            win_u_value, win_shgc, win_tvis, win_tolerance, window_lib
        )

        # Write windows in lines
        _write_window(lines, win_slope_dict, window)

        # Write window pool in lines
        _write_winPool(lines, window)

    def test_write_gains_conditioning(self, config, converttest):
        # Gets from fixture paths to files and IDF object to be used in test
        (
            idf,
            idf_file,
            weather_file,
            window_lib,
            trnsidf_exe,
            template,
            output_folder,
            _,
        ) = converttest

        # Gets EnergyPlus version
        ep_version = settings.ep_version

        # Adds Output variable in IDF
        outputs = [
            {
                "ep_object": "Output:Variable".upper(),
                "kwargs": dict(
                    Variable_Name="Zone Thermostat Heating Setpoint Temperature",
                    Reporting_Frequency="hourly",
                    save=True,
                ),
            },
            {
                "ep_object": "Output:Variable".upper(),
                "kwargs": dict(
                    Variable_Name="Zone Thermostat Cooling Setpoint Temperature",
                    Reporting_Frequency="hourly",
                    save=True,
                ),
            },
        ]

        # Run EnergyPlus Simulation
        _, idf = run_eplus(
            idf_file,
            weather_file,
            output_directory=None,
            ep_version=ep_version,
            output_report=None,
            prep_outputs=outputs,
            design_day=False,
            annual=True,
            expandobjects=True,
            return_idf=True,
        )

        # Output reports
        htm = idf.htm
        sql = idf.sql
        sql_file = idf.sql_file

        # Check if cache exists
        log_clear_names = False

        # Clean names of idf objects (e.g. 'MATERIAL')
        idf_2 = deepcopy(idf)
        clear_name_idf_objects(idf_2, log_clear_names)

        # Get old:new names equivalence
        old_new_names = pd.read_csv(
            os.path.join(
                settings.data_folder,
                Path(idf_file).basename().stripext() + "_old_new_names_equivalence.csv",
            )
        ).to_dict()

        # Read IDF_T3D template and write lines in variable
        lines = io.TextIOWrapper(io.BytesIO(settings.template_BUI)).readlines()

        # Get objects from IDF file
        (
            buildingSurfs,
            buildings,
            constructions,
            equipments,
            fenestrationSurfs,
            globGeomRules,
            lights,
            locations,
            materialAirGap,
            materialNoMass,
            materials,
            peoples,
            versions,
            zones,
            zonelists,
        ) = get_idf_objects(idf_2)

        # Write GAINS (People, Lights, Equipment) from IDF to lines (T3D)
        _write_gains(equipments, lights, lines, peoples, htm, old_new_names)

        # Gets schedules from IDF
        schedule_names, schedules = _get_schedules(idf_2)

        # Adds ground temperature to schedules
        adds_sch_ground(htm, schedule_names, schedules)

        # Adds "sch_setpoint_ZONES" to schedules
        df_heating_setpoint = ReportData.from_sqlite(
            sql_file, table_name="Zone Thermostat Heating Setpoint Temperature"
        )
        df_cooling_setpoint = ReportData.from_sqlite(
            sql_file, table_name="Zone Thermostat Cooling Setpoint Temperature"
        )
        # Heating
        adds_sch_setpoint(
            zones, df_heating_setpoint, old_new_names, schedule_names, schedules, "h"
        )
        # Cooling
        adds_sch_setpoint(
            zones, df_cooling_setpoint, old_new_names, schedule_names, schedules, "c"
        )

        # Writes conditioning in lines
        schedule_as_input = True
        heat_dict, cool_dict = _write_conditioning(
            htm, lines, schedules, old_new_names, schedule_as_input
        )


@pytest.fixture(
    params=[
        "RefBldgWarehouseNew2004_Chicago.idf",
        "ASHRAE9012016_Warehouse_Denver.idf",
        "ASHRAE9012016_ApartmentMidRise_Denver.idf",
        "5ZoneGeometryTransform.idf",
    ]
)
def trnbuild_file(config, request):
    idf_file = get_eplus_dirs(settings.ep_version) / "ExampleFiles" / request.param
    idf_file = copy_file(idf_file, where=settings.cache_folder)

    yield idf_file


@pytest.mark.skipif(
    get_platform() > (10, 15, 0),
    reason="Skipping since wine 32bit can't run on MacOs >10.15 (Catalina)",
)
@pytest.mark.skipif(
    os.environ.get("CI", "False").lower() == "true",
    reason="Skipping this test on CI environment.",
)
class TestTrnBuild:
    def test_trnbuild_from_idf(self, config, trnbuild_file):
        # Gets file paths/names
        window_file = "W74-lib.dat"
        template_dir = os.path.join("trnslator", "ressources")
        window_filepath = os.path.join(template_dir, window_file)
        weather_file = os.path.join(
            "tests", "input_data", "CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw"
        )

        # prepare args (key=value)f or EnergyPlus version to use, windows parameters,etc.
        kwargs_dict = {
            "ep_version": settings.ep_version,
            "u_value": 2.5,
            "shgc": 0.6,
            "t_vis": 0.78,
            "tolerance": 0.05,
            "fframe": 0.1,
            "uframe": 7.5,
            "ordered": True,
        }

        # Gets IDF file path from fixture
        file = trnbuild_file

        # Convert IDF to BUI file
        convert_idf_to_trnbuild(
            idf_file=file,
            weather_file=weather_file,
            window_lib=window_filepath,
            template="tests/input_data/trnsys/NewFileTemplate.d18",
            trnsidf_exe="docker/trnsidf/trnsidf.exe",
            **kwargs_dict
        )

    @pytest.mark.win32
    def test_trnbuild_from_idf_parallel(self, config, trnbuild_file):
        # Gets IDF file path from fixture
        files = trnbuild_file

        # Path to weather file
        weather_file = os.path.join(
            "tests", "input_data", "CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw"
        )

        # prepare args (key=value). Key is a unique id for the runs (here the
        # file basename is used). Value is a dict of the function arguments
        in_dict = {
            os.path.basename(file): dict(idf_file=file, weather_file=weather_file)
            for file in files
        }

        # Convert IDF files to BUI ones usinf parallel process
        result = parallel_process(in_dict, convert_idf_to_trnbuild, 4, use_kwargs=True)

        assert not any(isinstance(a, Exception) for a in result.values())

    @pytest.mark.darwin
    @pytest.mark.linux
    def test_trnbuild_from_idf_parallel_darwin_or_linux(self, config):
        # Path to EnergyPlus example files
        file_upper_path = os.path.join(
            get_eplus_dirs(settings.ep_version), "ExampleFiles"
        )

        # IDF file names
        files = [
            "RefBldgWarehouseNew2004_Chicago.idf",
            "ASHRAE9012016_Warehouse_Denver.idf",
            "ASHRAE9012016_ApartmentMidRise_Denver.idf",
            "5ZoneGeometryTransform.idf",
        ]

        # Path to weather file
        weather_file = os.path.join(
            "tests", "input_data", "CAN_PQ_Montreal.Intl.AP.716270_CWEC.epw"
        )

        # prepare args (key=value). Key is a unique id for the runs (here the
        # file basename is used). Value is a dict of the function arguments
        in_dict = {
            os.path.basename(file): dict(
                idf_file=os.path.join(file_upper_path, file),
                weather_file=weather_file,
                template="tests/input_data/trnsys/NewFileTemplate.d18",
                trnsidf_exe="docker/trnsidf/trnsidf.exe",
            )
            for file in files
        }

        # Convert IDF files to BUI ones usinf parallel process
        result = parallel_process(in_dict, convert_idf_to_trnbuild, 4, use_kwargs=True)

        # Print results
        [print(a) for a in result.values() if isinstance(a, Exception)]

        assert not any(isinstance(a, Exception) for a in result.values())

    @pytest.mark.win32
    def test_trnbuild_idf_win32(self, config):
        # Paths to T3D and B18 template files
        idf_file = "tests/input_data/trnsys/Building.idf"
        template = "tests/input_data/trnsys/NewFileTemplate.d18"

        # Convert T3D file to BUI file
        res = trnbuild_idf(idf_file, template=template, nonum=True)

        assert res

    @pytest.mark.darwin
    @pytest.mark.linux
    @pytest.mark.xfail(
        not Path("docker/trnsidf/trnsidf.exe").exists(),
        reason="xfail since trnsidf.exe is not installed. This test can work if the "
        "trnsidf.exe is copied in ./docker/trnsidf",
    )
    def test_trnbuild_idf_darwin_or_linux(self, config):
        # Paths to T3D, B18 template and trnsidf.exe files
        idf_file = "tests/input_data/trnsys/Building.idf"
        template = "tests/input_data/trnsys/NewFileTemplate.d18"
        trnsidf_exe = "docker/trnsidf/trnsidf.exe"

        # Convert T3D file to BUI file
        res = trnbuild_idf(
            idf_file,
            template=template,
            dck=True,
            nonum=False,
            refarea=False,
            volume=False,
            capacitance=True,
            trnsidf_exe=trnsidf_exe,
        )

        assert res

@pytest.mark.skipif(
    get_platform() > (10, 15, 0),
    reason="Skipping since wine 32bit can't run on MacOs >10.15 (Catalina)",
)
@pytest.mark.skipif(
    os.environ.get("CI", "False").lower() == "true",
    reason="Skipping this test on CI environment.",
)
def test_trnbuild_from_simple_idf(config):
    # Path to weather file, window library and T3D template
    window_file = "W74-lib.dat"
    template_dir = os.path.join("trnslator", "ressources")
    window_filepath = os.path.join(template_dir, window_file)
    # weather_file = os.path.join(
    #     "tests", "input_data", "CAN_QC_Montreal-McTavish.716120_CWEC2016.epw"
    # )
    weather_file = os.path.join(
        "tests", "input_data", "USA_NY_Buffalo.Niagara.Intl.AP.725280_TMY3.epw"
    )

    # prepare args (key=value)f or EnergyPlus version to use, windows parameters,etc.
    # WINDOW = 2-WSV_#3_Air
    kwargs_dict = {
        "ep_version": "9-2-0",
        "u_value": 1.62,
        "shgc": 0.64,
        "t_vis": 0.8,
        "tolerance": 0.05,
        "fframe": 0.0,
        "uframe": 0.5,
        "ordered": True,
    }

    # Path to IDF file
    # file = os.path.join("tests", "input_data", "trnsys", "simple_2_zone.idf")
    file = os.path.join("tests", "input_data", "ASHRAE90.1_OfficeLarge_STD2016_Buffalo.idf")

    # Converts IDF to BUI
    convert_idf_to_trnbuild(
        idf_file=file,
        weather_file=weather_file,
        window_lib=window_filepath,
        template="tests/input_data/trnsys/NewFileTemplate.d18",
        trnsidf_exe="docker/trnsidf/trnsidf.exe",
        schedule_as_input=True,
        **kwargs_dict
    )