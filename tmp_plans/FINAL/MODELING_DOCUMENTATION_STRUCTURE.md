# VMT Economic Modeling Documentation Structure

**Created**: October 9, 2025  
**Purpose**: Organize modeling effort documentation for clarity and accessibility  
**Status**: Draft Skeleton - Review & Customize

---

## Current State Overview

This document proposes a reorganized structure for the economic modeling documentation currently scattered across `tmp_plans/`. The goal is to create a clear hierarchy that separates:

1. **Foundational mathematical models** (theory)
2. **Implementation validation** (reviews & gaps)
3. **Project management** (plans & todos)
4. **Final authoritative docs** (synthesis)

---

## Proposed Folder Structure

```
tmp_plans/
│
├── FINAL/                                    # ✅ Authoritative, reviewed documents
│   ├── README.md                            # [NEW] Navigation guide for this structure
│   ├── Spatial_Economic_Theory_Framework.md # ✅ Exists - Normative theoretical foundation
│   ├── Opus_econ_model_review.md            # ✅ Exists - Validation guide
│   └── MODELING_DOCUMENTATION_STRUCTURE.md  # ✅ This file
│
├── MODELS/                                   # Mathematical specifications (theory → implementation)
│   ├── README.md                            # [NEW] Model hierarchy & relationships
│   ├── 1_single_agent_utility_spatial.md   # ✅ Phase 1: Foundation
│   ├── 2_bilateral_pure_exchange.md        # ✅ Phase 2: Pure exchange
│   ├── 3_bilateral_forage_exchange.md      # ✅ Phase 3: Combined forage + trade
│   ├── REVIEW_critical_gaps.md             # ✅ Cross-model gap analysis
│   │
│   ├── archive/                             # [NEW] Superseded or experimental models
│   │   └── [older drafts, if any]
│   │
│   └── me/                                  # ✅ Personal working drafts (Chris's sandbox)
│       └── [working notes]
│
├── REVIEWS/                                  # Expert reviews & validation feedback
│   ├── README.md                            # [NEW] Review summary & key takeaways
│   ├── first_thoughts.md                   # ✅ Initial review
│   ├── opus.md                              # ✅ Claude Opus review
│   ├── gemini_econ_model_review.md         # ✅ Gemini review
│   ├── gpt5high_econ_model_review.md       # ✅ GPT-5 review
│   ├── sonnet45_econ_model_review.md       # ✅ Sonnet review
│   ├── sonnet45_followup.md                # ✅ Sonnet follow-up
│   ├── llm_assist.md                        # ✅ General LLM assistance notes
│   │
│   └── synthesis/                           # [NEW] Cross-review synthesis
│       ├── consensus_issues.md             # [NEW] Issues flagged by multiple reviewers
│       └── resolution_status.md            # [NEW] Tracking fixes/decisions
│
├── TODOS/                                    # Project planning & task tracking
│   ├── README.md                            # [NEW] Current status & priorities
│   ├── ECONOMIC_MODEL_IMPLEMENTATION_PLAN.md # ✅ Main implementation roadmap
│   ├── Opus_BIG_PICTURE_review_a.md        # ✅ Strategic review
│   ├── gemini25pro_BIGPICTURE_review_a.md  # ✅ Strategic review
│   ├── gpt5high_BIGPICTURE_review_a.md     # ✅ Strategic review
│   │
│   └── archive/                             # [NEW] Completed or obsolete plans
│       └── [old plans]
│
└── CRITICAL/                                 # Infrastructure & architecture (non-modeling)
    ├── DEBUG_RECORDING_ARCHITECTURE.md      # ✅ Debug tooling design
    └── DEBUG_RECORDING_ARCHITECTURE_PATCH_V1.md # ✅ Implementation patch

```

---

## Recommended Additions

### 1. Navigation READMEs

Each major folder should have a `README.md` providing:
- **Purpose**: What belongs in this folder
- **Contents**: Brief description of each file
- **Status**: Which docs are authoritative vs. draft
- **Dependencies**: Links to related docs in other folders

### 2. Archive Folders

Create `archive/` subdirectories in:
- `MODELS/archive/` - Superseded model specs
- `TODOS/archive/` - Completed plans
- `REVIEWS/archive/` - Historical reviews (if needed)

Benefits:
- Keep working directories clean
- Preserve history without clutter
- Easy to restore if needed

### 3. Synthesis Documents (New)

**In `REVIEWS/synthesis/`**:
- `consensus_issues.md` - Problems flagged by 2+ reviewers
- `resolution_status.md` - Track which issues are fixed/deferred/wontfix

**In `FINAL/`**:
- `implementation_checklist.md` - Bridge theory → code
- `validation_test_matrix.md` - Required tests for each model

---

## Alternative Structures (Consider)

### Option A: Flat Structure with Prefixes
```
tmp_plans/
├── 00_README.md
├── 01_FINAL_Spatial_Economic_Theory.md
├── 01_FINAL_Opus_Validation.md
├── 10_MODEL_Single_Agent.md
├── 11_MODEL_Bilateral_Exchange.md
├── 20_REVIEW_Opus.md
├── 21_REVIEW_Gemini.md
├── 30_TODO_Implementation_Plan.md
└── 90_CRITICAL_Debug_Architecture.md
```

**Pros**: Single directory, alphabetical order, easy grep  
**Cons**: Harder to navigate visually, less semantic grouping

