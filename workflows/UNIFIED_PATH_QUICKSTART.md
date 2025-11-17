# Unified @path Analysis - Quick Start Guide

## Overview

The unified `@path` analysis system provides a single, intuitive syntax for analyzing both files and repositories. The system automatically detects what you're analyzing and loads relevant context from previous analyses.

## Basic Usage

### Analyze a Repository

**Option 1: Natural Language (NEW!)**

Simply type "analyze" or "analyse" followed by the directory name:

```
analyze myproject
analyse framework
check repository testudo
```

The system will automatically detect "myproject" as a directory in your current location and analyze it.

**Option 2: Explicit @path Syntax**

Use `@` followed by the path to your repository:

```
@C:\Users\yourname\projects\myproject
```

or on Unix/Linux:

```
@/home/yourname/projects/myproject
```

**What happens:**
1. System detects it's a directory
2. Runs full repository analysis
3. Saves results to `.pulsus/repository_analysis.json` in the repo root
4. Displays health assessment, statistics, and insights

### Analyze a File

Use `@` followed by the path to a Python file:

```
@C:\Users\yourname\projects\myproject\src\module.py
```

**What happens:**
1. System detects it's a file
2. Looks for parent repository (walks up to find .git, setup.py, etc.)
3. **Loads repository context if available** from `.pulsus/`
4. Analyzes file WITH repository context
5. Shows comparisons like "This file has 1 issue vs repo avg of 2.1"

## Natural Language Support (NEW!)

The system now supports natural language commands without requiring `@` syntax:

### Supported Patterns

```
analyze framework          # American spelling
analyse testudo            # British spelling
check repository myproject # Alternative verbs
inspect mydir              # Works too!
review project123          # Also supported
run analysis on framework  # Various phrasings
```

### How It Works

1. System detects analysis keywords: `analyze`, `analyse`, `check`, `inspect`, `review`
2. Extracts the directory name following the keyword
3. Resolves the path relative to your current directory
4. Validates the path exists
5. Routes to appropriate analyzer

### When to Use Natural Language vs @path

**Use Natural Language** (simpler directory names):
- `analyse framework`
- `check testudo`
- `analyze myproject`

**Use @path Syntax** (complex paths):
- `@"my project"` (spaces in name)
- `@C:\full\path\to\repo` (full paths)
- `@../relative/path` (relative with separators)

## Advanced Features

### Force Refresh Repository Analysis

If you've already analyzed a repository and want to re-run the analysis:

```
analyze repository @C:\path\to\repo with force_refresh=True
```

This bypasses the cache and performs a fresh analysis.

### View Cached Analysis

When you run analysis on a repository that was previously analyzed:

```
@C:\path\to\repo
```

**Output:**
```
[*] Found cached analysis (age: 2.3 hours)
[*] Loading from .pulsus/repository_analysis.json...
[*] Using cached analysis. To force refresh, use force_refresh=True
```

## Context-Aware Operations

### Function Commenting with Repository Patterns

When you generate function comments for a file in an analyzed repository:

```
comment functions in @C:\path\to\repo\file.py
```

The system will:
- Load repository context from `.pulsus/`
- Follow existing naming conventions from the repo
- Use repository-specific terminology and patterns

### File Analysis with Repository Insights

When analyzing a file that's part of a repository:

```
@C:\path\to\repo\src\module.py
```

You'll see:
```
[*] Repository context loaded
    - Compliance: 85.2%
    - Total files: 47
    - Avg issues/file: 2.1

[ANALYSIS RESULTS]
...
⚠️  This file has 5 issues vs repo average of 2.1

💡 Top reusable functions in repository:
   - format_data() (score: 12/15)
   - validate_input() (score: 11/15)
```

## The .pulsus/ Directory

### What is it?

When you analyze a repository, the system creates a `.pulsus/` directory in the repository root:

```
myproject/
├── .git/
├── .pulsus/
│   └── repository_analysis.json  ← Analysis cache
├── src/
├── tests/
└── README.md
```

### What's stored?

