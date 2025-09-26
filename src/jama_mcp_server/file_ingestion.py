"""
File-based Requirement Ingestion

Support for ingesting requirements from various file formats
when Jama Connect is not available or for testing purposes.

Supported formats:
- CSV files with requirement data
- JSON files with structured requirements  
- Excel files (.xlsx, .xls)
- Plain text files with one requirement per line
"""

import logging
import os
import json
import csv
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from .jama_client import JamaRequirement

logger = logging.getLogger(__name__)


@dataclass
class FileRequirement:
    """Represents a requirement loaded from file."""
    id: str
    name: str
    description: str
    requirement_type: str = "functional"
    priority: str = "medium"
    status: str = "active"
    tags: List[str] = None
    custom_fields: Dict[str, Any] = None
    project_id: str = "file_project"
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
    
    def to_jama_requirement(self) -> JamaRequirement:
        """Convert to JamaRequirement format for compatibility."""
        return JamaRequirement(
            id=hash(self.id) % 1000000,  # Generate numeric ID
            global_id=self.id,
            name=self.name,
            description=self.description,
            item_type=self.requirement_type,
            project_id=1,  # Default project ID
            created_date=datetime.now(),
            modified_date=datetime.now(),
            status=self.status,
            priority=self.priority,
            tags=self.tags,
            custom_fields=self.custom_fields
        )


class FileIngestionConfig(BaseModel):
    """Configuration for file ingestion."""
    
    # File settings
    file_path: str = Field(..., description="Path to requirements file")
    file_format: Optional[str] = Field(None, description="File format (auto-detected if None)")
    encoding: str = Field("utf-8", description="File encoding")
    
    # CSV/Excel settings
    id_column: str = Field("id", description="Column name for requirement ID")
    name_column: str = Field("name", description="Column name for requirement name")
    description_column: str = Field("description", description="Column name for description")
    type_column: Optional[str] = Field("type", description="Column name for requirement type")
    priority_column: Optional[str] = Field("priority", description="Column name for priority")
    status_column: Optional[str] = Field("status", description="Column name for status")
    tags_column: Optional[str] = Field("tags", description="Column name for tags")
    
    # Processing settings
    skip_empty: bool = Field(True, description="Skip rows with empty descriptions")
    auto_generate_ids: bool = Field(True, description="Auto-generate IDs if missing")
    default_type: str = Field("functional", description="Default requirement type")
    default_priority: str = Field("medium", description="Default priority")
    default_status: str = Field("active", description="Default status")