### Option B: Phase-Based Structure
```
tmp_plans/
├── phase1_single_agent/
│   ├── theory/
│   ├── reviews/
│   └── implementation/
├── phase2_bilateral_exchange/
│   ├── theory/
│   ├── reviews/
│   └── implementation/
└── cross_cutting/
    ├── spatial_theory_framework.md
    └── validation_guide.md
```

**Pros**: Clear phase boundaries, self-contained  
**Cons**: Duplication of cross-cutting concerns, harder to find shared docs

---

## Migration Steps (If Approved)

### Phase 1: Create Structure (No File Moves)
1. ✅ Create this document
2. Create `README.md` files in each major folder
3. Add `archive/` and `synthesis/` subdirectories

### Phase 2: Add New Documents
1. Write `MODELS/README.md` - Model hierarchy guide
2. Write `REVIEWS/README.md` - Review summary
3. Write `REVIEWS/synthesis/consensus_issues.md`
4. Write `FINAL/implementation_checklist.md`

### Phase 3: Archive Old Content (Optional)
1. Move superseded docs to `archive/` folders
2. Update cross-references in remaining docs
3. Add deprecation notices to moved files

### Phase 4: Validate & Lock
1. Review all READMEs with team
2. Mark `FINAL/` docs as read-only (except via PR)
3. Document the structure in main project README

---

## Decision Points (Your Input Needed)

### 1. Folder Organization
- [ ] Keep current hierarchical structure (MODELS/, REVIEWS/, TODOS/)
- [ ] Switch to flat structure with prefixes (Option A)
- [ ] Switch to phase-based structure (Option B)
- [ ] Custom hybrid (describe below)

**Notes**: _____________________________________________________________

### 2. Archive Strategy
- [ ] Create `archive/` subdirectories now
- [ ] Wait until content actually becomes obsolete
- [ ] Don't archive - delete obsolete files instead
- [ ] Use Git history for archival (keep tree clean)

**Notes**: _____________________________________________________________

### 3. README Granularity
- [ ] One README per major folder (4 READMEs total)
- [ ] READMEs for major + minor folders (8+ READMEs)
- [ ] Single master README at `tmp_plans/README.md`
- [ ] No READMEs - rely on this structure doc

**Notes**: _____________________________________________________________

### 4. Synthesis Documents Priority
Which synthesis docs are most valuable to create first?

- [ ] `REVIEWS/synthesis/consensus_issues.md` (cross-review gaps)
- [ ] `FINAL/implementation_checklist.md` (theory → code bridge)
- [ ] `FINAL/validation_test_matrix.md` (required tests)
- [ ] `MODELS/README.md` (model hierarchy guide)
- [ ] Other: _______________________________________________________

### 5. File Renaming
Should any existing files be renamed for clarity?

- [ ] Yes - propose renames below
- [ ] No - keep current names

**Proposed renames**:
- `Opus BIG PICTURE review a.md` → `Opus_BIGPICTURE_review_a.md` (consistency)
- _________________________________________________________________
- _________________________________________________________________

---

## Next Steps

1. **Review this skeleton** - Mark decisions above
2. **Customize structure** - Edit folder tree if needed
3. **Approve or iterate** - Discuss with team/self
4. **Execute migration** - Follow phased approach above

---

## Notes & Considerations

### What Goes in FINAL/?
- **Criteria**: Document is:
  - Reviewed by 2+ experts OR extensively validated
  - Stable (not expected to change frequently)
  - Authoritative reference for implementation
  - Cross-phase (not tied to single model/task)

- **Current FINAL/ candidates**:
  - `Spatial_Economic_Theory_Framework.md` ✅
  - `Opus_econ_model_review.md` ✅
  - Maybe: `MODELS/1_single_agent_utility_spatial.md` (once validated)

### What Stays in MODELS/?
- Mathematical specifications (theory)
- Analytical predictions
- Validation test designs
- Phase-specific implementation notes
- Working drafts (`me/` folder)

### What Stays in REVIEWS/?
- External expert reviews (LLM or human)
- Review-specific insights
- Comparative analysis
- Validation feedback
- NOT synthesis (goes in `synthesis/` subfolder)

### What Stays in TODOS/?
- Implementation plans
- Task tracking
- Project roadmaps
- Strategic reviews (BIG PICTURE)
- Timeline estimates
- NOT completed work (archive or delete)

### What Stays in CRITICAL/?
- Infrastructure design (debug tools, refactors)
- Architecture decisions
- Cross-cutting technical concerns
- NOT economic modeling (wrong folder)

---

## Maintenance Guidelines

### When to Update This Structure
- [ ] Major new phase starts (e.g., Phase 4: Multi-agent trade)
- [ ] Document types proliferate (need new subfolder)
- [ ] Team grows (more people need navigation)
- [ ] External docs needed (publications, teaching materials)

### Who Owns This Structure?
- **Owner**: Chris (project lead)
- **Update frequency**: As needed (not scheduled)
- **Review**: Before major milestones (Phase 1.2, 2.0, etc.)

### Avoiding Structure Debt
- Archive or delete obsolete docs (don't hoard)
- Update READMEs when adding new files
- Link related docs bidirectionally
- Use consistent naming conventions
- Don't create folders until 3+ files need grouping

---

**Status**: 🟡 Draft - Awaiting Review  
**Next Action**: Review decision points & customize folder tree  
**Owner**: Chris  
**Last Updated**: October 9, 2025
