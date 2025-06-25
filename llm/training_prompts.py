"""
Training Prompts for x-pull-request-reviewer
Comprehensive prompts to train the LLM on official documentation of various technologies.
"""

# Official Documentation URLs for reference
OFFICIAL_DOCS = {
    "go": {
        "url": "https://golang.org/doc/",
        "source": "https://github.com/golang/go",
        "focus": ["concurrency", "performance", "idioms", "best_practices"]
    },
    "java": {
        "url": "https://docs.oracle.com/en/java/javase/",
        "openjdk": "https://openjdk.org/",
        "focus": ["object_oriented", "design_patterns", "performance", "security"]
    },
    "python": {
        "url": "https://docs.python.org/3/",
        "source": "https://github.com/python/cpython",
        "focus": ["pythonic_code", "performance", "readability", "best_practices"]
    },
    "helm": {
        "url": "https://helm.sh/docs/",
        "source": "https://github.com/helm/helm",
        "focus": ["templates", "values", "yaml_logic", "best_practices"]
    },
    "terraform": {
        "url": "https://developer.hashicorp.com/terraform/docs",
        "source": "https://github.com/hashicorp/terraform",
        "focus": ["syntax", "modules", "variables", "state_management"]
    },
    "terraform-aws": {
        "url": "https://developer.hashicorp.com/terraform/docs/providers/aws",
        "github": "https://github.com/hashicorp/terraform-provider-aws/tree/main/website/docs",
        "source": "https://github.com/hashicorp/terraform-provider-aws",
        "focus": ["aws_resources", "aws_best_practices", "aws_security", "aws_networking"]
    },
    "terraform-kubernetes": {
        "url": "https://developer.hashicorp.com/terraform/docs/providers/kubernetes",
        "github": "https://github.com/hashicorp/terraform-provider-kubernetes/tree/main/website/docs",
        "source": "https://github.com/hashicorp/terraform-provider-kubernetes",
        "focus": ["kubernetes_resources", "kubernetes_manifests", "kubernetes_best_practices"]
    },
    "terraform-google": {
        "url": "https://developer.hashicorp.com/terraform/docs/providers/google",
        "github": "https://github.com/hashicorp/terraform-provider-google/tree/main/website/docs",
        "source": "https://github.com/hashicorp/terraform-provider-google",
        "focus": ["gcp_resources", "gcp_best_practices", "gcp_security", "gcp_networking"]
    },
    "fluxcd": {
        "url": "https://fluxcd.io/flux/",
        "source": "https://github.com/fluxcd/flux2",
        "focus": ["gitops", "deployment_patterns", "yaml_configs"]
    },
    "argocd": {
        "url": "https://argo-cd.readthedocs.io/",
        "source": "https://github.com/argoproj/argo-cd",
        "focus": ["deployment_flows", "sync_strategies", "yaml_configs"]
    },
    "kubernetes": {
        "url": "https://kubernetes.io/docs/",
        "source": "https://github.com/kubernetes/kubernetes",
        "focus": ["manifests", "resource_management", "anti_patterns", "security"]
    },
    "istio": {
        "url": "https://istio.io/latest/docs/",
        "source": "https://github.com/istio/istio",
        "focus": ["service_mesh", "traffic_management", "security", "observability", "best_practices"]
    }
}


def get_documentation_ingestion_prompt(technology: str, doc_content: str) -> str:
    """
    Phase 1: Documentation Ingestion Prompts
    Use this to simulate ingestion of knowledge from official documentation.
    """
    return f"""
You are learning from the official documentation of {technology.upper()}.
Start by understanding the core concepts from this content.

DOC START:
{doc_content}
DOC END

Based on this official documentation, please:

1. **Summarize Key Points**: Extract the main concepts, features, and capabilities
2. **List Tools/APIs**: Identify any command-line tools, APIs, or interfaces mentioned
3. **Highlight Best Practices**: Note any recommended practices, patterns, or guidelines
4. **Identify Warnings**: Capture any warnings, limitations, or common pitfalls
5. **Extract Examples**: Note any code examples or configuration samples
6. **Security Considerations**: Identify any security-related information
7. **Performance Notes**: Capture any performance considerations or optimizations

Format your response as structured markdown with clear sections.
"""


