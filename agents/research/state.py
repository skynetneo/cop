from __future__ import annotations
from typing import List, Optional, Dict, Any, Literal, Union, Set
from pydantic import BaseModel, Field, HttpUrl, constr
from datetime import datetime
from uuid import uuid4
import hashlib

# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------

def deterministic_id(*parts: str) -> str:
    h = hashlib.sha256("||".join(parts).encode()).hexdigest()
    return h[:24]

# ------------------------------------------------------------------
# Base / shared
# ------------------------------------------------------------------

ResearchType = Literal["company","person","job","grant","marketing","general"]
ProjectStatus = Literal["init","collecting","processing","analyzing","synthesizing","complete","error","stale","archived"]

class SourceRef(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    url: Optional[HttpUrl] = None
    source_type: Literal["web","api","pdf","manual","db","social","file","other"] = "web"
    retrieval_method: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    published_at: Optional[datetime] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None
    credibility_score: Optional[float] = Field(None, ge=0, le=1)
    bias_notes: Optional[str] = None
    license: Optional[str] = None

class RetrievalEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid4().hex[:10])
    query: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    tool: Optional[str] = None
    result_count: int = 0
    next_cursor: Optional[str] = None
    notes: Optional[str] = None

class ChunkBase(BaseModel):
    chunk_id: str
    source_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    kind: str
    raw_char_len: int
    lang: Optional[str] = None
    hash: str
    quality_score: Optional[float] = Field(None, ge=0, le=1)  # internal heuristic
    confidence: Optional[float] = Field(None, ge=0, le=1)
    sensitivity_tags: List[str] = Field(default_factory=list)  # ["pii","credential","internal"]
    entity_refs: List[str] = Field(default_factory=list)  # link to discovered entities
    parent_document_id: Optional[str] = None
    sequence: Optional[int] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class RawExtractChunk(ChunkBase):
    kind: Literal["raw_extract"] = "raw_extract"
    text: str

class FactChunk(ChunkBase):
    kind: Literal["fact"] = "fact"
    statement: str
    evidence_span_ids: List[str] = Field(default_factory=list)  # link back to raw chunks
    normalization_notes: Optional[str] = None

class TableChunk(ChunkBase):
    kind: Literal["table"] = "table"
    headers: List[str]
    rows: List[List[str]]
    extracted_text_preview: Optional[str] = None

class SocialPostChunk(ChunkBase):
    kind: Literal["social_post"] = "social_post"
    platform: Literal["twitter","reddit","facebook","instagram","tiktok","threads","linkedin","other"]
    author_handle: Optional[str] = None
    posted_at: Optional[datetime] = None
    text: str
    engagement: Dict[str, int] = Field(default_factory=dict)  # likes, shares, etc.

class SocialAggregateChunk(ChunkBase):
    kind: Literal["social_agg"] = "social_agg"
    platform: str
    metric_window: str  # e.g., "30d"
    metrics: Dict[str, Any]

class FinancialMetricChunk(ChunkBase):
    kind: Literal["financial_metric"] = "financial_metric"
    metric_name: str
    value: float
    unit: Optional[str] = None
    period: Optional[str] = None  # e.g., "FY2024Q1"

class SecurityFindingChunk(ChunkBase):
    kind: Literal["security_finding"] = "security_finding"
    finding_type: str  # "exposed_port","leaked_credential","tech_stack_component"
    description: str
    severity: Optional[Literal["low","medium","high","critical"]] = None
    cve_ids: List[str] = Field(default_factory=list)

class JobListingChunk(ChunkBase):
    kind: Literal["job_listing"] = "job_listing"
    role_title: str
    company_name: Optional[str]
    location: Optional[str]
    compensation: Optional[str]
    requirements: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

class GrantProgramChunk(ChunkBase):
    kind: Literal["grant_program"] = "grant_program"
    program_name: str
    agency: Optional[str]
    deadline: Optional[str]
    funding_range: Optional[str]
    eligibility: List[str] = Field(default_factory=list)
    match_requirements: Optional[str] = None
    reporting_requirements: Optional[str] = None

Chunk = Union[
    RawExtractChunk, FactChunk, TableChunk, SocialPostChunk, SocialAggregateChunk,
    FinancialMetricChunk, SecurityFindingChunk, JobListingChunk, GrantProgramChunk
]

class EntityRecord(BaseModel):
    entity_id: str
    name: str
    type: Literal["person","company","product","technology","skill","location","regulation","other"]
    canonical: str
    aliases: Set[str] = Field(default_factory=set)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    mention_count: int = 0
    source_ids: Set[str] = Field(default_factory=set)

