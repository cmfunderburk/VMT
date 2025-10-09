# Choice and Preferences

**Model Type**: Foundation - Single Agent Preferences Demonstration  
**Purpose**: Demonstrate how agents make choices based on their preferences; show flexibility of mathematical framework for predicting choice behavior rather than descriptions of psychological processes.

---

## Overview

This document provides the complete mathematical specification for single-agent preferences and choice behavior in a spatial grid environment. It bridges classical microeconomic theory (utility maximization, marginal utility, indifference curves) with spatial implementation (distance costs, discrete goods, grid-based movement).

**Educational Goal**: Students should be able to predict agent behavior from utility functions alone, understanding how preferences interact with spatial costs.

---

### 0.0 Default Grid Setup for Demonstrations

  - 5x5 grid.
  - Agent spawns at (1,1).
  - Preference parameters are normalized to 1 (alpha + beta = 1).
  - Epsilon is 0.001.
  - Distance discount constant is configurable, default is 0.
  - Perception radius is configurable, default is 8.
  - Carry capacity is 10.
  - Home storage is unlimited.
  - Inventory is carried and home storage.
  - Inventory is discrete and integer.
  - Inventory is stored in a dictionary with keys "good1" and "good2".
  - Resources spawn at random locations in the grid.

  ## 1. Agent Decision Problem (Spatial Context)