def get_concept_mapping_prompt(technology: str) -> str:
    """
    Phase 2: Concept and Usage Mapping
    Based on the official documentation, explain core concepts and usage.
    """
    return f"""
Based on the official documentation of {technology.upper()}, provide a comprehensive understanding:

## 1. Problem Domain
What specific problems does {technology} solve? What are its primary use cases?

## 2. Core Architecture
What are the main components, modules, or architectural patterns?

## 3. Installation & Setup
What are the recommended installation and deployment steps?

## 4. CLI Commands & Examples
What are the essential command-line tools and their usage patterns?

## 5. Best Practices
What are the recommended practices for:
- Code organization
- Configuration management
- Security considerations
- Performance optimization
- Error handling

## 6. Common Issues & Troubleshooting
What are common misconfigurations, errors, and their solutions?

## 7. Integration Patterns
How does {technology} integrate with other tools in the ecosystem?

Provide specific examples and code snippets where applicable.
"""


def get_code_review_prompt(technology: str, code_content: str, language: str = None) -> str:
    """
    Phase 3: Code Review Understanding
    Review code using best practices from official documentation.
    """
    lang = language or technology
    return f"""
You are a senior {technology.upper()} expert trained on official documentation.
Review the following {lang.upper()} code using best practices from the official documentation.

CODE TO REVIEW:
{code_content}

Provide a comprehensive review covering:

## 🔍 **Analysis**
- What does this code do?
- What patterns or anti-patterns are present?

## ⚠️ **Issues Found**
- **Syntax/Structural Issues**: Any syntax errors, structural problems
- **Style/Linting Issues**: Code style, naming conventions, formatting
- **Security Issues**: Security vulnerabilities, unsafe practices
- **Performance Issues**: Inefficiencies, resource usage problems
- **Best Practice Violations**: Deviations from official recommendations

## 💡 **Suggestions**
- Specific improvements with code examples
- Alternative approaches or patterns
- Performance optimizations
- Security enhancements

## 📋 **Checklist**
- [ ] Follows {technology} best practices
- [ ] Proper error handling
- [ ] Security considerations addressed
- [ ] Performance optimized
- [ ] Well-documented/commented
- [ ] Maintainable and readable

## 🎯 **Priority**
- **Critical**: Must fix immediately
- **High**: Should fix soon
- **Medium**: Nice to have improvements
- **Low**: Minor suggestions

Provide actionable, specific feedback with code examples where possible.
"""


def get_infrastructure_review_prompt(technology: str, config_content: str) -> str:
    """
    Phase 4: Infrastructure as Code & YAML Templates Review
    Validate configuration against best practices from official documentation.
    """
    return f"""
You are a senior {technology.upper()} infrastructure expert trained on official documentation.
Validate the following {technology.upper()} configuration and compare against best practices.

CONFIGURATION TO REVIEW:
{config_content}

Provide a comprehensive infrastructure review:

## 🏗️ **Configuration Analysis**
- What does this configuration do?
- What resources/services does it create/manage?
- What are the dependencies and relationships?

## ✅ **Validation Results**
- **Syntax**: Is the configuration syntactically correct?
- **Structure**: Does it follow {technology} conventions?
- **Security**: Any security vulnerabilities or misconfigurations?
- **Performance**: Any performance or scalability concerns?
- **Best Practices**: Does it follow official recommendations?

## 🔧 **Improvements**
- Specific configuration improvements
- Security hardening suggestions
- Performance optimizations
- Better practices to adopt

## 🚨 **Risks & Warnings**
- Potential issues or risks
- Common pitfalls to avoid
- Production readiness concerns

## 📝 **Revised Configuration**
Provide an improved version of the configuration with:
- Security enhancements
- Performance optimizations
- Best practice implementations
- Better documentation/comments

## 🎯 **Priority Levels**
- **Critical**: Security vulnerabilities, production risks
- **High**: Performance issues, scalability concerns
- **Medium**: Best practice violations, maintainability
- **Low**: Style improvements, documentation

Be specific and provide actionable recommendations.
"""


