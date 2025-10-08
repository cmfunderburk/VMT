# Economic Simulation Platform: Project Skeleton Plan

**Project Name**: EconSim Platform  
**Project Type**: Desktop GUI Application with Educational Focus  
**Development Philosophy**: Self-Contained Visualization-First Agent-Based Economic Modeling

---

## Core Understanding

### 1. Problem & Success Definition

**Problem**: Build a comprehensive educational and research platform that implements the full breadth of modern microeconomic theory, starting with the foundational dual framework of preference relations and choice functions, then progressing through the complete spectrum of economic models. Use visualization-first development with spatial NxN grid simulations to demonstrate why these concepts are powerful and flexible analytical tools, combining interactive visual simulations with statistical dashboards for deep economic understanding and novel research investigation.

**Core Educational and Research Mission**: Establish the fundamental relationship between preference relations, choice functions, and utility functions through immediate spatial visualization, then build systematically through consumer theory, market equilibrium, game theory, information economics, and beyond. The platform serves as both an educational tool for building intuition about abstract economic concepts through concrete spatial interactions, and as a research instrument enabling investigation of advanced microeconomic phenomena, mechanism design, and spatial economic behavior for graduate students and researchers.

**Success Metrics** (≤120 words):

- **R-01**: Solo developer can accurately predict agent spatial behavior for all three preference types within 95% accuracy in blind testing scenarios
- **R-02**: Interactive parameter adjustments (preferences, constraints, spatial costs) produce immediate visual feedback and statistical updates within 1 second
- **R-03**: Platform exports simulation data in standard formats (CSV, JSON) with statistical summaries that match theoretical calculations within 99% accuracy
- **R-04**: Spatial grid simulations run consistently at 30+ FPS on development machine with identical agent behavior patterns across 10 test runs
- **R-05**: Foundational spatial architecture scales from simple utility maximization to complex multi-agent economic models and game theory
- **R-06**: Economic simulations reproduce theoretical predictions with mathematical accuracy while maintaining visual clarity and educational intuition
- **R-07**: Solo developer can correctly identify preference type from agent spatial behavior in blind tests with 90%+ accuracy, and visual behaviors are measurably distinct using spatial pattern metrics

### 2. Key User Scenarios (3-5 flows)

**S-01**: Economics Instructor wants to teach consumer choice fundamentals
Flow: Launch preference tutorial → Show Cobb-Douglas agent balancing both goods → Switch to Perfect Substitutes (agent focuses on cheaper good) → Switch to Leontief (agent takes fixed proportions) → Students predict behaviors before switching → Export results for homework
Success: Students understand that different people have different preference patterns, all representable within economic framework
Failure modes: Too many preference types confuse students, behavioral differences aren't visually distinct enough

**S-02**: Economics Student wants to explore utility maximization
Flow: Open spatial grid simulation → Place agent and valued items on grid → Set budget/movement constraints → Watch agent optimize spatially → Analyze statistical dashboard
Success: Student gains intuitive understanding of constrained optimization through spatial agent behavior
Failure modes: Agent behavior appears random, constraints unclear, statistical feedback inadequate

**S-03**: Educator wants to build custom economic scenarios
Flow: Use scenario builder → Define agent preferences and spatial constraints → Test educational effectiveness → Share with colleagues → Export for classroom use
Success: Custom scenarios effectively teach targeted economic concepts with measurable learning outcomes
Failure modes: Scenario builder too complex, scenarios don't align with educational objectives, sharing mechanisms fail

**S-04**: Researcher wants to implement new economic theory
Flow: Extend platform with new economic model → See immediate spatial visualization → Validate against theoretical predictions → Generate statistical analysis → Publish results
Success: New theory implementation matches analytical solutions and provides novel educational insights
Failure modes: Visualization doesn't illuminate theory, implementation contains theoretical errors, performance inadequate

**S-05**: Student wants to understand complex economic interactions
Flow: Progress through curriculum → Start with simple spatial choice → Build to multi-agent interactions → Explore game theory scenarios → Export analysis for projects
Success: Student builds understanding from concrete spatial interactions to abstract economic theory
Failure modes: Progression too steep, spatial metaphors break down for complex theory, analysis tools inadequate

