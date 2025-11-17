# UTF-8
"""
Domain Validator - Validates domain/action pairs against config
"""
from typing import Dict, List, Optional, Tuple
import json
import os
from difflib import get_close_matches
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Structured validation result"""
    status: str  # "ok", "invalid_domain", "invalid_action", "unclear", "need_user_input"
    domain: Optional[str] = None
    action: Optional[str] = None
    need_context: bool = False
    message: str = ""
    suggestions: List[str] = None
    app_support: List[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "status": self.status,
            "domain": self.domain,
            "action": self.action,
            "need_context": self.need_context,
            "message": self.message,
            "suggestions": self.suggestions or [],
            "app_support": self.app_support or []
        }


class DomainValidator:
    """Validates domain/action pairs and provides fuzzy matching"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize validator with config file

        Args:
            config_path: Path to domains.json (defaults to config/domains.json)
        """
        if config_path is None:
            # Default to config/domains.json relative to this file
            base_dir = os.path.dirname(os.path.dirname(__file__))
            config_path = os.path.join(base_dir, "config", "domains.json")

        self.config_path = config_path
        self.config = self._load_config()
        self.domains = self.config.get("domains", {})
        self.fuzzy_threshold = self.config.get("fuzzy_match_threshold", 0.6)
        self.fallback_domain = self.config.get("fallback_domain", "Documentation")

    def _load_config(self) -> dict:
        """Load domains.json configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                "Please ensure config/domains.json exists."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def get_all_domains(self) -> List[str]:
        """Get list of all valid domains"""
        return list(self.domains.keys())

    def get_actions_for_domain(self, domain: str) -> List[str]:
        """Get list of valid actions for a domain"""
        if domain not in self.domains:
            return []
        return self.domains[domain].get("actions", [])

    def validate(self, domain: str, action: str, app: Optional[str] = None) -> ValidationResult:
        """
        Validate a domain/action pair

        Args:
            domain: The domain name (e.g., "Traffic Demand")
            action: The action name (e.g., "Generate OD matrix")
            app: Optional app context ("aimsun" or "qgis")

        Returns:
            ValidationResult with status and details
        """
        # Check if domain exists
        if domain not in self.domains:
            # Try fuzzy matching
            suggestions = get_close_matches(
                domain,
                self.get_all_domains(),
                n=3,
                cutoff=self.fuzzy_threshold
            )

            return ValidationResult(
                status="invalid_domain",
                domain=domain,
                action=action,
                message=f"Unknown domain '{domain}'",
                suggestions=suggestions
            )

        # Domain is valid, check action
        domain_config = self.domains[domain]
        valid_actions = domain_config.get("actions", [])

        # Check exact match first
        matched_action = None
        if action in valid_actions:
            matched_action = action
        else:
            # Try case-insensitive match
            action_lower = action.lower()
            for valid_action in valid_actions:
                if valid_action.lower() == action_lower:
                    matched_action = valid_action
                    break

        if not matched_action:
            # Try fuzzy matching for actions
            suggestions = get_close_matches(
                action,
                valid_actions,
                n=3,
                cutoff=self.fuzzy_threshold
            )

            # If fuzzy match found with high confidence, use it
            if suggestions and len(suggestions) > 0:
                # Check if it's a very close match (>0.8 similarity)
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, action.lower(), suggestions[0].lower()).ratio()
                if similarity > 0.85:
                    matched_action = suggestions[0]
                else:
                    return ValidationResult(
                        status="invalid_action",
                        domain=domain,
                        action=action,
                        message=f"Unknown action '{action}' in domain '{domain}'",
                        suggestions=suggestions
                    )
            else:
                return ValidationResult(
                    status="invalid_action",
                    domain=domain,
                    action=action,
                    message=f"Unknown action '{action}' in domain '{domain}'",
                    suggestions=suggestions
                )

        # Use the matched action (may be corrected)
        action = matched_action

        # Check app compatibility if specified
        app_support = domain_config.get("app", [])

        # Normalize app value (handle "null" string from LLM)
        if app in ["null", "None", ""]:
            app = None

        if app and app not in app_support:
            return ValidationResult(
                status="invalid_app",
                domain=domain,
                action=action,
                message=f"Domain '{domain}' not supported in {app}. Supported: {', '.join(app_support)}",
                app_support=app_support
            )

        # Check if action requires context
        requires_context = domain_config.get("requires_context", [])
        need_context = action in requires_context if isinstance(requires_context, list) else requires_context

        # All valid!
        return ValidationResult(
            status="ok",
            domain=domain,
            action=action,
            need_context=need_context,
            message=f"Valid: {domain} → {action}",
            app_support=app_support
        )

    def parse_and_validate(self, domain: Optional[str], action: Optional[str],
                          app: Optional[str] = None) -> ValidationResult:
        """
        Parse potentially None values and validate

        Args:
            domain: Domain name (may be None if unclear)
            action: Action name (may be None if unclear)
            app: App context

        Returns:
            ValidationResult
        """
        # Handle unclear classification
        if not domain or not action:
            missing = []
            if not domain:
                missing.append("domain")
            if not action:
                missing.append("action")

            return ValidationResult(
                status="unclear",
                domain=domain,
                action=action,
                message=f"Could not determine: {', '.join(missing)}",
                suggestions=self.get_all_domains() if not domain else []
            )

        # Proceed with validation
        return self.validate(domain, action, app)

    def get_context_keywords(self) -> Dict[str, List[str]]:
        """Get context detection keywords"""
        return self.config.get("context_keywords", {})

    def suggest_from_keywords(self, text: str) -> Tuple[Optional[str], List[str]]:
        """
        Suggest domain based on keywords in text

        Args:
            text: User input text

        Returns:
            (suggested_context, matching_domains)
        """
        text_lower = text.lower()
        context_keywords = self.get_context_keywords()
        matching_contexts = []

        # Check which contexts match
        for context, keywords in context_keywords.items():
            if any(kw in text_lower for kw in keywords):
                matching_contexts.append(context)

        # Find domains that might match
        matching_domains = []
        for domain, config in self.domains.items():
            domain_lower = domain.lower()
            if any(word in text_lower for word in domain_lower.split()):
                matching_domains.append(domain)

        suggested_context = matching_contexts[0] if matching_contexts else None
        return suggested_context, matching_domains


# Singleton instance
_validator: Optional[DomainValidator] = None


def get_validator() -> DomainValidator:
    """Get or create singleton validator instance"""
    global _validator
    if _validator is None:
        _validator = DomainValidator()
    return _validator


def reload_config():
    """Reload configuration (useful for testing)"""
    global _validator
    _validator = None
    return get_validator()