class FileIngestionProcessor:
    """
    Processes requirement files and converts them to processable format.
    
    Supports multiple file formats and flexible column mapping.
    """
    
    def __init__(self, config: FileIngestionConfig):
        self.config = config
        self.file_path = Path(config.file_path)
        
        # Detect file format if not specified
        if not config.file_format:
            self.file_format = self._detect_format()
        else:
            self.file_format = config.file_format.lower()
    
    def _detect_format(self) -> str:
        """Auto-detect file format from extension."""
        suffix = self.file_path.suffix.lower()
        
        format_map = {
            '.csv': 'csv',
            '.json': 'json',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.txt': 'text',
            '.md': 'text'
        }
        
        return format_map.get(suffix, 'csv')
    
    async def load_requirements(self) -> List[FileRequirement]:
        """Load requirements from file."""
        logger.info(f"Loading requirements from {self.file_path} (format: {self.file_format})")
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {self.file_path}")
        
        if self.file_format == 'csv':
            return await self._load_csv()
        elif self.file_format == 'json':
            return await self._load_json()
        elif self.file_format == 'excel':
            return await self._load_excel()
        elif self.file_format == 'text':
            return await self._load_text()
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")
    
    async def _load_csv(self) -> List[FileRequirement]:
        """Load requirements from CSV file."""
        try:
            df = pd.read_csv(self.file_path, encoding=self.config.encoding)
            return await self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise
    
    async def _load_excel(self) -> List[FileRequirement]:
        """Load requirements from Excel file."""
        try:
            df = pd.read_excel(self.file_path)
            return await self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise
    
    async def _load_json(self) -> List[FileRequirement]:
        """Load requirements from JSON file."""
        try:
            with open(self.file_path, 'r', encoding=self.config.encoding) as f:
                data = json.load(f)
            
            requirements = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Array of requirement objects
                for i, item in enumerate(data):
                    req = await self._parse_json_requirement(item, i)
                    if req:
                        requirements.append(req)
            elif isinstance(data, dict):
                if 'requirements' in data:
                    # Nested structure with requirements array
                    for i, item in enumerate(data['requirements']):
                        req = await self._parse_json_requirement(item, i)
                        if req:
                            requirements.append(req)
                else:
                    # Single requirement object
                    req = await self._parse_json_requirement(data, 0)
                    if req:
                        requirements.append(req)
            
            logger.info(f"Loaded {len(requirements)} requirements from JSON")
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to load JSON file: {e}")
            raise
    
    async def _load_text(self) -> List[FileRequirement]:
        """Load requirements from plain text file (one per line)."""
        try:
            with open(self.file_path, 'r', encoding=self.config.encoding) as f:
                lines = f.readlines()
            
            requirements = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    req = FileRequirement(
                        id=f"REQ-{i+1:04d}",
                        name=f"Requirement {i+1}",
                        description=line,
                        requirement_type=self.config.default_type,
                        priority=self.config.default_priority,
                        status=self.config.default_status
                    )
                    requirements.append(req)
            
            logger.info(f"Loaded {len(requirements)} requirements from text file")
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to load text file: {e}")
            raise
    
    async def _process_dataframe(self, df: pd.DataFrame) -> List[FileRequirement]:
        """Process pandas DataFrame into requirements."""
        requirements = []
        
        # Check required columns
        if self.config.description_column not in df.columns:
            raise ValueError(f"Description column '{self.config.description_column}' not found")
        
        for i, row in df.iterrows():
            try:
                # Skip empty descriptions
                description = str(row.get(self.config.description_column, "")).strip()
                if self.config.skip_empty and not description:
                    continue
                
                # Extract fields with fallbacks
                req_id = str(row.get(self.config.id_column, f"REQ-{i+1:04d}"))
                name = str(row.get(self.config.name_column, f"Requirement {i+1}"))
                req_type = str(row.get(self.config.type_column, self.config.default_type))
                priority = str(row.get(self.config.priority_column, self.config.default_priority))
                status = str(row.get(self.config.status_column, self.config.default_status))
                
                # Parse tags
                tags = []
                if self.config.tags_column and self.config.tags_column in df.columns:
                    tags_str = str(row.get(self.config.tags_column, ""))
                    if tags_str and tags_str != "nan":
                        tags = [tag.strip() for tag in tags_str.split(',')]
                
                # Custom fields from remaining columns
                custom_fields = {}
                excluded_columns = {
                    self.config.id_column, self.config.name_column,
                    self.config.description_column, self.config.type_column,
                    self.config.priority_column, self.config.status_column,
                    self.config.tags_column
                }
                
                for col in df.columns:
                    if col not in excluded_columns and not pd.isna(row[col]):
                        custom_fields[col] = row[col]
                
                req = FileRequirement(
                    id=req_id,
                    name=name,
                    description=description,
                    requirement_type=req_type,
                    priority=priority,
                    status=status,
                    tags=tags,
                    custom_fields=custom_fields
                )
                
                requirements.append(req)
                
            except Exception as e:
                logger.warning(f"Failed to process row {i}: {e}")
                continue
        
        logger.info(f"Processed {len(requirements)} requirements from DataFrame")
        return requirements
    
    async def _parse_json_requirement(self, item: Dict[str, Any], index: int) -> Optional[FileRequirement]:
        """Parse individual JSON requirement object."""
        try:
            # Extract fields with flexible key names
            req_id = str(item.get('id', item.get('requirement_id', f"REQ-{index+1:04d}")))
            name = str(item.get('name', item.get('title', item.get('summary', f"Requirement {index+1}"))))
            description = str(item.get('description', item.get('text', item.get('content', ""))))
            
            if self.config.skip_empty and not description.strip():
                return None
            
            req_type = str(item.get('type', item.get('requirement_type', self.config.default_type)))
            priority = str(item.get('priority', self.config.default_priority))
            status = str(item.get('status', self.config.default_status))
            
            # Parse tags
            tags = item.get('tags', [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',')]
            
            # Custom fields
            custom_fields = {}
            excluded_keys = {'id', 'requirement_id', 'name', 'title', 'summary', 
                           'description', 'text', 'content', 'type', 'requirement_type',
                           'priority', 'status', 'tags'}
            
            for key, value in item.items():
                if key not in excluded_keys:
                    custom_fields[key] = value
            
            return FileRequirement(
                id=req_id,
                name=name,
                description=description,
                requirement_type=req_type,
                priority=priority,
                status=status,
                tags=tags,
                custom_fields=custom_fields
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse JSON requirement {index}: {e}")
            return None


# Utility functions

async def load_requirements_from_file(
    file_path: str,
    file_format: Optional[str] = None,
    **kwargs
) -> List[JamaRequirement]:
    """
    Load requirements from file and convert to JamaRequirement format.
    
    Args:
        file_path: Path to requirements file
        file_format: File format (auto-detected if None)
        **kwargs: Additional configuration options
        
    Returns:
        List of JamaRequirement objects
    """
    config = FileIngestionConfig(
        file_path=file_path,
        file_format=file_format,
        **kwargs
    )
    
    processor = FileIngestionProcessor(config)
    file_requirements = await processor.load_requirements()
    
    # Convert to JamaRequirement format
    jama_requirements = [req.to_jama_requirement() for req in file_requirements]
    
    logger.info(f"Successfully loaded {len(jama_requirements)} requirements from file")
    return jama_requirements


def create_sample_requirements_file(file_path: str, format_type: str = "csv") -> None:
    """Create a sample requirements file for testing."""
    
    sample_requirements = [
        {
            "id": "REQ-001",
            "name": "User Authentication",
            "description": "The system must provide secure user authentication for mortgage loan applications when users have valid credentials.",
            "type": "functional",
            "priority": "high",
            "status": "active",
            "tags": "authentication,security,mortgage"
        },
        {
            "id": "REQ-002", 
            "name": "Credit Score Validation",
            "description": "If credit score is above 650, then automatically approve the preliminary assessment for mortgage applications.",
            "type": "business_rule",
            "priority": "high",
            "status": "active",
            "tags": "credit,validation,business-rule"
        },
        {
            "id": "REQ-003",
            "name": "Interest Rate Calculation", 
            "description": "The interest rate must be calculated as the base rate plus risk premium, where risk premium is determined by credit score and loan amount.",
            "type": "business_rule",
            "priority": "high",
            "status": "active",
            "tags": "calculation,interest,mortgage"
        },
        {
            "id": "REQ-004",
            "name": "System Performance",
            "description": "The system shall process mortgage applications within 5 seconds for 95% of requests under normal load conditions.",
            "type": "non_functional",
            "priority": "medium", 
            "status": "active",
            "tags": "performance,response-time"
        },
        {
            "id": "REQ-005",
            "name": "Document Upload",
            "description": "Users must be able to upload financial documents in PDF format with maximum size of 10MB per document.",
            "type": "functional",
            "priority": "medium",
            "status": "active", 
            "tags": "upload,documents,pdf"
        },
        {
            "id": "REQ-006",
            "name": "Loan Amount Constraints",
            "description": "When loan amount exceeds $500,000, additional documentation and manager approval are required before processing.",
            "type": "business_rule",
            "priority": "high",
            "status": "active",
            "tags": "constraints,approval,high-value"
        },
        {
            "id": "REQ-007",
            "name": "Data Encryption",
            "description": "All customer financial data must be encrypted at rest and in transit using AES-256 encryption standards.",
            "type": "security",
            "priority": "high",
            "status": "active",
            "tags": "encryption,security,data-protection"
        },
        {
            "id": "REQ-008",
            "name": "Interdiction Check",
            "description": "The system must verify that applicants are not on financial interdiction lists before approving any loan applications.",
            "type": "compliance",
            "priority": "critical",
            "status": "active",
            "tags": "compliance,interdiction,verification"
        },
        {
            "id": "REQ-009",
            "name": "Audit Trail",
            "description": "The system shall maintain a complete audit trail of all changes to loan applications for regulatory compliance.",
            "type": "non_functional",
            "priority": "high",
            "status": "active",
            "tags": "audit,compliance,logging"
        },
        {
            "id": "REQ-010",
            "name": "Mobile Compatibility",
            "description": "The application interface must be responsive and functional on mobile devices with screen sizes from 320px to 768px width.",
            "type": "usability",
            "priority": "medium",
            "status": "active",
            "tags": "mobile,responsive,ui"
        }
    ]
    
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_type.lower() == "csv":
        df = pd.DataFrame(sample_requirements)
        df.to_csv(file_path, index=False)
        
    elif format_type.lower() == "json":
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"requirements": sample_requirements}, f, indent=2, ensure_ascii=False)
            
    elif format_type.lower() == "excel":
        df = pd.DataFrame(sample_requirements)
        df.to_excel(file_path, index=False, engine='openpyxl')
        
    elif format_type.lower() == "text":
        with open(file_path, 'w', encoding='utf-8') as f:
            for req in sample_requirements:
                f.write(f"{req['description']}\n")
    
    logger.info(f"Created sample requirements file: {file_path}")