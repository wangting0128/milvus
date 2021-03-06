import os
import random
import string
import numpy as np
import pandas as pd
from sklearn import preprocessing

from pymilvus_orm.types import DataType
from pymilvus_orm.schema import CollectionSchema, FieldSchema
from common import common_type as ct
from utils.util_log import test_log as log
import threading
import traceback


"""" Methods of processing data """
l2 = lambda x, y: np.linalg.norm(np.array(x) - np.array(y))


def gen_unique_str(str_value=None):
    prefix = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    return "test_" + prefix if str_value is None else str_value + "_" + prefix


def gen_str_by_length(length=8):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def gen_int64_field(name=ct.default_int64_field_name, is_primary=False, description=ct.default_desc):
    int64_field = FieldSchema(name=name, dtype=DataType.INT64, description=description, is_primary=is_primary)
    return int64_field


def gen_float_field(name=ct.default_float_field_name, is_primary=False, description=ct.default_desc):
    float_field = FieldSchema(name=name, dtype=DataType.FLOAT, description=description, is_primary=is_primary)
    return float_field


def gen_float_vec_field(name=ct.default_float_vec_field_name, is_primary=False, dim=ct.default_dim,
                        description=ct.default_desc):
    float_vec_field = FieldSchema(name=name, dtype=DataType.FLOAT_VECTOR, description=description, dim=dim,
                                  is_primary=is_primary)
    return float_vec_field


def gen_binary_vec_field(name=ct.default_binary_vec_field_name, is_primary=False, dim=ct.default_dim,
                         description=ct.default_desc):
    binary_vec_field = FieldSchema(name=name, dtype=DataType.BINARY_VECTOR, description=description, dim=dim,
                                   is_primary=is_primary)
    return binary_vec_field


def gen_default_collection_schema(description=ct.default_desc, primary_field=None):
    fields = [gen_int64_field(), gen_float_field(), gen_float_vec_field()]
    schema = CollectionSchema(fields=fields, description=description, primary_field=primary_field)
    return schema


def gen_collection_schema(fields, primary_field=None, description=ct.default_desc):
    schema = CollectionSchema(fields=fields, primary_field=primary_field, description=description)
    return schema


def gen_default_binary_collection_schema(description=ct.default_desc, primary_field=None):
    fields = [gen_int64_field(), gen_float_field(), gen_binary_vec_field()]
    binary_schema = CollectionSchema(fields=fields, description=description, primary_field=primary_field)
    return binary_schema


def gen_vectors(nb, dim):
    vectors = [[random.random() for _ in range(dim)] for _ in range(nb)]
    vectors = preprocessing.normalize(vectors, axis=1, norm='l2')
    return vectors.tolist()


def gen_binary_vectors(num, dim):
    raw_vectors = []
    binary_vectors = []
    for _ in range(num):
        raw_vector = [random.randint(0, 1) for _ in range(dim)]
        raw_vectors.append(raw_vector)
        binary_vectors.append(bytes(np.packbits(raw_vector, axis=-1).tolist()))
    return raw_vectors, binary_vectors


def gen_default_dataframe_data(nb=ct.default_nb, dim=ct.default_dim):
    int_values = pd.Series(data=[i for i in range(nb)])
    float_values = pd.Series(data=[float(i) for i in range(nb)], dtype="float32")
    float_vec_values = gen_vectors(nb, dim)
    df = pd.DataFrame({
        ct.default_int64_field_name: int_values,
        ct.default_float_field_name: float_values,
        ct.default_float_vec_field_name: float_vec_values
    })
    return df


def gen_default_binary_dataframe_data(nb=ct.default_nb, dim=ct.default_dim):
    int_values = pd.Series(data=[i for i in range(nb)])
    float_values = pd.Series(data=[float(i) for i in range(nb)], dtype="float32")
    binary_raw_values, binary_vec_values = gen_binary_vectors(nb, dim)
    df = pd.DataFrame({
        ct.default_int64_field_name: int_values,
        ct.default_float_field_name: float_values,
        ct.default_binary_vec_field_name: binary_vec_values
    })
    return df, binary_raw_values


def gen_default_list_data(nb=ct.default_nb, dim=ct.default_dim):
    int_values = [i for i in range(nb)]
    float_values = [np.float32(i) for i in range(nb)]
    float_vec_values = gen_vectors(nb, dim)
    data = [int_values, float_values, float_vec_values]
    return data


