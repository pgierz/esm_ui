"""Main module."""

import pathlib
import socket

from git import Repo
import panel as pn
import param


# TODO(PG): Maybe convert to dataclass?
# See here: https://www.python.org/dev/peps/pep-0557/
class Project(param.Paramerized):
    """
    This is a representation of an entire scientific project.
    """

    name = param.String(
        allow_None=False,
        doc="""The name of the project. This should probably closely correlate to the
        name of the paper you intent to publish afterwards, or a keyword which
        you easily understand.""",
    )
    project_base = param.FolderPath(
        doc="""This describes where the project is located on the machine, and
        should point to a directory which you want to use, either as a
        pathlib.Path object, or as a string which can be converted to a
        Path.""",
    )
    models = param.ListSelector(
        objects=["AWIESM-2.1", "AWIESM-2.2", "PISM-1.2"],
        doc="""A list of models you intend to use. This can either be a list of
        strings specifiying model names, or a list of Model objects. Strings of
        this list will be automatically converted into Model objects for you. """,
    )
    experiments = param.List(doc="Which experiments are in this project")
    using_internal_model_codes = param.Boolean(
        default=True,
        doc="Does this project include models from inside the project folder?",
    )
    using_internal_pool = param.Boolean(
        default=True, doc="Does this project use pool files in the project folder?"
    )
    using_internal_bc_dir = param.Boolean(
        default=True,
        doc="Does this project use boundary condition sets from inside the project folder?",
    )
    hpc_system = param.Selector(
        objects=["mistral.dkrz.de", "ollie.awi.de", socket.getfqdn()],
        doc="""This describes where the project is located on the machine, and
        should point to a directory which you want to use, either as a
        pathlib.Path object, or as a string which can be converted to a
        Path.""",
    )
    description = param.String(
        doc="""A long form description of what this project is about. If unset,
        defaults to an empty string, but you really should describe what you
        are trying to do with your science.""",
    )

    def add_experiment(self, *args):
        for arg in args:
            self.experiments.append(arg)
    
    class WebUI(param.Paramerized):
        pl = pn.pipeline.Pipeline()
        pl.add_stage("Step 1: Project Metadata", ConfigureMetadata)

        class ConfigureMetadata(pn.Paramerized):
            name = Project.name
            description = Project.description
            ready = param.Boolean(default=False, precedence=-1)

            @param.output(('Name', param.String), ('Description', param.String))
            def output(self):
                return self.name, self.description

            def panel(self):
                return self.param
            

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
        if self.using_internal_pool:
            self._mkdir_in_project_base("nonstandard_pool_files")

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
                self.add_as_submodule(
                    model.name, f"model_codes/{model.name}", model.clone_url
                )
            else:
                self.hpc_system.pool_locations[model.name].symlink_to(
                    f"model_codes/{model.name}"
                )

    def add_as_submodule(self, name, project_path, repo_or_url):
        # A rather useless wrapper function, for now. But maybe we can
        # auto-create the repo or something.
        self.repo.create_submodule(name, project_path, repo_or_url)

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


def main():
    project = Project()
    project.WebUI.pl.servable()

#if __name__ == "__main__":
main()