**S-06**: Graduate Student/Researcher wants to investigate spatial economic phenomena
Flow: Design custom spatial scenario → Implement novel agent behaviors → Run large-scale simulations → Analyze emergent patterns → Export research-grade data and visualizations
Success: Novel insights about spatial economic behavior, publication-quality results, reproducible research methodology
Failure modes: Platform lacks flexibility for novel research questions, performance insufficient for research-scale simulations, data export inadequate for statistical analysis

### 3. System Sketch (components + data flow)

```markdown
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Spatial Foundation│◄──►│ Consumer Theory  │◄──►│ Educational UI  │
│      (M-01)      │    │     (M-02)       │    │     (M-03)      │
│ • NxN Grid       │    │ • Preferences    │    │ • Tutorials     │
│ • Agent Movement │    │ • Choice Functions│    │ • Explanations  │
│ • Constraints    │    │ • Utility Max    │    │ • Assessments   │
│ • Extensibility  │    │ • Custom Behaviors│    │ • Research UI   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │  Analytics Engine   │
                    │      (M-04)         │
                    │ • Statistical Dash  │
                    │ • Research Export   │
                    │ • Theory Validation │
                    │ • Reproducibility   │
                    └─────────────────────┘
```

**Data Flow**: Spatial Agent State → Economic Choice Calculation → Visual Rendering → Statistical Analysis → Research Data Export → Parameter Feedback → Spatial Update Loop

### 4. Risk Radar (top 5 risks with impact)

**R-01**: Visual complexity overwhelms educational value
Impact: High | Likelihood: Med
Validation: Solo developer testing with progressive complexity reveal and clear visual hierarchies
Mitigation: Progressive complexity reveal, simple defaults, iterative refinement based on solo development testing

**R-02**: Performance degrades below educational threshold (< 10 FPS) or research scale requirements
Impact: High | Likelihood: Med
Validation: Stress test with 1000+ agents for education, 10,000+ agents for research scale, profile rendering bottlenecks
Mitigation: Spatial partitioning, level-of-detail rendering, performance budgets per visual component, research-mode optimizations

**R-03**: Economic algorithms contain theoretical errors
Impact: High | Likelihood: Low
Validation: Compare simulation results against published analytical solutions for standard economic models
Mitigation: Theoretical validation test suite, economics expert code review, mathematical cross-reference system

**R-04**: Development complexity prevents rapid iteration and feature addition
Impact: Med | Likelihood: High
Validation: Track feature development velocity, measure time from concept to working visualization
Mitigation: Modular architecture with clear interfaces, comprehensive visual testing, hot-reload development environment

**R-05**: Research results lack reproducibility undermining scientific credibility
Impact: High | Likelihood: Low
Validation: Test scenario reproduction across different platforms and time periods with identical results
Mitigation: Comprehensive metadata tracking, deterministic random seeding, version control for all research parameters

**R-06**: Multiple preference types create cognitive overload instead of educational clarity
Impact: High | Likelihood: Med
Validation: Solo developer testing with clear behavioral differences between preference types, simple switching interface
Mitigation: Progressive disclosure in tutorials, visually distinct spatial behaviors, clear conceptual anchoring to "different people, different preferences"

### 5. Assumptions & Validation Experiments

**A-02**: Visual-first development improves code quality and reduces bugs
Counterpoint: Visual validation overhead might slow development without corresponding quality gains
Validation: Track bug rates, development velocity, and code review feedback compared to traditional TDD
Experiment: Develop same feature using visual-first vs traditional approaches, compare outcomes

**A-03**: Economic theory can be made visually intuitive without sacrificing mathematical rigor
Counterpoint: Visual simplification might lead to theoretical inaccuracies or oversimplification
Validation: Solo developer validation of visual representations against economic theory fundamentals
Experiment: Create utility function visualizer, validate mathematical accuracy against analytical solutions

**A-04**: Real-time parameter adjustment enhances learning effectiveness
Counterpoint: Too much interactivity might distract from core economic concepts
Validation: Measure learning outcomes with interactive vs static educational materials
Experiment: Build movement cost slider, measure student engagement and concept retention