def get_comprehension_test_prompt(technology: str, question: str) -> str:
    """
    Phase 5: Test Understanding with Questions
    Test comprehension after exposure to documentation.
    """
    return f"""
You are a {technology.upper()} expert who has been trained on official documentation.
Answer the following question based on your knowledge of {technology.upper()} best practices and official documentation:

**Question**: {question}

Provide a comprehensive answer that includes:

## 📚 **Official Documentation Reference**
- What does the official documentation say about this?
- Which specific sections or guides are relevant?

## 💡 **Practical Application**
- How would you apply this in real-world scenarios?
- What are the practical considerations?

## ⚠️ **Common Pitfalls**
- What are common mistakes or misconceptions?
- What should be avoided?

## 🔧 **Best Practices**
- What are the recommended approaches?
- What patterns or practices should be followed?

## 📋 **Examples**
- Provide concrete examples or code snippets
- Show both good and bad approaches

Base your answer on official documentation and real-world experience.
"""


def get_agent_goal_prompt() -> str:
    """
    Bonus: Agent Goal Prompt for Code Review
    For inference-based use (without training).
    """
    return """
You are a senior DevOps and cloud-native engineer trained on official documentation from:
- **Languages**: Go, Java, Python
- **Infrastructure**: Helm, Terraform, Kubernetes
- **GitOps**: FluxCD and ArgoCD

## 🎯 **Your Mission**
Perform thorough code and configuration reviews based on official documentation and best practices.

## 🔍 **Review Framework**
When given code or configuration, systematically analyze:

### 1. **Syntax & Structure**
- Language-specific syntax correctness
- Proper formatting and conventions
- Structural integrity and organization

### 2. **Security**
- Security vulnerabilities and anti-patterns
- Authentication and authorization issues
- Data protection and privacy concerns
- Infrastructure security best practices

### 3. **Performance**
- Efficiency and optimization opportunities
- Resource usage and scalability
- Bottlenecks and performance anti-patterns

### 4. **Best Practices**
- Official documentation compliance
- Industry-standard patterns and conventions
- Maintainability and readability
- Error handling and resilience

### 5. **DevOps & Cloud-Native**
- Infrastructure as Code principles
- GitOps practices and patterns
- Container and orchestration best practices
- CI/CD pipeline considerations

## 📋 **Output Format**
Provide structured feedback with:

1. **Summary**: Brief overview of findings
2. **Critical Issues**: Must-fix problems
3. **High Priority**: Important improvements
4. **Medium Priority**: Good-to-have enhancements
5. **Low Priority**: Minor suggestions
6. **Code Examples**: Specific fixes and improvements
7. **Resources**: Links to relevant documentation

## 🎯 **Priority Levels**
- **Critical**: Security vulnerabilities, production risks, breaking changes
- **High**: Performance issues, scalability concerns, major best practice violations
- **Medium**: Code quality, maintainability, minor best practice issues
- **Low**: Style improvements, documentation, minor optimizations

Be precise, actionable, and reference official documentation when possible.
"""


def get_technology_specific_prompt(technology: str) -> str:
    """
    Get technology-specific review prompts based on the technology type.
    """
    tech_prompts = {
        "go": """
**Go-Specific Review Focus:**
- Concurrency patterns (goroutines, channels, sync primitives)
- Error handling and propagation
- Performance considerations (memory allocation, garbage collection)
- Go idioms and conventions
- Package organization and module management
- Testing practices and coverage
- Security considerations (input validation, crypto usage)
""",
        "java": """
**Java-Specific Review Focus:**
- Object-oriented design principles
- Exception handling and error management
- Performance optimization (JVM tuning, memory management)
- Security practices (authentication, authorization, input validation)
- Design patterns and architectural decisions
- Testing strategies (unit, integration, performance)
- Dependency management and build tools
""",
        "python": """
**Python-Specific Review Focus:**
- Pythonic code and idioms
- Performance considerations (list comprehensions, generators)
- Error handling and exception management
- Security practices (input validation, dependency management)
- Code organization and module structure
- Testing and documentation practices
- Type hints and static analysis
""",
        "terraform": """
**Terraform-Specific Review Focus:**
- State management and locking
- Module organization and reusability
- Variable validation and type constraints
- Security best practices (IAM, encryption, network security)
- Performance optimization (parallelism, resource dependencies)
- Error handling and rollback strategies
- Documentation and naming conventions
""",
        "kubernetes": """
**Kubernetes-Specific Review Focus:**
- Resource definitions and API versions
- Security contexts and RBAC
- Resource limits and requests
- Health checks and readiness probes
- Service discovery and networking
- Storage and persistence
- Monitoring and observability
""",
        "helm": """
**Helm-Specific Review Focus:**
- Template syntax and functions
- Values structure and validation
- Chart organization and dependencies
- Security considerations (RBAC, network policies)
- Upgrade strategies and rollbacks
- Testing and validation
- Documentation and maintainability
""",
        "fluxcd": """
**FluxCD-Specific Review Focus:**
- GitOps workflow configuration
- Source and Kustomization resources
- Image automation and policies
- Security and RBAC configuration
- Monitoring and alerting setup
- Multi-cluster management
- Troubleshooting and debugging
""",
        "argocd": """
**ArgoCD-Specific Review Focus:**
- Application definitions and sync policies
- RBAC and security configuration
- Multi-cluster and multi-tenant setup
- Application health and status monitoring
- Rollback and sync strategies
- Integration with CI/CD pipelines
- Resource management and quotas
"""
    }
    
    return tech_prompts.get(technology.lower(), "")


