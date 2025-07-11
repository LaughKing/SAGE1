from typing import Any, Iterable, Optional
from sage_core.operator.base_operator import BaseOperator
from sage_core.api.function_api.flatmap_function import FlatMapFunction
from sage_core.function.flatmap_collector import Collector



class FlatMapOperator(BaseOperator):
    """
    FlatMap操作符，支持将输入数据转换为多个输出数据。
    
    支持两种使用模式：
    1. Function内部调用out.collect()收集数据
    2. Function返回可迭代对象，自动展开发送给下游
    
    Example:
        # 模式1：在function内部使用out.collect()
        def my_function(data):
            words = data.value.split()
            for word in words:
                self.out.collect(word)
        
        # 模式2：function返回可迭代对象
        def my_function(data):
            return data.value.split()
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 创建并注入collector（仅当function是FlatMapFunction时）
        if isinstance(self.function, FlatMapFunction):
            self.collector = Collector(
                operator=self,
                session_folder=kwargs.get('session_folder'),
                name=kwargs.get('name', 'FlatMapOperator')
            )
            self.function.insert_collector(self.collector)
            self.logger.debug(f"FlatMapOperator '{self.name}' initialized with collector")
        else:
            self.collector = None
            self.logger.warning(f"FlatMapOperator '{self.name}' initialized without FlatMapFunction")
        self.logger.debug(f"FlatMapOperator '{self.name}' initialized")

    def receive_packet(self, data):
        """
        处理输入数据，支持两种模式：
        1. Function内部调用out.collect()
        2. Function返回可迭代对象
        """
        self.logger.debug(f"FlatMapOperator '{self.name}' processing data on tag '{tag}': {data}")
        
        try:
            # 清空收集器中的数据（如果有的话）
            self.out.clear()
            
            result = self.function.execute(data)
            
            # 处理function的返回值
            if result is not None:
                self._emit_iterable(result)
            
            # 处理通过collector收集的数据
            if self.collector:
                collected_data = self.collector.get_collected_data()
                if collected_data:
                    self.logger.debug(f"FlatMapOperator '{self.name}' collected {len(collected_data)} items via collector")
                    for item_data, item_tag in collected_data:
                        self.emit(item_data, item_tag)
                    # 清空collector
                    self.collector.clear()
            
            self.logger.debug(f"FlatMapOperator '{self.name}' finished processing")
            
        except Exception as e:
            self.logger.error(f"Error in FlatMapOperator '{self.name}'.receive_packet(): {e}", exc_info=True)
            raise

    def _emit_iterable(self, result: Any, tag: Optional[str] = None):
        """
        将可迭代对象展开并发送给下游
        
        Args:
            result: Function的返回值，应该是可迭代对象
            tag: 输出标签
        """
        try:
            # 检查返回值是否为可迭代对象（但不是字符串）
            if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                count = 0
                for item in result:
                    self.emit(item, tag)
                    count += 1
                self.logger.debug(f"FlatMapOperator '{self.name}' emitted {count} items from iterable")
            else:
                # 如果不是可迭代对象，直接发送
                self.emit(result, tag)
                self.logger.debug(f"FlatMapOperator '{self.name}' emitted single item: {result}")
                
        except Exception as e:
            self.logger.error(f"Error in FlatMapOperator '{self.name}'._emit_iterable(): {e}", exc_info=True)
            raise

    def get_collector_statistics(self) -> dict:
        """
        获取collector的统计信息
        
        Returns:
            dict: 统计信息，如果没有collector则返回空字典
        """
        if self.collector:
            return self.collector.get_statistics()
        return {}

    def debug_print_collector_info(self):
        """
        打印collector的调试信息
        """
        if self.collector:
            print(f"\n🔍 FlatMapOperator '{self.name}' Collector Info:")
            self.collector.debug_print_collected_data()
        else:
            print(f"\n🔍 FlatMapOperator '{self.name}' has no collector")