from typing import Optional
import unreal
from abc import ABC, abstractmethod
from pathlib import Path


class UECacheABC(ABC):
    @abstractmethod
    def import_cache(
        self,
        cache_path: Path,
        dest_path: str,
        start_frame: int,
        end_frame: int,
        dest_name: Optional[str] = None,
    ):
        pass


class UEGeometryCache(UECacheABC):
    """
    UE Geometry cache类型
    """

    def __init__(self):
        pass

    def import_cache(
        self,
        cache_path: Path,
        dest_path: str,
        start_frame: int,
        end_frame: int,
        dest_name: Optional[str] = None,
    ) -> unreal.GeometryCache:
        """
        导入Geometry 缓存

        :param cache_path: 要导入的缓存路径
        :param dest_path: 导入位置
        :param dest_name: 导入名字
        :param start_frame: 起始帧
        :param end_frame: 结束帧

        :raise RuntimeError: 当导入失败时候触发诧异
        """
        task = unreal.AssetImportTask()
        task.filename = str(cache_path)
        task.destination_path = dest_path
        if not dest_name:
            dest_name = cache_path.stem
        task.destination_name = dest_name

        task.automated = True
        task.save = True
        task.replace_existing = True
        # options
        options = unreal.AbcImportSettings()
        options.import_type = unreal.AlembicImportType.GEOMETRY_CACHE
        options.sampling_settings.sampling_type = unreal.AlembicSamplingType.PER_FRAME
        options.sampling_settings.frame_start = start_frame
        options.sampling_settings.frame_end = end_frame
        options.geometry_cache_settings.motion_vectors = unreal.AbcGeometryCacheMotionVectorsImport.IMPORT_ABC_VELOCITIES_AS_MOTION_VECTORS
        options.normal_generation_settings.force_one_smoothing_group_per_object = True
        options.material_settings.find_materials = True
        options.conversion_settings.preset = unreal.AbcConversionPreset.MAYA

        task.options = options
        task.factory = unreal.AlembicImportFactory()
        tasks = unreal.Array(unreal.AssetImportTask)
        tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        if not task.imported_object_paths:
            raise RuntimeError("导入缓存失败")
        return unreal.load_asset(task.imported_object_paths[0])


class UEGroomCache(UECacheABC):
    def __init__(self):
        pass

    def import_cache(
        self,
        cache_path: Path,
        dest_path: str,
        start_frame: int,
        end_frame: int,
        dest_name: Optional[str] = None,
    ) -> unreal.GeometryCache:
        """
        导入Groom 缓存

        :param cache_path: 要导入的缓存路径
        :param dest_path: 导入位置
        :param dest_name: 导入名字
        :param start_frame: 起始帧
        :param end_frame: 结束帧

        :raise RuntimeError: 当导入失败时候触发诧异
        """
        task = unreal.AssetImportTask()
        task.filename = str(cache_path)
        task.destination_path = dest_path
        if not dest_name:
            dest_name = cache_path.stem
        task.destination_name = dest_name
        task.automated = True
        task.save = True
        task.replace_existing = True

        conversion_settings = unreal.GroomConversionSettings(
            unreal.Vector(90.0, 0.0, 0.0), unreal.Vector(1.0, -1.0, 1.0)
        )

        options = unreal.GroomCacheImportOptions()
        settings = options.import_settings
        settings.import_groom_cache = True
        settings.import_groom_asset = True
        settings.import_type = unreal.GroomCacheImportType.ALL
        settings.frame_start = start_frame
        settings.frame_end = end_frame
        settings.override_conversion_settings = True
        settings.conversion_settings = conversion_settings

        task.options = options
        tasks = unreal.Array(unreal.AssetImportTask)
        tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        if not task.imported_object_paths:
            raise RuntimeError("导入缓存失败")
        return unreal.load_asset(task.imported_object_paths[0])


class UEAssetBrowser:
    def __init__(self):
        self.asset_subsys = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)

    # 目录操作
    def check_directory_exists(self, directory_path: str, create: bool = False) -> bool:
        """
        检查UE的目录是否存在

        :param directory_path: UE中的路径
        :param create: 是否要创建这个目录
        :returns: 如果存在返回True，如果不存在返回False
        """
        if not self.asset_subsys:
            raise RuntimeError("初始化Editor Asset System 失败")
        if not self.asset_subsys.does_directory_exist(directory_path):
            if create:
                self.asset_subsys.make_directory(directory_path)
                return True
            return False
        return True

    def create_directory(self, directory_path: str) -> None:
        """
        创建一个目录

        :param directory_path: 要创建的UE路径
        :return: None
        """
        if not self.asset_subsys:
            raise RuntimeError("初始化Editor Asset System 失败")
        if self.check_directory_exists(directory_path):
            return
        self.asset_subsys.make_directory(directory_path)

    def delete_directory(self, directory_path: str) -> None:
        """
        删除目录

        :param directory_path: 要删除的目录
        """
        if not self.asset_subsys:
            raise RuntimeError("初始化Editor Asset System 失败")
        if not self.check_directory_exists(directory_path):
            raise RuntimeError(f"目录: {directory_path} 不存在")
        self.asset_subsys.delete_directory(directory_path)