def gen_default_tuple_data(nb=ct.default_nb, dim=ct.default_dim):
    int_values = [i for i in range(nb)]
    float_values = [float(i) for i in range(nb)]
    float_vec_values = gen_vectors(nb, dim)
    data = (int_values, float_values, float_vec_values)
    return data


def gen_numpy_data(nb=ct.default_nb, dim=ct.default_dim):
    int_values = np.arange(nb, dtype='int64')
    float_values = np.arange(nb, dtype='float32')
    float_vec_values = gen_vectors(nb, dim)
    data = [int_values, float_values, float_vec_values]
    return data


def gen_default_binary_list_data(nb=ct.default_nb, dim=ct.default_dim):
    int_values = [i for i in range(nb)]
    float_values = [np.float32(i) for i in range(nb)]
    _, binary_vec_values = gen_binary_vectors(nb, dim)
    data = [int_values, float_values, binary_vec_values]
    return data


def gen_simple_index():
    index_params = []
    for i in range(len(ct.all_index_types)):
        if ct.all_index_types[i] in ct.binary_support:
            continue
        dic = {"index_type": ct.all_index_types[i], "metric_type": "L2"}
        dic.update({"params": ct.default_index_params[i]})
        index_params.append(dic)
    return index_params


def gen_invalid_field_types():
    field_types = [
        6,
        1.0,
        [[]],
        {},
        (),
        "",
        "a"
    ]
    return field_types


def gen_all_type_fields():
    fields = []
    for k, v in DataType.__members__.items():
        if v != DataType.UNKNOWN:
            field = FieldSchema(name=k.lower(), dtype=v)
            fields.append(field)
    return fields


def gen_invalid_dataframe():
    vec = gen_vectors(3, 2)
    dfs = [
        # just columns df
        pd.DataFrame(columns=[ct.default_int64_field_name, ct.default_float_vec_field_name]),
        # no column just data df
        pd.DataFrame({' ': vec}),
        # datetime df
        pd.DataFrame({"date": pd.date_range('20210101', periods=3)}),
        # invalid column df
        pd.DataFrame({'%$#': vec}),
    ]
    return dfs


def jaccard(x, y):
    x = np.asarray(x, np.bool)
    y = np.asarray(y, np.bool)
    return 1 - np.double(np.bitwise_and(x, y).sum()) / np.double(np.bitwise_or(x, y).sum())


def hamming(x, y):
    x = np.asarray(x, np.bool)
    y = np.asarray(y, np.bool)
    return np.bitwise_xor(x, y).sum()


def tanimoto(x, y):
    x = np.asarray(x, np.bool)
    y = np.asarray(y, np.bool)
    return -np.log2(np.double(np.bitwise_and(x, y).sum()) / np.double(np.bitwise_or(x, y).sum()))


def substructure(x, y):
    x = np.asarray(x, np.bool)
    y = np.asarray(y, np.bool)
    return 1 - np.double(np.bitwise_and(x, y).sum()) / np.count_nonzero(y)


def superstructure(x, y):
    x = np.asarray(x, np.bool)
    y = np.asarray(y, np.bool)
    return 1 - np.double(np.bitwise_and(x, y).sum()) / np.count_nonzero(x)


def modify_file(file_path_list, is_modify=False, input_content=""):
    """
    file_path_list : file list -> list[<file_path>]
    is_modify : does the file need to be reset
    input_content ：the content that need to insert to the file
    """
    if not isinstance(file_path_list, list):
        log.error("[modify_file] file is not a list.")

    for file_path in file_path_list:
        folder_path, file_name = os.path.split(file_path)
        if not os.path.isdir(folder_path):
            log.debug("[modify_file] folder(%s) is not exist." % folder_path)
            os.makedirs(folder_path)

        if not os.path.isfile(file_path):
            log.error("[modify_file] file(%s) is not exist." % file_path)
        else:
            if is_modify is True:
                log.debug("[modify_file] start modifying file(%s)..." % file_path)
                with open(file_path, "r+") as f:
                    f.seek(0)
                    f.truncate()
                    f.write(input_content)
                    f.close()
                log.info("[modify_file] file(%s) modification is complete." % file_path_list)