**A-05**: Cross-platform Python/Pygame deployment is feasible for educational distribution
Counterpoint: Installation complexity might prevent adoption by educators
Validation: Solo developer testing of installation process across different platforms and configurations
Experiment: Create installation packages for each platform, test setup process across development environments

---

## Phase 2: Design Contracts (45 min)

### 6. Domain Model (core entities + relationships)

### 7. Core Interfaces (3-5 key APIs with intent)

### 8. Error Handling Strategy

**Educational Error Philosophy**: Transform computational errors into learning opportunities

**Error Categories**:

**Economic Errors (EC-01)**: Theoretical violations, convergence failures

- Strategy: Visual explanation of economic problem (e.g., "No equilibrium exists because...")
- Recovery: Suggest theoretically valid parameter adjustments with visual guidance
- Example: Market fails to clear → Show excess demand/supply visually, suggest price adjustments

**Educational Errors (ED-01)**: Confusing visualizations, theoretical inaccuracies

- Strategy: Immediate user feedback collection with alternative explanation generation
- Recovery: Revert to validated educational content, log for improvement
- Example: Student indicates confusion → Offer alternative explanation methods, simpler visualizations

**Error Logging Strategy**: All errors include educational context, student interaction history, and theoretical validation state for debugging learning effectiveness

### 9. Testing Strategy Outline

**Visual Test-Driven Development Philosophy**: Build tests that validate both computational correctness and educational effectiveness

**T-01**: Visual Regression Tests
Purpose: Ensure visual consistency and educational clarity across code changes
Method: Screenshot comparison with perceptual hashing and tolerance thresholds
Coverage: All major visual components, educational scenarios, cross-platform rendering
Test Example: `test_utility_curve_visualization()` captures and validates Cobb-Douglas curve shape

**T-02**: Economic Validation Tests
Purpose: Verify mathematical correctness against established economic theory
Method: Compare simulation results to analytical solutions from economics literature
Coverage: Utility maximization, equilibrium computation, welfare analysis, spatial economics
Test Example: `test_walrasian_equilibrium()` validates price discovery against analytical solution

**T-03**: Educational Content Validation Tests
Purpose: Validate theoretical accuracy and conceptual clarity of educational content
Method: Solo developer validation against economic theory principles, visual behavior verification
Coverage: Interactive tutorials, parameter adjustment exercises, visual explanations, theoretical accuracy
Test Example: `test_preference_type_behaviors()` validates that each preference type produces expected spatial patterns

### 10. Integration Points & Dependencies

**Core Dependencies**:

- **Python 3.11+**: Type hints, dataclasses, performance improvements for educational responsiveness
- **PyQt6**: Professional desktop GUI framework with OpenGL integration for Pygame embedding
- **Pygame 2.5+**: Real-time visualization engine embedded within PyQt6 interface
- **NumPy 1.24+**: Efficient numerical computation for economic calculations
- **SciPy 1.10+**: Optimization algorithms for equilibrium solving, statistical analysis

**Desktop Application Dependencies**:

- **PyInstaller 6.0+**: Cross-platform application packaging for self-contained distribution
- **Pillow**: Image processing for icons, splash screens, and visual assets

**Development Dependencies**:

- **pytest 7.4+**: Testing framework with visual testing extensions
- **Black 23.0+**: Code formatting for educational code clarity
- **mypy 1.5+**: Type checking for educational code reliability

**Educational Dependencies** (Optional):

- **Pillow**: Image processing for visual regression testing
- **imageio**: Animation export for educational presentations
- **pandas**: Data analysis for educational metrics

**Integration Strategy**:

- **Zero External Services**: Fully self-contained educational tool, no network dependencies
- **Minimal Dependencies**: Reduce complexity for educational deployment
- **Version Pinning**: Ensure reproducible educational environments
- **Graceful Degradation**: Optional dependencies enhance but don't break core functionality

**No Integration Points**:

- No databases (educational scenarios use generated data)
- No web APIs (standalone educational tool)
- No cloud services (privacy and accessibility for education)
- No real-time data feeds (focus on theoretical economic models)

