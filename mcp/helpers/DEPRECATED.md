# DEPRECATED: MCP Helpers

**Status**: Deprecated - Migration to `mcp/simple/` in progress

This directory contains legacy MCP helper implementations that are being migrated
to the new MCPBase class architecture in `mcp/simple/`.

## Migration Status

| Helper | Status | New Location |
|--------|--------|--------------|
| script_ops.py | ✅ Migrated | mcp/simple/script_ops.py |
| repository_manager.py | ⚠️ Pending | mcp/simple/repository_ops.py |
| action_logger.py | ⚠️ Pending | mcp/simple/action_logger.py |
| layer_manager.py | ⚠️ Pending | mcp/simple/layer_manager.py |
| model_inspector.py | ⚠️ Pending | mcp/simple/model_inspector.py |
| pulse_generator.py | ⚠️ Pending | mcp/simple/pulse_generator.py |
| repository_analyzer.py | ⚠️ Pending | workflows/tools/analyze/repository_analyzer.py |
| script_manager.py | ⚠️ Pending | mcp/simple/script_manager.py |
| data_analyzer.py | ⚠️ Pending | mcp/simple/data_analyzer.py |

## Timeline

- **Phase 2 Week 1-2**: Migrate all helpers to new architecture
- **Phase 2 Week 3**: Deprecate this directory completely
- **Phase 2 Complete**: Remove this directory

## For Developers

**Do not add new code to this directory.** All new MCP operations should be
implemented in `mcp/simple/` (Tier 1) or `workflows/` (Tier 2) using the
MCPBase class architecture.

See `docs/PHASE2_PLAN.md` for migration guide.
