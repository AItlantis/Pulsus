# Routing Enhancements - Implicit Path Detection

## Issue Identified

**Problem**: When users type natural language commands like `analyse framework`, the system would fall back to a generic generator instead of recognizing it as a repository analysis request.

**Example of the issue**:
```
[YOU] > analyse framework

[SYSTEM] No suitable candidates; falling back to generator
         Generated: "Hey! I see you mentioned 'analyse framework'—could you
         clarify which framework you're referring to?"
```

**Expected behavior**: The system should recognize "framework" as a directory name and route to repository analysis.

## Solution Implemented

### 1. Implicit Path Pattern Matching

Enhanced `mcp_router.py` to detect implicit path references in natural language:

**Supported patterns**:
- `analyze framework` → detects "framework" as potential directory
- `analyse mydir` → British spelling support
- `check repository myproject` → alternative verbs
- `run analysis on testudo` → various phrasings

**Pattern regex**:
```python
implicit_patterns = [
    r'(?:analys[ez])\s+(?:repository\s+)?([a-zA-Z0-9_\-\.]+)(?:\s|$)',
    r'(?:check|inspect|review)\s+(?:repository\s+)?([a-zA-Z0-9_\-\.]+)(?:\s|$)',
    r'(?:run\s+)?(?:repository\s+)?(?:analys[ei]s)\s+(?:on\s+)?([a-zA-Z0-9_\-\.]+)(?:\s|$)',
]
```

### 2. Path Validation

When a pattern matches, the system:
1. Extracts the potential path name (e.g., "framework")
2. Checks if it's an absolute path
3. If not, resolves relative to current working directory
4. Verifies if the path exists

**Routing logic**:
```python
if path_obj.exists():
    # Valid path found - route to analyze_path with high confidence
    return ParsedIntent(
        domain="analysis",
        action="analyze_path",
        intent=f"@{path_obj}",  # Convert to @path syntax
        confidence=0.90
    )
else:
    # Path doesn't exist but pattern matched
    # Route to analyze_repository with medium confidence
    return ParsedIntent(
        domain="analysis",
        action="analyze_repository",
        intent=text,
        confidence=0.75
    )
```

### 3. British vs American Spelling

The regex pattern `analys[ez]` matches both:
- `analyze` (American)
- `analyse` (British)

Additional keywords added to `repository_analysis.json`:
- `"analyse"` (British spelling)
- `"repo"` (shorthand)
- `"check"`, `"inspect"`, `"review"` (alternative verbs)

## Priority Order

The routing now follows this priority:

1. **Explicit @path syntax** (confidence: 0.95)
   - `@C:\path\to\dir`
   - `@/path/to/file.py`

2. **Implicit path patterns** (confidence: 0.90 if exists, 0.75 if not)
   - `analyse framework`
   - `analyze myproject`
   - `check repository testudo`

3. **Workflow semantic matching** (confidence: 0.5-0.95)
   - Based on keywords and descriptions

4. **MCP tool matching** (confidence: 0.5-0.95)
   - Based on tool metadata

5. **Fallback to generator** (confidence: 0.3)
   - When no good match found

## Examples

### Example 1: Existing Directory
```
Input: "analyse framework"

Processing:
1. Pattern matches: "framework" extracted
2. Path resolved: C:\Users\...\Atlantis\framework
3. Path exists: Yes
4. Route: analyze_path (confidence: 0.90)
5. Intent converted to: "@C:\Users\...\Atlantis\framework"

Result:
→ Runs repository analysis on framework directory
→ Saves to .pulsus/repository_analysis.json
```

### Example 2: Non-existent Directory
```
Input: "analyze nonexistent"

Processing:
1. Pattern matches: "nonexistent" extracted
2. Path resolved: C:\Users\...\Atlantis\nonexistent
3. Path exists: No
4. Route: analyze_repository (confidence: 0.75)
5. Intent unchanged: "analyze nonexistent"

Result:
→ Routes to repository analysis workflow
→ Workflow will handle non-existent path error
```

### Example 3: British Spelling with Variants
```
Input: "analyse testudo repository"

Processing:
1. Pattern matches: "testudo" extracted (with "repository" keyword)
2. Path resolved: C:\Users\...\Atlantis\testudo
3. Path exists: Yes
4. Route: analyze_path (confidence: 0.90)
5. Intent converted to: "@C:\Users\...\Atlantis\testudo"

Result:
→ Runs repository analysis on testudo directory
```

### Example 4: Alternative Verbs
```
Input: "check myproject"

Processing:
1. Pattern matches: "myproject" extracted
2. Path resolved: C:\Users\...\Atlantis\myproject
3. Path exists: Yes/No (either way, pattern matched)
4. Route: analyze_path or analyze_repository

Result:
→ Routes to appropriate analyzer
```

## Backward Compatibility

All existing functionality remains intact:

✅ `@C:\explicit\path` still works (highest priority)
✅ Workflow keyword matching still works
✅ MCP tool matching still works
✅ Generator fallback still works

New functionality is **additive** and doesn't break existing behavior.

## Benefits

### For Users
- More natural language support
- Don't need to remember `@` syntax for simple cases
- British spelling support (analyse vs analyze)
- Flexible command variations

### For System
- Higher routing accuracy
- Better user intent detection
- Reduced fallback to generator
- Improved user experience

## Limitations

### Current Limitations
1. **Simple names only**: Only matches simple directory names (alphanumeric, dash, underscore, dot)
2. **No complex paths**: Won't match paths with spaces or special characters
3. **CWD relative**: Paths resolved relative to current working directory

### Not Matched (use @path syntax instead)
- `analyse my project` (space in name) → use `@"my project"`
- `analyse C:\full\path` (already a path) → use `@C:\full\path`
- `analyse ../parent/dir` (path separator) → use `@../parent/dir`

## Testing

### Test Cases

**Should match and route correctly**:
```
✓ "analyse framework"
✓ "analyze testudo"
✓ "check repository myproject"
✓ "inspect mydir"
✓ "review project123"
✓ "run analysis on framework"
```

**Should still use fallback (no implicit path)**:
```
✗ "what is a framework"
✗ "explain the framework"
✗ "how to analyze"
```

**Should use explicit @path (higher priority)**:
```
✓ "@framework" (explicit)
✓ "@C:\full\path"
✓ "@../relative/path"
```

## Implementation Files Changed

1. **testudo/agents/pulsus/routing/mcp_router.py**
   - Added implicit path pattern detection
   - Added path validation logic
   - Maintains priority ordering

2. **testudo/agents/pulsus/workflows/repository_analysis.json**
   - Added British spelling: `"analyse"`
   - Added alternative verbs: `"check"`, `"inspect"`, `"review"`
   - Added shorthand: `"repo"`

## Usage Recommendation

### Recommended (New)
```
analyse framework          # Simple, natural
analyze testudo            # American spelling
check myproject            # Alternative verb
```

### Still Valid (Original)
```
@framework                 # Explicit syntax
@C:\full\path\to\repo     # Full paths
@../relative/path          # Relative paths
```

### When to Use @path Syntax
- Paths with spaces: `@"my project"`
- Full paths: `@C:\Users\name\projects\repo`
- Relative paths with separators: `@../other-project`
- When implicit detection isn't working

## Summary

The routing enhancement makes the system more user-friendly by:
1. Supporting natural language commands
2. Detecting implicit directory references
3. Supporting British spelling variants
4. Providing intelligent path resolution

Users can now type `analyse framework` instead of `@framework`, making the interface more intuitive while maintaining all existing functionality.
