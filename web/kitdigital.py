import os
import yaml
from enum import Enum
import streamlit as st


class StageStatus(Enum):
    """
    Enum class for stage status
    """
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    PROGRESS = "PROGRESS"
    SKIP = "SKIP"


class StageType(Enum):
    """
    Enum class for stage types
    """
    CRAWL_URLS = "URLS"
    DIRECTORIES = "DIRECTORIES"


class Stage:
    def __init__(self, name: str, results_path: str, status=StageStatus.PENDING) -> None:
        self.name: str = name
        self.status: StageStatus = status
        self.results_path: str = results_path
        self.info: str = ""
        if not os.path.exists(self.results_path):
            os.makedirs(self.results_path, exist_ok=True)

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.value,
            "results_path": self.results_path,
            "info": self.info
        }
    
    @classmethod
    def from_dict(cls, data):
        name = data["name"]
        status = StageStatus(data["status"])
        results_path = data["results_path"]
        stage = cls(name, results_path, status) 
        stage.info = data["info"]
        return stage


class KitDigital:
    result_path_root = st.secrets.paths.result_kit

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.id: str = url.replace("https://", "").replace("http://", "").replace("/", "")
        self.results_path: str = os.path.join(self.result_path_root, self.id)
        self.info_file: str = os.path.join(self.results_path, "info_kit.yaml")
        self.stages: dict[StageType, Stage] = {
            StageType.CRAWL_URLS: Stage("Obtención De Urls", os.path.join(self.results_path, "urls")),
            StageType.DIRECTORIES: Stage("Subida a Directorios", os.path.join(self.results_path, "directories"))
        }
        if not os.path.exists(self.results_path):
            os.makedirs(self.results_path, exist_ok=True)
            self.to_yaml()

    def set_url(self, url):
        self.url = url
    
    def set_results_path(self, results_path):
        self.results_path = results_path

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "results_path": self.results_path,
            "stages": {
                stage_name.value: stage.to_dict() for stage_name, stage in self.stages.items()
            }
        }
    
    def to_yaml(self):
        with open(self.info_file, 'w') as f:
            yaml.dump(self.to_dict(), f)

    @classmethod
    def from_dict(cls, data):
        url = data["url"]
        kit_digital = cls(url)
        kit_digital.id = data["id"]
        kit_digital.results_path = data["results_path"]
        kit_digital.stages = {
            StageType(stage_name): Stage.from_dict(stage_data) for stage_name, stage_data in data["stages"].items()
        }
        return kit_digital
    
    @classmethod
    def from_yaml(cls, path):
        with open(path, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return cls.from_dict(data)
    
    @staticmethod
    def get_kit_digital(url: str) -> "KitDigital" | None:
        kit_id = url.replace("https://", "").replace("http://", "").replace("/", "_")
        results_path = os.path.join(KitDigital.result_path_root, kit_id)
        info_file = os.path.join(results_path, "info_kit.yaml")
        if os.path.exists(info_file):
            return KitDigital.from_yaml(info_file)
        else:
            return None

