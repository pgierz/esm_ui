"""Main module."""

import pathlib
import socket

from git import Repo

# TODO(PG): Maybe convert to dataclass?
# See here: https://www.python.org/dev/peps/pep-0557/
class Project:

    def __init__(self, name, models=None, hpc_system=None, project_base=None, description=None):
    """
    This is a representation of an entire scientific project.

    You should specify the following (mandatory) arugments. You may also
    specify the optional arguments, which are marked as "optional":

    Parameters
    ----------
    name : str
        The name of the project. This should probably closely correlate to the
        name of the paper you intent to publish afterwards, or a keyword which
        you easily understand.
    models : list of str or Model (optional)
        A list of models you intend to use. This can either be a list of
        strings specifiying model names, or a list of Model objects. Strings of
        this list will be automatically converted into Model objects for you.
    hpc_system : str or HPCSystem (optional)
        The High Perfomance Computer used for this particular project. This can
        be passed in as a string descirbing the hpc's fully qualified domain
        name (fqdn), so, for example "ollie0.awi.de", or, alternatively, an
        already initializied HPCSystem object.
    project_base : str or pathlib.Path (optional if not specified in your user config)
        This describes where the project is located on the machine, and
        should point to a directory which you want to use, either as a
        pathlib.Path object, or as a string which can be converted to a
        Path.
    description : str (optional, but probably should be required)
        A long form description of what this project is about. If unset,
        defaults to an empty string, but you really should describe what you
        are trying to do with your science.
    """
        # Some basic information. What is this project, where is it, what is it
        # about
        self.name = name
        # TODO(PG): The defaults should come from some sort of user config.
        self.project_base = pathlib.Path(
            project_base or f"/work/ollie/pgierz/projects/PalModII/{self.name}"
        )
        self.hpc_system = HPCSystem(hpc_system) or HPCSystem(socket.getfqdn())  # "ollie0.awi.de"
        self.description = description or ""

        # Some information regarding which models are being used
        self.models = [models]  # List, since maybe one or more models are
                                # being used.
        self.experiments = []   # Empty list, the init routine should not
                                # generate any experiments for you.

        # Some things may be directly in the project, or they may come from
        # elsewhere on the filesystem
        # TODO(PG): Get this from the outside
        self.using_internal_model_codes = True
        self.using_internal_pool = True
        self.using_internal_bc_dir = True

        self.using_external_model_codes = not self.using_internal_model_codes
        self.using_external_pool = not self.using_internal_pool
        self.using_external_bc_dir = not self.using_internal_bc_dir

    def add_experiment(self, *args):
        for arg in args:
            self.experiments.append(arg)

    def create(self):
        self._setup_directories()
        self._get_models()
        self._get_software()
        self._setup_direnv()
        self._commit_to_gitlab()
        self._install_software()
        self._install_models()

    def _setup_directories(self):
        self._mkdir_base_directory()
        self._git_init()
        self._mkdir_in_project_base("software")
        self._mkdir_in_project_base("run_configs")
        self._mkdir_in_project_base("experiments")
        self._mkdir_in_project_base("model_codes")
        self._mkdir_in_project_base("boundary_conditions")
        self._mkdir_in_project_base("nonstandard_pool_files") if self.using_internal_pool

    # This should probably go into the init. Anyone who isn't using git for
    # their project is a dumbass.
    def _git_init(self):
        self.repo = Repo.init(self.project_base)

    def _mkdir_in_project_base(self, name):
        dir_to_make = self.project_base / name
        dir_to_make.mkdir(parents=True, exist_ok=True)

    def _mkdir_base_directory(self):
        self.project_base.mkdir(parents=True, exists_ok=True)

    def _get_models(self):
        for model in self.models:
            if self.using_internal_model_codes:
                self.add_as_submodule(model.name, f"model_codes/{model.name}", model.clone_url)
            else:
                self.hpc_system.pool_locations[model.name].symlink_to(f"model_codes/{model.name}")

    def add_as_submodule(self, name, project_path, repo_or_url):
        # A rather useless wrapper function, for now. But maybe we can
        # auto-create the repo or something.
        self.repo.create_submodule(name=name, project_path, repo_or_url)



    def _register_to_db(self):
        pass

    def _create_from_db(self):
        pass


class Model:
    """Representation of a Climate Model"""
    clone_url = "https://example.com"


class ModelComponent:
    """One Component (could be a stand-alone Model)"""


class ModelSetup:
    """Representation of a coupled model setup"""


class Experiment:
    """Representation of a specific model run"""


class RunConfig:
    """A YAML run config"""


class BoundaryConditionSet:
    """A specific set of boundary conditions"""


class SWTool:
    """A software tool to be added to a project"""

class HPCSystem:
    """Representation of a HPC System"""