def create_training_dataset_entry(technology: str, doc_content: str, code_example: str = None) -> dict:
    """
    Create a training dataset entry for fine-tuning.
    Format: {"prompt": "...", "response": "..."}
    """
    prompt = get_documentation_ingestion_prompt(technology, doc_content)
    
    # This would be the ideal response based on the documentation
    response = f"""
Based on the {technology.upper()} official documentation:

## Key Points Summary
[Extracted key concepts and features]

## Tools and APIs
[List of command-line tools, APIs, and interfaces]

## Best Practices
[Recommended practices and patterns]

## Warnings and Limitations
[Common pitfalls and limitations]

## Security Considerations
[Security-related information and recommendations]

## Performance Notes
[Performance considerations and optimizations]
"""
    
    return {
        "prompt": prompt,
        "response": response,
        "technology": technology,
        "type": "documentation_ingestion"
    }


def get_multi_technology_review_prompt(technologies: list, content: str) -> str:
    """
    Review content that involves multiple technologies.
    """
    tech_list = ", ".join([tech.upper() for tech in technologies])
    
    return f"""
You are a senior DevOps engineer expert in multiple technologies: {tech_list}

Review the following content that involves {tech_list}:

CONTENT TO REVIEW:
{content}

Provide a comprehensive multi-technology review covering:

## 🔍 **Technology-Specific Analysis**
For each technology involved:
- {technology_specific_analysis(technologies)}

## 🔗 **Integration Points**
- How do these technologies work together?
- Are there any integration issues or conflicts?
- Best practices for multi-technology deployments

## 🏗️ **Architecture Review**
- Overall system architecture and design
- Scalability and performance considerations
- Security across all technology layers

## 📋 **Technology-Specific Recommendations**
Provide specific recommendations for each technology involved.

## 🎯 **Cross-Technology Best Practices**
- DevOps and GitOps practices
- CI/CD pipeline considerations
- Monitoring and observability
- Security and compliance

Be comprehensive and reference official documentation for each technology.
"""


def technology_specific_analysis(technologies: list) -> str:
    """Generate technology-specific analysis points."""
    analysis_points = []
    
    for tech in technologies:
        if tech.lower() == "go":
            analysis_points.append("- Go: Concurrency patterns, error handling, performance")
        elif tech.lower() == "java":
            analysis_points.append("- Java: OOP design, exception handling, JVM optimization")
        elif tech.lower() == "python":
            analysis_points.append("- Python: Pythonic code, performance, security")
        elif tech.lower() == "terraform":
            analysis_points.append("- Terraform: State management, modules, security")
        elif tech.lower() == "kubernetes":
            analysis_points.append("- Kubernetes: Resource definitions, security, networking")
        elif tech.lower() == "helm":
            analysis_points.append("- Helm: Templates, values, chart organization")
        elif tech.lower() == "fluxcd":
            analysis_points.append("- FluxCD: GitOps workflow, automation, policies")
        elif tech.lower() == "argocd":
            analysis_points.append("- ArgoCD: Application management, sync policies, RBAC")
    
    return "\n".join(analysis_points) 