The `.pulsus/repository_analysis.json` file contains:
- Repository health assessment
- Statistics (files, functions, classes, LOC)
- Issues summary (by priority and type)
- Reusability scores for functions
- Metadata (timestamp, version)

### Why is it useful?

1. **Speed**: Second analysis is instant (loads from cache)
2. **Context**: File analysis uses repository context
3. **Consistency**: Same insights across multiple sessions
4. **Portability**: Can be committed to git for team sharing

## Workflow Examples

### Example 1: New Repository Analysis

```
Step 1: Analyze repository
> @C:\projects\myapp

[*] Analyzing repository: C:\projects\myapp
[*] Please wait, this may take a moment...
[...analysis output...]
[*] Analysis saved to .pulsus/repository_analysis.json
```

```
Step 2: Analyze specific file (uses repo context)
> @C:\projects\myapp\src\utils.py

[*] Detected file: C:\projects\myapp\src\utils.py
[*] Loading repository context from: C:\projects\myapp
[*] Repository context loaded successfully
    - Repository: myapp
    - Total files: 47
    - Compliance: 85.2%
[...file analysis with context...]
```

### Example 2: Re-analyzing After Changes

```
> @C:\projects\myapp

[*] Found cached analysis (age: 0.5 hours)
[*] Loading from .pulsus/repository_analysis.json...
[*] Using cached analysis. To force refresh, use force_refresh=True
[...cached results...]
```

```
> analyze repository @C:\projects\myapp force_refresh

[*] Analyzing repository: C:\projects\myapp
[*] Please wait, this may take a moment...
[...fresh analysis...]
```

### Example 3: Analyzing Multiple Files

```
> @C:\projects\myapp\src\database.py
[...analysis with repo context...]

> @C:\projects\myapp\src\api.py
[...analysis with same repo context (cached)...]

> @C:\projects\myapp\tests\test_utils.py
[...analysis with same repo context (cached)...]
```

Notice: After the first file, repository context is cached in memory for the session.

## Tips and Best practices

### 1. Analyze Repository First

For best results, analyze the repository before analyzing individual files:

```
Step 1: @C:\path\to\repo           ← Repository analysis
Step 2: @C:\path\to\repo\file.py   ← File analysis with context
```

### 2. Commit .pulsus/ to Git (Optional)

You can add `.pulsus/` to your repository to share analysis with your team:

```bash
git add .pulsus/
git commit -m "Add repository analysis cache"
```

Or exclude it by adding to `.gitignore`:

```
.pulsus/
```

### 3. Refresh After Major Changes

After significant refactoring or adding many files:

```
analyze repository @C:\path\to\repo force_refresh
```

### 4. Path Formats Supported

The system accepts multiple path formats:

- **Windows absolute**: `@C:\Users\name\projects\repo`
- **Windows with forward slash**: `@C:/Users/name/projects/repo`
- **Unix absolute**: `@/home/name/projects/repo`
- **Relative**: `@./src/module.py` or `@../other-project`

## Troubleshooting

### "No repository context found"

This means:
- The file isn't part of a recognized repository, OR
- The repository hasn't been analyzed yet

**Solution**: Analyze the repository first:
```
@C:\path\to\repo
```

### "Could not save to .pulsus/ directory"

Possible causes:
- Insufficient permissions
- Disk full
- Path doesn't exist

**Solution**: Check permissions and ensure the repository root is writable.

### "Path does not exist"

Double-check the path:
- Use absolute paths for clarity
- On Windows, use `\` or `/` (both work)
- Ensure no typos in the path

## What's Next?

After analyzing your repository and files:

1. **Generate function comments**: `comment functions in @path\to\file.py`
2. **Create documentation**: `generate docs for @path\to\file.py`
3. **Ask follow-up questions**: The system remembers your current context

## Summary

The unified `@path` system provides:
- ✅ Single syntax for files and directories
- ✅ Automatic context loading from `.pulsus/`
- ✅ Repository-aware file analysis
- ✅ Intelligent caching for performance
- ✅ Insights and comparisons

Just use `@path` and let the system figure out the rest!
