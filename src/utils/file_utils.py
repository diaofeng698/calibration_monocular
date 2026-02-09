"""
文件工具函数
用于保存和加载标定结果
"""
import yaml
import numpy as np
import json
import os


def save_calibration(data: dict, filename: str):
    """
    保存标定结果到YAML文件
    
    Args:
        data: 标定数据字典
        filename: 输出文件路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 转换numpy数组为列表
    data_to_save = convert_numpy_to_list(data)
    
    with open(filename, 'w') as f:
        yaml.dump(data_to_save, f, default_flow_style=False)
    
    print(f"标定结果已保存到: {filename}")


def load_calibration(filename: str) -> dict:
    """
    从YAML文件加载标定结果
    
    Args:
        filename: 输入文件路径
        
    Returns:
        标定数据字典
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"文件不存在: {filename}")
    
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"标定结果已加载: {filename}")
    return data


def convert_numpy_to_list(obj):
    """
    递归转换numpy数组为列表
    
    Args:
        obj: 要转换的对象
        
    Returns:
        转换后的对象
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_list(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_list(item) for item in obj]
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    else:
        return obj


def save_json(data: dict, filename: str):
    """
    保存数据到JSON文件
    
    Args:
        data: 数据字典
        filename: 输出文件路径
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    data_to_save = convert_numpy_to_list(data)
    
    with open(filename, 'w') as f:
        json.dump(data_to_save, f, indent=2)
    
    print(f"数据已保存到: {filename}")


def load_json(filename: str) -> dict:
    """
    从JSON文件加载数据
    
    Args:
        filename: 输入文件路径
        
    Returns:
        数据字典
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"文件不存在: {filename}")
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return data
