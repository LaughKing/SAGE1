import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict, Tuple, Optional
from enum import Enum
from uuid import uuid4
import time
from pathlib import Path


class QualityLabel(Enum):
    """质量评估标签"""
    COMPLETE_EXCELLENT = "complete_excellent"      # 完美解决，可直接输出
    COMPLETE_GOOD = "complete_good"                # 良好解决，可直接输出
    PARTIAL_NEEDS_IMPROVEMENT = "partial_needs_improvement"  # 部分解决，需要改进
    INCOMPLETE_MISSING_INFO = "incomplete_missing_info"      # 信息不足，需要更多资源
    FAILED_POOR_QUALITY = "failed_poor_quality"              # 质量差，需要重新处理
    ERROR_INVALID = "error_invalid"                          # 错误或无效响应

@dataclass
class CriticEvaluation:
    """Critic评估结果"""
    label: QualityLabel
    confidence: float  # 0.0-1.0
    reasoning: str
    specific_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    should_return_to_chief: bool = False
    ready_for_output: bool = False

@dataclass
class AI_Template:
    # Packet metadata
    sequence: int = 0
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    # Generator content
    raw_question: str = None
    retriver_chunks: List[str] = field(default_factory=list)
    prompts: List[Dict[str, str]] = field(default_factory=list)
    response: str = None
    uuid: str = field(default_factory=lambda: str(uuid4()))
    tool_name: str = None
    evaluation: CriticEvaluation = None
    # Tool configuration - 存储工具相关的配置和中间结果
    tool_config: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """
        格式化显示AI_Template内容，用于terminal输出
        """
        # 时间格式化
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', 
                                     time.localtime(self.timestamp / 1000))
        
        # 构建输出字符串
        output_lines = []
        output_lines.append("=" * 80)
        
        # 标题行包含tool_name和评估信息
        title_parts = [f"🤖 AI Processing Result [ID: {self.uuid[:8]}]"]
        if self.tool_name:
            tool_emoji = self._get_tool_emoji(self.tool_name)
            title_parts.append(f"{tool_emoji} Tool: {self.tool_name}")
        
        output_lines.append(" | ".join(title_parts))
        output_lines.append(f"📅 Time: {timestamp_str} | Sequence: {self.sequence}")
        
        # 评估状态行
        if self.evaluation:
            quality_emoji = self._get_quality_emoji(self.evaluation.label)
            status_parts = [
                f"{quality_emoji} Quality: {self.evaluation.label.value}",
                f"Confidence: {self.evaluation.confidence:.2f}",
                f"Output Ready: {'✅' if self.evaluation.ready_for_output else '❌'}"
            ]
            output_lines.append("📊 " + " | ".join(status_parts))
        
        output_lines.append("=" * 80)
        
        # 原始问题
        if self.raw_question:
            output_lines.append(f"❓ Original Question:")
            output_lines.append(f"   {self.raw_question}")
            output_lines.append("")
        
        # 工具配置信息
        if self.tool_config:
            output_lines.append(f"🔧 Tool Configuration:")
            self._format_tool_config(output_lines)
            output_lines.append("")
        
        # 检索到的信息片段
        if self.retriver_chunks:
            output_lines.append(f"📚 Retrieved Information ({len(self.retriver_chunks)} sources):")
            for i, chunk in enumerate(self.retriver_chunks[:3], 1):  # 只显示前3个
                # 截取片段内容
                preview = chunk[:150] + "..." if len(chunk) > 150 else chunk
                output_lines.append(f"   [{i}] {preview}")
            
            if len(self.retriver_chunks) > 3:
                output_lines.append(f"   ... and {len(self.retriver_chunks) - 3} more sources")
            output_lines.append("")
        
        # 处理步骤信息（基于prompts）
        if self.prompts:
            system_prompts = [p for p in self.prompts if p.get('role') == 'system']
            user_prompts = [p for p in self.prompts if p.get('role') == 'user']
            
            if system_prompts or user_prompts:
                output_lines.append(f"⚙️  Processing Steps:")
                if system_prompts:
                    output_lines.append(f"   • System instructions: {len(system_prompts)} phases")
                if user_prompts:
                    # 显示最后一个用户prompt（通常是具体任务）
                    last_user_prompt = user_prompts[-1].get('content', '')
                    if last_user_prompt and last_user_prompt != self.raw_question:
                        preview = last_user_prompt[:100] + "..." if len(last_user_prompt) > 100 else last_user_prompt
                        output_lines.append(f"   • Specific task: {preview}")
                output_lines.append("")
        
        # AI响应
        if self.response:
            output_lines.append(f"🎯 AI Response:")
            # 格式化响应，添加适当的缩进
            response_lines = self.response.split('\n')
            for line in response_lines:
                output_lines.append(f"   {line}")
            output_lines.append("")
        
        # 评估详情
        if self.evaluation:
            output_lines.append(f"🔍 Evaluation Details:")
            output_lines.append(f"   • Reasoning: {self.evaluation.reasoning}")
            
            if self.evaluation.specific_issues:
                output_lines.append(f"   • Issues: {', '.join(self.evaluation.specific_issues)}")
            
            if self.evaluation.suggestions:
                output_lines.append(f"   • Suggestions: {', '.join(self.evaluation.suggestions)}")
            
            if self.evaluation.should_return_to_chief:
                output_lines.append(f"   • ⚠️  Should return to Chief for reprocessing")
            
            output_lines.append("")
        
        # 处理状态指示
        status_indicators = []
        if self.tool_name:
            status_indicators.append(f"Tool: {self.tool_name}")
        if self.response:
            status_indicators.append("✅ Response Generated")
        else:
            status_indicators.append("⏳ Processing")
        if self.retriver_chunks:
            status_indicators.append(f"📊 {len(self.retriver_chunks)} chunks")
        if self.evaluation:
            status_indicators.append(f"🔍 Evaluated ({self.evaluation.label.value})")
        if self.tool_config:
            status_indicators.append(f"🔧 Tool Config")
        
        if status_indicators:
            output_lines.append(f"📋 Status: {' | '.join(status_indicators)}")
            output_lines.append("")
        
        output_lines.append("=" * 80)
        
        return '\n'.join(output_lines)

    def _format_tool_config(self, output_lines: List[str]) -> None:
        """格式化工具配置信息的显示"""
        for key, value in self.tool_config.items():
            if key == "search_queries":
                # 特殊处理搜索查询
                if isinstance(value, list) and value:
                    output_lines.append(f"   • Search Queries ({len(value)}):")
                    for i, query in enumerate(value[:5], 1):  # 最多显示5个
                        preview = query[:80] + "..." if len(query) > 80 else query
                        output_lines.append(f"     [{i}] {preview}")
                    if len(value) > 5:
                        output_lines.append(f"     ... and {len(value) - 5} more queries")
                else:
                    output_lines.append(f"   • Search Queries: {value}")
            
            elif key == "search_analysis":
                # 特殊处理搜索分析
                if isinstance(value, dict):
                    output_lines.append(f"   • Search Analysis:")
                    if "analysis" in value:
                        analysis_text = value["analysis"][:100] + "..." if len(str(value["analysis"])) > 100 else value["analysis"]
                        output_lines.append(f"     - Analysis: {analysis_text}")
                    if "reasoning" in value:
                        reasoning_text = value["reasoning"][:100] + "..." if len(str(value["reasoning"])) > 100 else value["reasoning"]
                        output_lines.append(f"     - Reasoning: {reasoning_text}")
                else:
                    output_lines.append(f"   • Search Analysis: {value}")
            
            elif key == "optimization_metadata":
                # 特殊处理优化元数据
                if isinstance(value, dict):
                    output_lines.append(f"   • Optimization Metadata:")
                    for meta_key, meta_value in value.items():
                        if isinstance(meta_value, (str, int, float, bool)):
                            output_lines.append(f"     - {meta_key}: {meta_value}")
                        else:
                            output_lines.append(f"     - {meta_key}: {type(meta_value).__name__}")
                else:
                    output_lines.append(f"   • Optimization Metadata: {value}")
            
            else:
                # 通用处理其他配置项
                if isinstance(value, (list, dict)):
                    output_lines.append(f"   • {key.replace('_', ' ').title()}: {type(value).__name__}({len(value)} items)")
                else:
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:50] + "..."
                    output_lines.append(f"   • {key.replace('_', ' ').title()}: {value_str}")

    def _get_tool_emoji(self, tool_name: str) -> str:
        """根据工具名称返回对应的emoji"""
        tool_emojis = {
            "web_search": "🔍",
            "knowledge_retrieval": "📖",
            "calculator": "🧮",
            "code_executor": "💻",
            "data_analyzer": "📊",
            "translation": "🌐",
            "summarizer": "📝",
            "fact_checker": "✅",
            "image_analyzer": "🖼️",
            "weather_service": "🌤️",
            "stock_market": "📈",
            "news_aggregator": "📰",
            "direct_response": "💭",
            "error_handler": "⚠️"
        }
        return tool_emojis.get(tool_name, "🔧")

    def _get_quality_emoji(self, quality_label: QualityLabel) -> str:
        """根据质量标签返回对应的emoji"""
        quality_emojis = {
            QualityLabel.COMPLETE_EXCELLENT: "🌟",
            QualityLabel.COMPLETE_GOOD: "✅",
            QualityLabel.PARTIAL_NEEDS_IMPROVEMENT: "⚡",
            QualityLabel.INCOMPLETE_MISSING_INFO: "❓",
            QualityLabel.FAILED_POOR_QUALITY: "❌",
            QualityLabel.ERROR_INVALID: "⚠️"
        }
        return quality_emojis.get(quality_label, "❔")

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式，用于序列化
        支持嵌套的dataclass结构
        """
        result = {}
        
        # 基础字段
        result['sequence'] = self.sequence
        result['timestamp'] = self.timestamp
        result['raw_question'] = self.raw_question
        result['retriver_chunks'] = self.retriver_chunks.copy() if self.retriver_chunks else []
        result['prompts'] = self.prompts.copy() if self.prompts else []
        result['response'] = self.response
        result['uuid'] = self.uuid
        result['tool_name'] = self.tool_name
        result['tool_config'] = self._deep_copy_tool_config(self.tool_config) if self.tool_config else {}
        
        # 处理evaluation字段
        if self.evaluation:
            eval_dict = {
                'label': self.evaluation.label.value,  # 转换枚举为字符串
                'confidence': self.evaluation.confidence,
                'reasoning': self.evaluation.reasoning,
                'specific_issues': self.evaluation.specific_issues.copy(),
                'suggestions': self.evaluation.suggestions.copy(),
                'should_return_to_chief': self.evaluation.should_return_to_chief,
                'ready_for_output': self.evaluation.ready_for_output
            }
            result['evaluation'] = eval_dict
        else:
            result['evaluation'] = None
        
        return result

    def _deep_copy_tool_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """深拷贝tool_config，确保嵌套结构正确复制"""
        import copy
        return copy.deepcopy(config)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AI_Template':
        """
        从字典创建AI_Template实例
        支持嵌套的dataclass结构恢复
        """
        # 复制数据以避免修改原始数据
        data = data.copy()
        
        # 处理evaluation字段
        evaluation = None
        if data.get('evaluation'):
            eval_data = data['evaluation']
            
            # 恢复QualityLabel枚举
            label = QualityLabel(eval_data['label'])
            
            evaluation = CriticEvaluation(
                label=label,
                confidence=eval_data.get('confidence', 0.0),
                reasoning=eval_data.get('reasoning', ''),
                specific_issues=eval_data.get('specific_issues', []),
                suggestions=eval_data.get('suggestions', []),
                should_return_to_chief=eval_data.get('should_return_to_chief', False),
                ready_for_output=eval_data.get('ready_for_output', False)
            )
        
        # 创建AI_Template实例
        return cls(
            sequence=data.get('sequence', 0),
            timestamp=data.get('timestamp', int(time.time() * 1000)),
            raw_question=data.get('raw_question'),
            retriver_chunks=data.get('retriver_chunks', []),
            prompts=data.get('prompts', []),
            response=data.get('response'),
            uuid=data.get('uuid', str(uuid4())),
            tool_name=data.get('tool_name'),
            evaluation=evaluation,
            tool_config=data.get('tool_config', {})
        )

    def to_json(self) -> str:
        """
        转换为JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AI_Template':
        """
        从JSON字符串创建AI_Template实例
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to create AI_Template from JSON: {e}")

    def save_to_file(self, file_path: str) -> None:
        """
        保存到文件
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
        except Exception as e:
            raise IOError(f"Failed to save AI_Template to {file_path}: {e}")

    @classmethod
    def load_from_file(cls, file_path: str) -> 'AI_Template':
        """
        从文件加载
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return cls.from_json(f.read())
        except FileNotFoundError:
            raise FileNotFoundError(f"AI_Template file not found: {file_path}")
        except Exception as e:
            raise IOError(f"Failed to load AI_Template from {file_path}: {e}")

    def clone(self) -> 'AI_Template':
        """
        创建当前模板的深拷贝
        """
        return self.from_dict(self.to_dict())

    def update_evaluation(self, label: QualityLabel, confidence: float, 
                         reasoning: str, issues: List[str] = None, 
                         suggestions: List[str] = None) -> None:
        """
        更新或创建评估信息
        """
        self.evaluation = CriticEvaluation(
            label=label,
            confidence=confidence,
            reasoning=reasoning,
            specific_issues=issues or [],
            suggestions=suggestions or [],
            should_return_to_chief=label in [QualityLabel.FAILED_POOR_QUALITY, 
                                           QualityLabel.INCOMPLETE_MISSING_INFO],
            ready_for_output=label in [QualityLabel.COMPLETE_EXCELLENT, 
                                     QualityLabel.COMPLETE_GOOD]
        )

    # Tool Configuration相关方法
    def set_tool_config(self, key: str, value: Any) -> None:
        """
        设置工具配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        if self.tool_config is None:
            self.tool_config = {}
        self.tool_config[key] = value

    def get_tool_config(self, key: str, default: Any = None) -> Any:
        """
        获取工具配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        if not self.tool_config:
            return default
        return self.tool_config.get(key, default)

    def update_tool_config(self, config_dict: Dict[str, Any]) -> None:
        """
        批量更新工具配置
        
        Args:
            config_dict: 配置字典
        """
        if self.tool_config is None:
            self.tool_config = {}
        self.tool_config.update(config_dict)

    def remove_tool_config(self, key: str) -> Any:
        """
        移除工具配置项
        
        Args:
            key: 配置键
            
        Returns:
            被移除的值，如果不存在则返回None
        """
        if not self.tool_config:
            return None
        return self.tool_config.pop(key, None)

    def has_tool_config(self, key: str) -> bool:
        """
        检查是否存在指定的工具配置项
        
        Args:
            key: 配置键
            
        Returns:
            是否存在
        """
        return bool(self.tool_config and key in self.tool_config)

    # SearcherBot专用方法
    def set_search_queries(self, queries: List[str], analysis: Dict[str, Any] = None) -> None:
        """
        设置搜索查询和分析结果（SearcherBot专用）
        
        Args:
            queries: 搜索查询列表
            analysis: 搜索分析结果
        """
        self.set_tool_config("search_queries", queries)
        if analysis:
            self.set_tool_config("search_analysis", analysis)

    def get_search_queries(self) -> List[str]:
        """
        获取搜索查询列表
        
        Returns:
            搜索查询列表
        """
        return self.get_tool_config("search_queries", [])

    def get_search_analysis(self) -> Dict[str, Any]:
        """
        获取搜索分析结果
        
        Returns:
            搜索分析字典
        """
        return self.get_tool_config("search_analysis", {})

    def has_search_queries(self) -> bool:
        """
        检查是否有搜索查询
        
        Returns:
            是否有搜索查询
        """
        queries = self.get_search_queries()
        return bool(queries and len(queries) > 0)

    def has_complete_response(self) -> bool:
        """
        检查是否有完整的响应
        """
        return bool(self.response and self.response.strip())

    def is_ready_for_output(self) -> bool:
        """
        检查是否准备好输出
        """
        return (self.evaluation and 
                self.evaluation.ready_for_output and 
                self.has_complete_response())

    def get_processing_summary(self) -> Dict[str, Any]:
        """
        获取处理摘要信息
        """
        return {
            "uuid": self.uuid,
            "tool_name": self.tool_name,
            "has_response": self.has_complete_response(),
            "has_evaluation": self.evaluation is not None,
            "evaluation_label": self.evaluation.label.value if self.evaluation else None,
            "confidence": self.evaluation.confidence if self.evaluation else None,
            "ready_for_output": self.is_ready_for_output(),
            "chunks_count": len(self.retriver_chunks),
            "prompts_count": len(self.prompts),
            "has_tool_config": bool(self.tool_config),
            "tool_config_keys": list(self.tool_config.keys()) if self.tool_config else [],
            "has_search_queries": self.has_search_queries(),
            "search_queries_count": len(self.get_search_queries()),
            "timestamp": self.timestamp
        }