---

## Phase 3: Implementation Readiness (30 min)

### 11. Directory Structure & File Plan

> Needs to be filled in post refactor

### 12. Tooling & Quality Setup

**Development Toolchain** (D-01: Educational-focused development environment):

| Tool | Purpose | Educational Rationale | Quality Gate |
|------|---------|----------------------|--------------|
| **Black** | Code formatting | Clear, readable code for educational use | Q-01: Pre-commit autoformat |
| **Ruff** | Linting | Fast, comprehensive error detection | Q-02: Zero lint errors allowed |
| **mypy** | Type checking | Reliable educational software | Q-03: 100% type coverage |
| **pytest** | Test runner | Comprehensive testing with visual extensions | Q-04: 90% test coverage minimum |
| **pytest-visual** | Visual testing | Automated educational content validation | Q-05: All visual components tested |

### 14. Implementation Roadmap (MVP focus)

**Week 0: Technology Validation** (5-7 days)

**MVP Milestone 1: Spatial Foundation** (Week 1-2)

- **MVP Components**: S-03, S-04, S-06, S-02 - NxN grid, spatial agents, visualization, application entry
- **Success Criteria**: Grid renders with agents at 60+ steps per second, agents move smoothly with spatial constraints
- **Educational Validation**: Solo developer verification that spatial agent movement is clear and intuitive
- **Risk Mitigation**: Focus on rock-solid spatial foundation that scales to complex economic behavior

**MVP Milestone 2: Flexible Preference/Utility Architecture** (Week 3-4)

- **MVP Components**: S-08 foundation - Extensible utility function architecture, parameter adjustment interface
- **Success Criteria**: Preference system can support multiple function types, parameter changes propagate immediately to visualization
- **Educational Validation**: Architecture supports clear switching between different preference patterns
- **Risk Mitigation**: Build extensible system from start to avoid refactoring when adding preference types

**MVP Milestone 3: Three Core Preference Types** (Week 5-6)

- **MVP Components**: S-08, S-09, S-10 completion - Cobb-Douglas, Perfect Substitutes, Perfect Complements implementations with choice functions and utility optimization
- **Success Criteria**: Agent demonstrates visually distinct spatial behaviors for each preference type, mathematical accuracy validated against theory
- **Educational Validation**: Each preference type produces clearly different spatial choice patterns
- **Risk Mitigation**: Validate mathematical correctness before visual implementation, ensure behavioral differences are obvious

**MVP Milestone 4: Spatial Choice Integration** (Week 7)

- **MVP Components**: S-05 - Spatial choice modeling connecting all preference types to grid-based optimization
- **Success Criteria**: All three preference types work seamlessly with spatial constraints and produce optimal choices
- **Educational Validation**: Agent choice behavior matches theoretical predictions for each preference type
- **Risk Mitigation**: Comprehensive testing of preference-constraint interactions

**MVP Milestone 5: Educational Interface** (Week 8)

- **MVP Components**: S-18, S-19, S-13, S-14 - Progressive preference tutorial, comparative explanations, statistical dashboard, economic metrics
- **Success Criteria**: Complete tutorial system showcasing all three preference types, real-time parameter adjustment with statistical feedback
- **Educational Validation**: Solo developer testing confirms tutorial effectively demonstrates preference flexibility concept
- **Risk Mitigation**: Progressive disclosure prevents cognitive overload, clear conceptual anchoring throughout

**Post-MVP Phase 1: Consumer Theory Extension** (Week 9-12)

- **Post-MVP Components**: S-11, S-15, S-17 - Demand theory, export capabilities, advanced visualizations
- **Success Criteria**: Full consumer theory curriculum with demand curves, consumer surplus, comparative statics
- **Educational Validation**: Advanced consumer theory concepts accessible through spatial demonstration
- **Extensions**: Income effects, substitution effects, welfare analysis, comparative statics

**Post-MVP Phase 2: Research Enhancement** (Week 13-16)