class Insight(BaseModel):
    insight_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    category: str  # "strategy","risk","opportunity","trend","skill_gap","eligibility","security"
    statement: str
    supporting_chunk_ids: List[str]
    confidence: float = Field(..., ge=0, le=1)
    importance: Optional[float] = Field(None, ge=0, le=1)
    derived_metrics: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class SynthesisSection(BaseModel):
    section_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str  # "SWOT","ExecutiveSummary","RiskMatrix","SkillGapMap","MarketingPersona"
    content: str
    insight_ids: List[str] = Field(default_factory=list)
    source_trace: Dict[str, int] = Field(default_factory=dict)  # chunk_id -> count in synthesis
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    quality_score: Optional[float] = None
    version: int = 1

class GapQuestion(BaseModel):
    gap_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    question: str
    rationale: str
    priority: Literal["high","medium","low"] = "medium"
    suggested_queries: List[str] = Field(default_factory=list)
    filled: bool = False
    filled_at: Optional[datetime] = None

class CoverageMetrics(BaseModel):
    total_chunks: int = 0
    fact_chunks: int = 0
    sources: int = 0
    avg_confidence: Optional[float] = None
    recency_score: Optional[float] = None
    entity_coverage: Dict[str, float] = Field(default_factory=dict)  # entity_type -> %
    gap_count: int = 0

# ------------------------------------------------------------------
# Domain-specific profiles
# ------------------------------------------------------------------

class CompanyProfile(BaseModel):
    name: str
    description: Optional[str] = None
    sectors: List[str] = Field(default_factory=list)
    headquarters: Optional[str] = None
    size_estimate: Optional[str] = None
    founded_year: Optional[int] = None
    tech_stack: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    swot: Optional[Dict[str,List[str]]] = None
    security_posture_summary: Optional[str] = None

class PersonProfile(BaseModel):
    full_name: str
    current_roles: List[str] = Field(default_factory=list)
    affiliations: List[str] = Field(default_factory=list)
    expertise_areas: List[str] = Field(default_factory=list)
    public_sentiment_summary: Optional[str] = None
    exposure_risk_summary: Optional[str] = None

class JobProfile(BaseModel):
    role_title: str
    industry: Optional[str] = None
    target_companies: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    salary_bands: List[str] = Field(default_factory=list)
    skill_gap_analysis: Optional[str] = None

class GrantProfile(BaseModel):
    focus_area: Optional[str] = None
    target_population: Optional[str] = None
    geographic_scope: Optional[str] = None
    eligibility_summary: Optional[str] = None
    deadlines: List[str] = Field(default_factory=list)
    typical_award_range: Optional[str] = None
    success_factors: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)

class MarketingProfile(BaseModel):
    campaign_goal: Optional[str] = None
    target_audiences: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    competitor_handles: List[str] = Field(default_factory=list)
    audience_personas: List[str] = Field(default_factory=list)
    trend_summary: Optional[str] = None
    messaging_pillars: List[str] = Field(default_factory=list)

class GeneralProfile(BaseModel):
    domain_topic: str
    scope_notes: Optional[str] = None
    key_theories: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)

DomainProfile = Union[
    CompanyProfile, PersonProfile, JobProfile, GrantProfile, MarketingProfile, GeneralProfile
]

class ScopeDefinition(BaseModel):
    primary_subject: str
    research_type: ResearchType
    objectives: List[str]
    initial_queries: List[str]
    constraints: Dict[str, Any] = Field(default_factory=dict)  # time_range, locale, language, etc.
    start_time: datetime = Field(default_factory=datetime.utcnow)
    max_rounds: int = 5
    current_round: int = 0

class AuditInfo(BaseModel):
    version: str = "1.0.0"
    schema_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    last_agent_node: Optional[str] = None
    notes: Optional[str] = None

class ResearchProject(BaseModel):
    project_id: str
    status: ProjectStatus = "init"
    scope: ScopeDefinition
    profile: Optional[DomainProfile] = None
    sources: Dict[str, SourceRef] = Field(default_factory=dict)
    retrieval_log: List[RetrievalEvent] = Field(default_factory=list)
    chunks: Dict[str, Chunk] = Field(default_factory=dict)
    entities: Dict[str, EntityRecord] = Field(default_factory=dict)
    insights: Dict[str, Insight] = Field(default_factory=dict)
    syntheses: Dict[str, SynthesisSection] = Field(default_factory=dict)
    gaps: Dict[str, GapQuestion] = Field(default_factory=dict)
    coverage: CoverageMetrics = Field(default_factory=CoverageMetrics)
    audit: AuditInfo = Field(default_factory=AuditInfo)
    tags: List[str] = Field(default_factory=list)
    # ephemeral runtime (excluded from serialization)
    runtime_cache: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
