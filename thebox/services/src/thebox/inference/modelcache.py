from typing import List
from logging import Logger
import gzip
import urllib.request
import hashlib
import os
import re
import threading
from shutil import copyfile

from thebox.common.model import ModelType, ModelDescriptor

class ModelCache(object):

    model_name_legnth: int = 12
    url_check_regex = re.compile(
        r'^(?:http|ftp)s?://.+$', # http://* or https://* or ftp://*
         re.IGNORECASE)

    def __init__(self, model_cache_location: str, logger: Logger):
        self.model_cache_root = model_cache_location
        self.__download_lock = threading.Lock()
        self.log = logger
        
    @staticmethod
    def __generate_model_file_name(file_url: str):
        hash_object = hashlib.sha256(file_url.encode('utf-8'))
        return hash_object.hexdigest()[0:ModelCache.model_name_legnth]

    def __download_file(self, file_url: str, out_file_name: str):
        """
        Download file from a given URL. If it is GZiped (has .gz), 
        it will unzip it. Return the downloaded file name.
        """
        decompress = False
        assert(out_file_name is not None)

        src_file_name = file_url[file_url.rfind("/")+1:]
        if src_file_name[-3:] == ".gz":
            decompress = True

        isUrl = re.match(ModelCache.url_check_regex, file_url) is not None
        
        self.log.debug(f"Caching model {file_url}, decompress={decompress}, isurl={isUrl}")

        if isUrl:
            response = urllib.request.urlopen(file_url)
            with open(out_file_name, 'wb') as outfile:
                if decompress:
                    outfile.write(gzip.decompress(response.read()))
                else:
                    outfile.write(response.read())
        else:
            if decompress:
                with open(file_url, 'rb') as infile:
                    with open(out_file_name, 'wb') as outfile:
                        outfile.write(gzip.decompress(infile.read()))
            else:
                copyfile(file_url, out_file_name)
            

    def fetch_model(self, model_desc: ModelDescriptor) -> str:
        """
        Return a local loadable model file for a given ModelDescriptor
        This function is thread safe

        Arguments:
            model_desc {ModelDescriptor} -- Model's scriptor
        
        Raises:
            NotImplementedError: if Model is not a CUSTOM model but PREBUILT
        
        Returns:
            str -- The local path to the model
        """
        if (model_desc.model_type != ModelType.BUILTIN):
            model_file_name = os.path.join(
                self.model_cache_root, 
                ModelCache.__generate_model_file_name(model_desc.model_location)
                )
            if not os.path.exists(self.model_cache_root):
                os.makedirs(self.model_cache_root)
            if not os.path.exists(model_file_name):
                with self.__download_lock:
                    if not os.path.exists(model_file_name):
                        self.__download_file(
                            model_desc.model_location,
                            model_file_name
                            )
            return model_file_name
        else:
            raise NotImplementedError(f"fetchModel with {model_desc.model_type}")