- **Post-MVP Components**: S-24, S-16 - Research reproducibility, statistical validation, custom behavior modeling
- **Success Criteria**: Platform supports novel research investigations with full reproducibility
- **Educational Validation**: Research capabilities enhance rather than complicate educational use
- **Extensions**: Custom agent behaviors, large-scale simulations, publication-quality data export

**Post-MVP Phase 3: Multi-Agent and Market Theory** (Week 17-22)

- **Post-MVP Components**: S-20, S-21, S-22 - Multi-agent scenarios, assessment tools, curriculum sequencing
- **Success Criteria**: Multiple agents interacting spatially, early market formation, equilibrium concepts
- **Educational Validation**: Progression from individual choice to market interactions maintains clarity
- **Extensions**: Simple trading, price formation, market efficiency, strategic interactions

**Post-MVP Phase 4: Advanced Theory Integration** (Week 23+)  

- **Deferred Components**: Game theory, information economics, mechanism design, behavioral economics
- **Success Criteria**: Full microeconomic theory curriculum with spatial intuition maintained throughout
- **Educational Validation**: Platform adopted by economics educators for comprehensive theory instruction
- **Extensions**: Research-grade simulations, publication-quality analysis, community content creation

**Deferred Features**:

- Web-based deployment (maintain desktop focus initially)
- 3D visualization options (2D sufficient for core concepts)
- Multi-threaded performance optimization (educational scale sufficient)
- Advanced econometric analysis (focus on core microeconomic theory)
- Real-time collaborative features (single-user educational tool initially)

### 15. Decision Log & Next Steps

#### D-01: Interface Architecture Choice

#### D-02: Visualization Technology Choice

- **Context & Forces**: Need high-performance real-time visualization embedded within desktop GUI framework
- **Criteria**: Performance for real-time simulation, educational visual clarity, solo developer learning curve
- **Decision**: Pygame embedded in PyQt6 QOpenGLWidget
- **Rationale**: Combines Pygame's educational visualization strengths with PyQt6's professional GUI capabilities
- **Consequences**: (+) Best of both frameworks, (-) Integration complexity during development
- **Revisit Conditions**: If PyQt6-Pygame integration proves too complex during Week 0 validation
- **Review Date**: End of Week 0 technology validation

#### D-02: Economic Theory Validation Strategy

- **Context & Forces**: Must ensure mathematical correctness for educational integrity while maintaining development velocity
- **Options**: (1) Manual expert review, (2) Automated testing against analytical solutions, (3) Academic collaboration
- **Criteria**: Correctness guarantee, scalability, development integration, credibility with educators
- **Decision**: Automated validation against established economic solutions + expert review for new features
- **Rationale**: Scalable correctness validation with expert oversight for novel implementations
- **Consequences**: (+) High confidence in educational accuracy, (-) Requires building validation framework
- **Revisit Conditions**: If validation framework becomes maintenance burden or expert review unavailable
- **Review Date**: After economic engine implementation

#### D-03: Educational Content Development Approach

- **Context & Forces**: Balance between comprehensive economic coverage and development resources
- **Options**: (1) Build comprehensive content library, (2) Minimal examples with extension points, (3) Community-driven content
- **Criteria**: Educational completeness, development time, maintainability, community adoption potential
- **Decision**: Minimal high-quality examples with clear extension framework for educator customization
- **Rationale**: Enables rapid MVP delivery while supporting diverse educational needs
- **Consequences**: (+) Faster time to market, educator flexibility, (-) Initial content limited
- **Revisit Conditions**: If educators need more comprehensive out-of-box content
- **Review Date**: After initial educator testing

#### D-06: MVP Theory Scope - Multiple Preference Functions

- **Context & Forces**: Balance between educational completeness and implementation complexity for MVP validation
- **Options**: (1) Single preference function for simplicity, (2) Two preference functions for trade-offs, (3) Three preference functions for pedagogical robustness
- **Criteria**: Educational impact, addresses student criticism, implementation feasibility, instructor adoption potential
- **Decision**: Three preference functions (Cobb-Douglas, Perfect Substitutes, Leontief) in MVP
- **Rationale**: Addresses "people don't behave like that" criticism immediately, demonstrates framework flexibility, transforms common objection into strength
- **Consequences**: (+) Stronger pedagogical foundation, addresses realism concerns, (-) Increased implementation complexity, longer development time
- **Revisit Conditions**: If implementation complexity becomes unmanageable or solo development testing shows single preference is sufficient
- **Review Date**: After MVP completion and solo validation testing

