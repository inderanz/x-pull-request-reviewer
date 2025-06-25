from .training_prompts import (
    get_agent_goal_prompt, 
    get_technology_specific_prompt,
    get_code_review_prompt,
    get_infrastructure_review_prompt,
    OFFICIAL_DOCS
)

def build_review_prompt(diff, static_summary, language):
    """
    Build a detailed prompt for the LLM to review code changes with actionable suggestions.
    Enhanced with technology-specific knowledge from official documentation.
    """
    # Get technology-specific focus areas
    tech_focus = get_technology_specific_prompt(language.lower())
    
    # Get the base agent goal prompt
    agent_prompt = get_agent_goal_prompt()
    
    prompt = f"""
{agent_prompt}

{tech_focus}

You are reviewing code changes in {language.upper()}. 

IMPORTANT: For each suggestion, provide specific actionable recommendations in this format:
- For file changes: "file:path/to/file.py:line_number: specific change description"
- For line-specific issues: "line X: specific issue description"
- For general suggestions: "suggestion: general recommendation"

Examples:
- "file:src/main.py:15: Add input validation for user_id parameter"
- "line 23: Consider using a more descriptive variable name"
- "suggestion: Add error handling for database connection failures"

---

CODE DIFF:
{diff}

---

STATIC ANALYSIS SUMMARY:
{static_summary}

---

Respond with a detailed review and a summary table of findings. Include specific file paths and line numbers for actionable changes.

Focus on:
1. **Security**: Vulnerabilities, unsafe practices, authentication issues
2. **Performance**: Inefficiencies, resource usage, optimization opportunities
3. **Best Practices**: Official documentation compliance, industry standards
4. **Maintainability**: Code organization, readability, documentation
5. **Error Handling**: Exception management, resilience patterns
"""

    return prompt


def build_actionable_suggestions_prompt(llm_response, diff, language):
    """
    Build a prompt to extract actionable suggestions from the LLM response.
    """
    prompt = f"""
Extract actionable code suggestions from the following {language} code review.
For each suggestion that requires a code change, provide:
1. File path (if applicable)
2. Line number (if applicable) 
3. Current code (if applicable)
4. Suggested new code
5. Reason for the change

Format each suggestion as:
SUGGESTION_ID: file:path/to/file.py:line_number
REASON: brief explanation
CURRENT: current code line
SUGGESTED: suggested new code line

If a suggestion doesn't apply to a specific line, mark it as:
SUGGESTION_ID: general
REASON: brief explanation
ACTION: what should be done

---

REVIEW RESPONSE:
{llm_response}

---

DIFF CONTEXT:
{diff}

---

Extract only the suggestions that require actual code changes (not just comments or general advice).
"""
    return prompt


def build_technology_specific_review_prompt(technology: str, content: str, content_type: str = "code") -> str:
    """
    Build a technology-specific review prompt based on the content type.
    
    Args:
        technology: The technology being reviewed (go, java, python, terraform, etc.)
        content: The content to review
        content_type: Type of content ("code", "config", "yaml", "hcl")
    """
    if content_type in ["config", "yaml", "hcl", "tf"]:
        return get_infrastructure_review_prompt(technology, content)
    else:
        return get_code_review_prompt(technology, content, technology)


def build_multi_technology_review_prompt(technologies: list, content: str) -> str:
    """
    Build a review prompt for content involving multiple technologies.
    """
    from .training_prompts import get_multi_technology_review_prompt
    return get_multi_technology_review_prompt(technologies, content)


def get_supported_technologies() -> list:
    """Get list of supported technologies for review."""
    return list(OFFICIAL_DOCS.keys())


def detect_technologies_in_content(content: str) -> list:
    """
    Detect which technologies are present in the content.
    """
    detected = []
    
    # Simple keyword-based detection
    tech_keywords = {
        "go": ["package main", "import", "func", "goroutine", "channel", "go func"],
        "java": ["public class", "import java", "public static void main", "extends", "implements"],
        "python": ["import", "def ", "class ", "if __name__", "print(", "return"],
        "terraform": ["terraform", "resource", "data", "variable", "output", "module"],
        "kubernetes": ["apiVersion:", "kind:", "metadata:", "spec:", "containers:"],
        "helm": ["apiVersion:", "kind: Chart", "values:", "templates:", "{{", "}}"],
        "fluxcd": ["apiVersion: source.toolkit.fluxcd.io", "apiVersion: kustomize.toolkit.fluxcd.io"],
        "argocd": ["apiVersion: argoproj.io/v1alpha1", "kind: Application", "spec:"]
    }
    
    content_lower = content.lower()
    
    for tech, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                if tech not in detected:
                    detected.append(tech)
                break
    
    return detected


def build_enhanced_review_prompt(diff: str, static_summary: str, language: str = None) -> str:
    """
    Build an enhanced review prompt that automatically detects technologies and applies appropriate review strategies.
    """
    # Detect technologies in the diff
    detected_techs = detect_technologies_in_content(diff)
    
    if len(detected_techs) > 1:
        # Multi-technology review
        return build_multi_technology_review_prompt(detected_techs, diff)
    elif len(detected_techs) == 1:
        # Single technology review
        tech = detected_techs[0]
        return build_technology_specific_review_prompt(tech, diff, "code")
    else:
        # Fallback to language-based review
        return build_review_prompt(diff, static_summary, language or "code") 