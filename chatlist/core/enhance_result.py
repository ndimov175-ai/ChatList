"""
Data models for prompt enhancement feature.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class EnhanceResult:
    """Result of prompt enhancement operation."""
    original_prompt: str
    enhanced_prompt: str
    alternatives: List[str]
    explanation: str
    recommendations: Dict[str, str]
    model_id: int
    enhancement_type: str = "general"
    timestamp: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage."""
        return {
            'original_prompt': self.original_prompt,
            'enhanced_prompt': self.enhanced_prompt,
            'alternatives': json.dumps(self.alternatives),
            'explanation': self.explanation,
            'recommendations': json.dumps(self.recommendations),
            'model_id': self.model_id,
            'enhancement_type': self.enhancement_type,
            'created_at': self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict) -> 'EnhanceResult':
        """Create from database row dictionary."""
        return EnhanceResult(
            id=data.get('id'),
            original_prompt=data['original_prompt'],
            enhanced_prompt=data['enhanced_prompt'],
            alternatives=json.loads(data.get('alternatives', '[]')),
            explanation=data['explanation'],
            recommendations=json.loads(data.get('recommendations', '{}')),
            model_id=data['model_id'],
            enhancement_type=data.get('enhancement_type', 'general'),
            timestamp=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
        )