#### ❗Needs-Decision[D-05]: Assessment and Learning Analytics Strategy

- **Context**: Educational effectiveness measurement approaches vary significantly
- **Options**: (1) Built-in assessment tools, (2) External analytics integration, (3) Simple interaction logging
- **Required Decision**: Level of learning analytics integration for educational validation
- **Timeline**: Before educational interface implementation

**Extended Skeleton Artifacts**:

**Scaffold Generation Checklist**:

1. [ ] S-01: Initialize Python package structure with proper `__init__.py` files
2. [ ] S-02: Create main application entry point with GUI and command-line interface
3. [ ] S-03: Implement NxN grid world with spatial indexing for performance
4. [ ] S-04: Build spatial agents with movement and constraint systems
5. [ ] S-05: Create spatial choice modeling and optimization visualization
6. [ ] S-06: Develop spatial rendering engine with Pygame and animation support
7. [ ] S-07: Implement movement costs, barriers, and spatial constraints
8. [ ] S-08: Build three core preference types (Cobb-Douglas, Perfect Substitutes, Leontief) with parameter adjustment systems
9. [ ] S-09: Create rational choice functions supporting all preference types and revealed preference analysis
10. [ ] S-10: Implement utility function calculations and spatial optimization for all three preference types
11. [ ] S-11: Build demand theory and consumer surplus analysis
12. [ ] S-12: Create economic theory validation and testing framework
13. [ ] S-13: Develop interactive statistical dashboards with real-time updates
14. [ ] S-14: Build economic metrics and KPI calculation systems
15. [ ] S-15: Implement data export and visualization export capabilities
16. [ ] S-16: Create statistical validation of economic theory predictions
17. [ ] S-17: Build publication-quality plots and charts generation
18. [ ] S-18: Develop progressive economic concept tutorials
19. [ ] S-19: Create dynamic concept explanations with contextual help
20. [ ] S-20: Build pre-configured educational economic scenarios
21. [ ] S-21: Implement learning effectiveness measurement and assessment tools
22. [ ] S-22: Create curriculum sequencing and progression management
23. [ ] S-23: Write comprehensive getting started and educator guides
24. [ ] S-24: Implement research reproducibility and metadata management system

**README Seed Outline**:

```markdown
# EconSim Platform: Visual Economic Simulation for Education

## Quick Start
<!-- Reference to S-02, S-23 -->

## Educational Philosophy  
<!-- Reference to educational approach, Section 1 -->

## Installation
<!-- Reference to development setup, S-01 -->

## Basic Usage
<!-- Reference to tutorials, S-16 -->

## Economic Concepts Covered
<!-- Reference to scenarios, S-18 -->

## For Educators
<!-- Reference to educational guide -->

## For Developers
<!-- Reference to development documentation -->

## Contributing
<!-- Reference to development workflows -->

**Quality Gates Summary**:

| Q-ID | Name | Stage | Tool | Blocking? | Signal | Auto-fix |
|------|------|-------|------|-----------|--------|----------|
| Q-01 | Code Format | pre-commit | Black | Yes | Non-standard format | black --fix |
| Q-02 | Lint Clean | pre-commit | Ruff | Yes | Lint errors | ruff --fix |
| Q-03 | Type Safety | CI | mypy | Yes | Type errors | Manual fix required |
| Q-04 | Test Coverage | CI | pytest | Yes | <90% coverage | Write additional tests |
| Q-05 | Visual Consistency | CI | pytest-visual | Yes | Visual regression | Manual review required |
| Q-06 | Economic Accuracy | CI | validation framework | Yes | Theory mismatch | Expert review required |
| Q-07 | Educational Effectiveness | Release | User testing | No | Low comprehension | Content revision |

---

## Patch Notes

**Added IDs**:

**Rationale**:
