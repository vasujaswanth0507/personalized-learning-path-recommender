import json
from sqlalchemy.orm import Session
from app.models import (
    Skill, SkillPrerequisite, LearningResource, Project, Assessment,
    AssessmentQuestion, Milestone
)

def seed_database(db: Session):
    print("Checking knowledge base seed status...")

    # =========================================================================
    # 1. SKILLS DATA
    # =========================================================================
    skills_data = [
        # --- Cloud & DevOps (10 skills) ---
        {"id": 1, "name": "Linux Fundamentals", "domain": "Cloud / DevOps", "category": "Operating Systems", "difficulty_level": "Beginner", "description": "Core command line navigation, file permissions, process management, shell scripting basics."},
        {"id": 2, "name": "Networking & DNS Protocols", "domain": "Cloud / DevOps", "category": "Networking", "difficulty_level": "Beginner", "description": "IP addressing, CIDR subnetting, TCP/UDP, DNS resolution, HTTP/S, firewalls, and routing fundamentals."},
        {"id": 3, "name": "Cloud Computing Fundamentals", "domain": "Cloud / DevOps", "category": "Cloud", "difficulty_level": "Beginner", "description": "IaaS, PaaS, SaaS concepts, multi-region availability, redundancy, and basic cloud pricing models."},
        {"id": 4, "name": "AWS Core Services", "domain": "Cloud / DevOps", "category": "Cloud", "difficulty_level": "Intermediate", "description": "Hands-on provisioning with EC2, S3, VPC subnets, RDS, Route53, and security groups."},
        {"id": 5, "name": "IAM & Cloud Security", "domain": "Cloud / DevOps", "category": "Security", "difficulty_level": "Intermediate", "description": "Principle of least privilege, IAM roles, policies, MFA, audit logs, and credential rotation."},
        {"id": 6, "name": "Containerization with Docker", "domain": "Cloud / DevOps", "category": "Containers", "difficulty_level": "Intermediate", "description": "Dockerfile optimization, multi-stage builds, container registries, volumes, and Docker Compose."},
        {"id": 7, "name": "Infrastructure as Code (Terraform)", "domain": "Cloud / DevOps", "category": "IaC", "difficulty_level": "Intermediate", "description": "Declarative cloud provisioning, state management, modules, drift detection, and automated plans."},
        {"id": 8, "name": "CI/CD Automation", "domain": "Cloud / DevOps", "category": "DevOps", "difficulty_level": "Intermediate", "description": "Automating test and build pipelines, GitHub Actions workflows, artifacts, and staging deployments."},
        {"id": 9, "name": "Kubernetes Cluster Orchestration", "domain": "Cloud / DevOps", "category": "Containers", "difficulty_level": "Advanced", "description": "Pods, Deployments, Services, Ingress controllers, Helm charts, rolling updates, and scaling."},
        {"id": 10, "name": "Observability & SRE", "domain": "Cloud / DevOps", "category": "Operations", "difficulty_level": "Advanced", "description": "Metrics with Prometheus, log aggregation with Grafana/Loki, SLOs, alerts, and tracing."},

        # --- Full-Stack Web Development (10 skills) ---
        {"id": 11, "name": "HTML5 & Modern CSS", "domain": "Full-Stack Web", "category": "Frontend", "difficulty_level": "Beginner", "description": "Semantic markup, Flexbox, CSS Grid layouts, responsive media queries, and web accessibility."},
        {"id": 12, "name": "Modern JavaScript (ES6+)", "domain": "Full-Stack Web", "category": "Frontend", "difficulty_level": "Beginner", "description": "Async/await, Promises, closures, array methods, DOM manipulation, and ES module bundling."},
        {"id": 13, "name": "Frontend Architecture with React", "domain": "Full-Stack Web", "category": "Frontend", "difficulty_level": "Intermediate", "description": "Functional components, custom hooks, state lifting, component lifecycle, and routing."},
        {"id": 14, "name": "State Management & Component Design", "domain": "Full-Stack Web", "category": "Frontend", "difficulty_level": "Intermediate", "description": "Context API, Zustand/Redux patterns, memoization, reusable UI component patterns."},
        {"id": 15, "name": "RESTful API Design & HTTP", "domain": "Full-Stack Web", "category": "Backend", "difficulty_level": "Beginner", "description": "HTTP status codes, REST conventions, request headers, query params, and JSON schemas."},
        {"id": 16, "name": "Backend APIs with Node & FastAPI", "domain": "Full-Stack Web", "category": "Backend", "difficulty_level": "Intermediate", "description": "Routing, middleware, request validation, async controllers, and error handling."},
        {"id": 17, "name": "Relational Databases & SQL", "domain": "Full-Stack Web", "category": "Database", "difficulty_level": "Intermediate", "description": "Table schemas, foreign keys, complex JOINs, indexing, migrations, and ORMs."},
        {"id": 18, "name": "Authentication & JWT Security", "domain": "Full-Stack Web", "category": "Security", "difficulty_level": "Intermediate", "description": "Password hashing (bcrypt), JWT access/refresh tokens, OAuth2 flows, and CORS configuration."},
        {"id": 19, "name": "End-to-End Testing & Quality", "domain": "Full-Stack Web", "category": "Testing", "difficulty_level": "Advanced", "description": "Unit testing, integration testing, mocking external APIs, and frontend component tests."},
        {"id": 20, "name": "Full-Stack Cloud Deployment", "domain": "Full-Stack Web", "category": "Deployment", "difficulty_level": "Advanced", "description": "Production builds, containerized web servers, reverse proxies (Nginx), SSL, and CDN caching."},

        # --- AI & Machine Learning (10 skills) ---
        {"id": 21, "name": "Python for Scientific Computing", "domain": "AI & Machine Learning", "category": "Programming", "difficulty_level": "Beginner", "description": "Python syntax, virtual environments, data structures, functional patterns, and package management."},
        {"id": 22, "name": "Linear Algebra & Probability for ML", "domain": "AI & Machine Learning", "category": "Math", "difficulty_level": "Beginner", "description": "Vectors, matrices, dot products, eigenvalues, probability distributions, Bayes rule, and gradient descent."},
        {"id": 23, "name": "Data Manipulation with Pandas & NumPy", "domain": "AI & Machine Learning", "category": "Data Science", "difficulty_level": "Beginner", "description": "Array slicing, broadcasting, DataFrame filtering, grouping, merging, and handling missing values."},
        {"id": 24, "name": "Exploratory Data Analysis & Viz", "domain": "AI & Machine Learning", "category": "Data Science", "difficulty_level": "Intermediate", "description": "Feature correlation, distributions, outlier detection, Matplotlib/Seaborn interactive plotting."},
        {"id": 25, "name": "Classical Machine Learning (Scikit-Learn)", "domain": "AI & Machine Learning", "category": "Machine Learning", "difficulty_level": "Intermediate", "description": "Regression, decision trees, random forests, clustering, cross-validation, and ROC-AUC metrics."},
        {"id": 26, "name": "Neural Networks & Deep Learning", "domain": "AI & Machine Learning", "category": "Deep Learning", "difficulty_level": "Intermediate", "description": "Perceptrons, backpropagation, activation functions, loss curves, regularization, and optimization."},
        {"id": 27, "name": "PyTorch Framework & GPU Workflows", "domain": "AI & Machine Learning", "category": "Deep Learning", "difficulty_level": "Intermediate", "description": "Tensors, autograd, custom nn.Modules, Dataset/DataLoader pipelines, and GPU training loops."},
        {"id": 28, "name": "NLP & Transformer Architectures", "domain": "AI & Machine Learning", "category": "NLP", "difficulty_level": "Advanced", "description": "Tokenization, self-attention mechanism, BERT/GPT architectures, and HuggingFace pipelines."},
        {"id": 29, "name": "Generative AI & RAG Systems", "domain": "AI & Machine Learning", "category": "GenAI", "difficulty_level": "Advanced", "description": "Prompt engineering, vector embeddings, semantic search, hybrid retrieval, and LLM orchestration."},
        {"id": 30, "name": "MLOps & Model Serving", "domain": "AI & Machine Learning", "category": "MLOps", "difficulty_level": "Advanced", "description": "Model registries, FastAPI inference services, containerized deployment, drift monitoring."},

        # --- Data Engineering (10 skills) ---
        {"id": 31, "name": "Python for Data Workflows", "domain": "Data Engineering", "category": "Programming", "difficulty_level": "Beginner", "description": "File I/O, JSON/CSV parsing, requests, generators, and data processing automation."},
        {"id": 32, "name": "Advanced SQL & Query Tuning", "domain": "Data Engineering", "category": "Database", "difficulty_level": "Beginner", "description": "Window functions, CTEs, execution plan analysis, index types, and query optimization."},
        {"id": 33, "name": "Data Modeling & Dimensional Schemas", "domain": "Data Engineering", "category": "Architecture", "difficulty_level": "Intermediate", "description": "Star and Snowflake schemas, fact and dimension tables, SCD (Slowly Changing Dimensions)."},
        {"id": 34, "name": "Linux Shell & Automation", "domain": "Data Engineering", "category": "Systems", "difficulty_level": "Beginner", "description": "Bash scripting, cron jobs, environment isolation, and batch file handling."},
        {"id": 35, "name": "Distributed Processing with PySpark", "domain": "Data Engineering", "category": "Big Data", "difficulty_level": "Intermediate", "description": "Spark RDDs, DataFrames, transformations, actions, partitions, shuffling, and cluster memory."},
        {"id": 36, "name": "Pipeline Orchestration with Airflow", "domain": "Data Engineering", "category": "Orchestration", "difficulty_level": "Intermediate", "description": "DAG authoring, operators, task dependencies, retries, backfilling, and XComs."},
        {"id": 37, "name": "Event Streaming with Apache Kafka", "domain": "Data Engineering", "category": "Streaming", "difficulty_level": "Advanced", "description": "Producers, consumers, topics, partitions, consumer groups, offsets, and stream buffering."},
        {"id": 38, "name": "Modern Lakehouse Architecture", "domain": "Data Engineering", "category": "Architecture", "difficulty_level": "Advanced", "description": "Parquet formats, Delta Lake / Apache Iceberg ACID tables, time travel, and partitioning."},
        {"id": 39, "name": "Data Quality & Contract Testing", "domain": "Data Engineering", "category": "Quality", "difficulty_level": "Intermediate", "description": "Great Expectations, schema validation, anomaly detection, and data lineage."},
        # --- UI/UX Design (10 skills) ---
        {"id": 41, "name": "User Research & Empathy Mapping", "domain": "UI/UX Design", "category": "UX Research", "difficulty_level": "Beginner", "description": "User interviews, surveys, empathy mapping, personas, and identifying user pain points."},
        {"id": 42, "name": "Information Architecture & Flows", "domain": "UI/UX Design", "category": "UX Design", "difficulty_level": "Beginner", "description": "Sitemaps, card sorting, content taxonomy, user task journeys, and navigation hierarchies."},
        {"id": 43, "name": "Wireframing & Structural Grids", "domain": "UI/UX Design", "category": "UI Design", "difficulty_level": "Beginner", "description": "Rapid low-fidelity sketches, content wireframes, layout grids, and responsive column structures."},
        {"id": 44, "name": "Figma Essentials & Auto-Layout", "domain": "UI/UX Design", "category": "Design Tools", "difficulty_level": "Beginner", "description": "Vector networks, frames, components, variants, nested auto-layout, and constraint systems."},
        {"id": 45, "name": "Typography & Color Theory for UI", "domain": "UI/UX Design", "category": "Visual Design", "difficulty_level": "Beginner", "description": "Type scales, vertical rhythm, WCAG contrast compliance, color palettes, and visual hierarchy."},
        {"id": 46, "name": "Design Systems & Component Libraries", "domain": "UI/UX Design", "category": "Design Systems", "difficulty_level": "Intermediate", "description": "Design tokens, atomic design methodology, reusable component libraries, and documentation."},
        {"id": 47, "name": "Interactive Prototyping & Micro-Interactions", "domain": "UI/UX Design", "category": "Prototyping", "difficulty_level": "Intermediate", "description": "Interactive component states, smart animate transitions, mobile gestures, and realistic flow simulation."},
        {"id": 48, "name": "Usability Testing & Heuristic Review", "domain": "UI/UX Design", "category": "Testing", "difficulty_level": "Intermediate", "description": "Moderated task testing, Nielsen Norman 10 heuristics, cognitive walkthroughs, and error analysis."},
        {"id": 49, "name": "Responsive Web & Mobile UI", "domain": "UI/UX Design", "category": "Visual Design", "difficulty_level": "Intermediate", "description": "Touch target sizing, fluid layouts, platform patterns (iOS HIG vs Material Design), and breakpoints."},
        {"id": 50, "name": "UX Case Study & Portfolio Design", "domain": "UI/UX Design", "category": "Career", "difficulty_level": "Advanced", "description": "Problem framing, research evidence, design iterations, user metrics, and business outcome presentation."}
    ]

    for s in skills_data:
        existing = db.query(Skill).filter(Skill.id == s["id"]).first()
        if not existing:
            db.add(Skill(**s))
    db.commit()

    # =========================================================================
    # 2. PREREQUISITES GRAPH
    # =========================================================================
    prereqs_data = [
        # Cloud/DevOps
        {"skill_id": 2, "prerequisite_skill_id": 1, "strength": "required"},  # Net -> Linux
        {"skill_id": 3, "prerequisite_skill_id": 2, "strength": "required"},  # Cloud Fund -> Net
        {"skill_id": 4, "prerequisite_skill_id": 3, "strength": "required"},  # AWS -> Cloud Fund
        {"skill_id": 5, "prerequisite_skill_id": 4, "strength": "required"},  # IAM -> AWS
        {"skill_id": 6, "prerequisite_skill_id": 1, "strength": "required"},  # Docker -> Linux
        {"skill_id": 7, "prerequisite_skill_id": 4, "strength": "required"},  # Terraform -> AWS
        {"skill_id": 8, "prerequisite_skill_id": 6, "strength": "required"},  # CI/CD -> Docker
        {"skill_id": 9, "prerequisite_skill_id": 6, "strength": "required"},  # K8s -> Docker
        {"skill_id": 9, "prerequisite_skill_id": 2, "strength": "recommended"}, # K8s -> Net
        {"skill_id": 10, "prerequisite_skill_id": 9, "strength": "required"}, # Observability -> K8s

        # Full-Stack Web
        {"skill_id": 12, "prerequisite_skill_id": 11, "strength": "required"}, # JS -> HTML/CSS
        {"skill_id": 13, "prerequisite_skill_id": 12, "strength": "required"}, # React -> JS
        {"skill_id": 14, "prerequisite_skill_id": 13, "strength": "required"}, # State Mgmt -> React
        {"skill_id": 15, "prerequisite_skill_id": 12, "strength": "required"}, # REST -> JS
        {"skill_id": 16, "prerequisite_skill_id": 15, "strength": "required"}, # Backend -> REST
        {"skill_id": 17, "prerequisite_skill_id": 16, "strength": "recommended"}, # SQL -> Backend
        {"skill_id": 18, "prerequisite_skill_id": 16, "strength": "required"}, # Auth -> Backend
        {"skill_id": 19, "prerequisite_skill_id": 13, "strength": "recommended"}, # Testing -> React
        {"skill_id": 20, "prerequisite_skill_id": 18, "strength": "required"}, # Deployment -> Auth

        # AI & ML
        {"skill_id": 23, "prerequisite_skill_id": 21, "strength": "required"}, # Pandas -> Python
        {"skill_id": 24, "prerequisite_skill_id": 23, "strength": "required"}, # EDA -> Pandas
        {"skill_id": 25, "prerequisite_skill_id": 23, "strength": "required"}, # Scikit -> Pandas
        {"skill_id": 25, "prerequisite_skill_id": 22, "strength": "required"}, # Scikit -> Math
        {"skill_id": 26, "prerequisite_skill_id": 25, "strength": "required"}, # Deep Learning -> Scikit
        {"skill_id": 27, "prerequisite_skill_id": 26, "strength": "required"}, # PyTorch -> DL
        {"skill_id": 28, "prerequisite_skill_id": 27, "strength": "required"}, # NLP -> PyTorch
        {"skill_id": 29, "prerequisite_skill_id": 28, "strength": "required"}, # GenAI/RAG -> NLP
        {"skill_id": 30, "prerequisite_skill_id": 29, "strength": "required"}, # MLOps -> GenAI

        # Data Engineering
        {"skill_id": 33, "prerequisite_skill_id": 32, "strength": "required"}, # Modeling -> SQL
        {"skill_id": 35, "prerequisite_skill_id": 31, "strength": "required"}, # Spark -> Python
        {"skill_id": 35, "prerequisite_skill_id": 32, "strength": "required"}, # Spark -> SQL
        {"skill_id": 36, "prerequisite_skill_id": 31, "strength": "required"}, # Airflow -> Python
        {"skill_id": 36, "prerequisite_skill_id": 34, "strength": "recommended"}, # Airflow -> Linux
        {"skill_id": 37, "prerequisite_skill_id": 35, "strength": "required"}, # Kafka -> Spark
        {"skill_id": 38, "prerequisite_skill_id": 33, "strength": "required"}, # Lakehouse -> Modeling
        {"skill_id": 40, "prerequisite_skill_id": 33, "strength": "required"},  # Cloud DW -> Modeling

        # UI/UX Design
        {"skill_id": 42, "prerequisite_skill_id": 41, "strength": "required"},  # Info Arch -> User Research
        {"skill_id": 43, "prerequisite_skill_id": 42, "strength": "required"},  # Wireframing -> Info Arch
        {"skill_id": 44, "prerequisite_skill_id": 43, "strength": "required"},  # Figma -> Wireframing
        {"skill_id": 45, "prerequisite_skill_id": 43, "strength": "required"},  # Typography -> Wireframing
        {"skill_id": 46, "prerequisite_skill_id": 44, "strength": "required"},  # Design Systems -> Figma
        {"skill_id": 46, "prerequisite_skill_id": 45, "strength": "recommended"}, # Design Systems -> Typography
        {"skill_id": 47, "prerequisite_skill_id": 44, "strength": "required"},  # Prototyping -> Figma
        {"skill_id": 48, "prerequisite_skill_id": 47, "strength": "required"},  # Usability Testing -> Prototyping
        {"skill_id": 49, "prerequisite_skill_id": 46, "strength": "required"},  # Responsive UI -> Design Systems
        {"skill_id": 50, "prerequisite_skill_id": 48, "strength": "required"},  # Portfolio -> Usability Testing
        {"skill_id": 50, "prerequisite_skill_id": 49, "strength": "recommended"} # Portfolio -> Responsive UI
    ]

    for p in prereqs_data:
        existing = db.query(SkillPrerequisite).filter(
            SkillPrerequisite.skill_id == p["skill_id"],
            SkillPrerequisite.prerequisite_skill_id == p["prerequisite_skill_id"]
        ).first()
        if not existing:
            db.add(SkillPrerequisite(**p))
    db.commit()

    # =========================================================================
    # 3. LEARNING RESOURCES
    # =========================================================================
    resources_data = [
        # Linux
        {"title": "Mastering the Linux Command Line", "topic": "Linux", "domain": "Cloud / DevOps", "difficulty": "Beginner", "prerequisites_summary": "None", "estimated_hours": 4.0, "resource_type": "Interactive Lab", "url": "https://linuxjourney.com/", "skill_id": 1, "description": "Hands-on terminal guide covering bash navigation, stream redirection, pipes, file permissions, and process management.", "key_takeaways": "Master grep, find, chmod, systemctl, and standard I/O."},
        {"title": "Bash Scripting for System Automation", "topic": "Linux", "domain": "Cloud / DevOps", "difficulty": "Beginner", "prerequisites_summary": "Basic terminal navigation", "estimated_hours": 3.5, "resource_type": "Tutorial", "url": "https://devhints.io/bash", "skill_id": 1, "description": "Learn to write robust bash scripts with variables, control flow, functions, and error traps for server tasks.", "key_takeaways": "Automate routine backups, system health checks, and log rotations."},

        # Networking
        {"title": "Computer Networking for Cloud Engineers", "topic": "Networking", "domain": "Cloud / DevOps", "difficulty": "Beginner", "prerequisites_summary": "Linux Fundamentals", "estimated_hours": 5.0, "resource_type": "Course", "url": "https://roadmap.sh/guides/networking-terms", "skill_id": 2, "description": "Complete breakdown of OSI layers, subnetting math, DNS propagation, TLS handshakes, and network troubleshooting tools like traceroute and netstat.", "key_takeaways": "Calculate CIDR blocks, diagnose DNS latency, and configure security firewalls."},

        # Cloud Fundamentals
        {"title": "Cloud Architecture Core Concepts", "topic": "Cloud", "domain": "Cloud / DevOps", "difficulty": "Beginner", "prerequisites_summary": "Networking & DNS Protocols", "estimated_hours": 4.0, "resource_type": "Tutorial", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "skill_id": 3, "description": "Understand shared responsibility models, high availability across multi-AZ regions, and cloud cost optimization principles.", "key_takeaways": "Distinguish public/private subnets, managed databases, and object storage storage classes."},

        # AWS Core Services
        {"title": "AWS Compute, Storage & VPC Deep Dive", "topic": "AWS", "domain": "Cloud / DevOps", "difficulty": "Intermediate", "prerequisites_summary": "Cloud Computing Fundamentals", "estimated_hours": 6.5, "resource_type": "Interactive Lab", "url": "https://aws.amazon.com/getting-started/hands-on/", "skill_id": 4, "description": "Build a secure VPC with Internet Gateways, NAT Gateways, auto-scaled EC2 instances, and private RDS PostgreSQL databases.", "key_takeaways": "Deploy production cloud infrastructure with resilient routing and security group rules."},

        # Docker
        {"title": "Docker from Scratch to Production", "topic": "Docker", "domain": "Cloud / DevOps", "difficulty": "Intermediate", "prerequisites_summary": "Linux Fundamentals", "estimated_hours": 5.0, "resource_type": "Interactive Lab", "url": "https://docs.docker.com/get-started/", "skill_id": 6, "description": "Containerize real web applications using multi-stage builds, Alpine base images, volume persistence, and Compose networks.", "key_takeaways": "Write minimal, secure Dockerfiles and orchestrate multi-container microservices."},

        # Terraform
        {"title": "Terraform Up & Running: Infrastructure as Code", "topic": "Terraform", "domain": "Cloud / DevOps", "difficulty": "Intermediate", "prerequisites_summary": "AWS Core Services", "estimated_hours": 6.0, "resource_type": "Course", "url": "https://developer.hashicorp.com/terraform/tutorials", "skill_id": 7, "description": "Write declarative HCL configuration to create VPCs, load balancers, and S3 buckets with remote state locking in DynamoDB.", "key_takeaways": "Master terraform plan/apply, parameterized modules, and drift remediation."},

        # CI/CD
        {"title": "Automated Pipelines with GitHub Actions", "topic": "CI/CD", "domain": "Cloud / DevOps", "difficulty": "Intermediate", "prerequisites_summary": "Docker", "estimated_hours": 4.5, "resource_type": "Tutorial", "url": "https://docs.github.com/en/actions", "skill_id": 8, "description": "Build automated continuous integration and delivery pipelines that run tests, scan container images, and publish to registries.", "key_takeaways": "Configure reusable GitHub workflows, secret handling, and deployment gates."},

        # Kubernetes
        {"title": "Kubernetes in Action: Deployments & Ingress", "topic": "Kubernetes", "domain": "Cloud / DevOps", "difficulty": "Advanced", "prerequisites_summary": "Docker & Networking", "estimated_hours": 8.0, "resource_type": "Course", "url": "https://kubernetes.io/docs/tutorials/", "skill_id": 9, "description": "Orchestrate resilient workloads with ReplicaSets, Horizontal Pod Autoscalers, ConfigMaps, Secrets, and NGINX Ingress rules.", "key_takeaways": "Execute zero-downtime rolling updates and manage production Helm releases."},

        # Observability
        {"title": "Prometheus & Grafana: Cloud Observability", "topic": "Observability", "domain": "Cloud / DevOps", "difficulty": "Advanced", "prerequisites_summary": "Kubernetes Orchestration", "estimated_hours": 5.0, "resource_type": "Interactive Lab", "url": "https://prometheus.io/docs/introduction/overview/", "skill_id": 10, "description": "Instrument backend services, scrape Prometheus metrics, configure alertmanager rules, and build Grafana executive dashboards.", "key_takeaways": "Define meaningful SLOs/SLIs, monitor latency percentiles (p95/p99), and track error budgets."},

        # Full-Stack Web Resources
        {"title": "Modern JavaScript Deep Dive (ES2024)", "topic": "JavaScript", "domain": "Full-Stack Web", "difficulty": "Beginner", "prerequisites_summary": "HTML & CSS", "estimated_hours": 5.5, "resource_type": "Course", "url": "https://javascript.info/", "skill_id": 12, "description": "Thorough coverage of event loop, async/await, closures, prototypical inheritance, and functional array techniques.", "key_takeaways": "Write modular, idiomatic asynchronous JavaScript code."},
        {"title": "Building Dynamic Frontends with React", "topic": "React", "domain": "Full-Stack Web", "difficulty": "Intermediate", "prerequisites_summary": "Modern JavaScript", "estimated_hours": 7.0, "resource_type": "Interactive Lab", "url": "https://react.dev/learn", "skill_id": 13, "description": "Master component thinking, useState, useEffect, custom hooks, and performant state updates without unnecessary re-renders.", "key_takeaways": "Build responsive single-page applications with clean component boundaries."},
        {"title": "High-Performance REST APIs with FastAPI", "topic": "Backend APIs", "domain": "Full-Stack Web", "difficulty": "Intermediate", "prerequisites_summary": "RESTful API Design", "estimated_hours": 6.0, "resource_type": "Course", "url": "https://fastapi.tiangolo.com/tutorial/", "skill_id": 16, "description": "Create async API endpoints with automatic Swagger documentation, Pydantic validation, dependency injection, and JWT auth.", "key_takeaways": "Implement secure authentication, pagination, and relational database queries."},
        {"title": "PostgreSQL & SQLAlchemy Schema Design", "topic": "Databases", "domain": "Full-Stack Web", "difficulty": "Intermediate", "prerequisites_summary": "Backend APIs", "estimated_hours": 5.0, "resource_type": "Tutorial", "url": "https://www.postgresql.org/docs/", "skill_id": 17, "description": "Design normalized relational schemas, write optimal indexing strategies, manage database migrations, and prevent N+1 query traps.", "key_takeaways": "Optimize relational performance and ensure referential integrity."},

        # AI & ML Resources
        {"title": "Applied Data Analysis with Pandas & NumPy", "topic": "Data Science", "domain": "AI & Machine Learning", "difficulty": "Beginner", "prerequisites_summary": "Python basics", "estimated_hours": 5.0, "resource_type": "Interactive Lab", "url": "https://pandas.pydata.org/docs/getting_started/index.html", "skill_id": 23, "description": "Vectorized computations, grouping, aggregating time-series, reshaping matrices, and cleaning noisy datasets.", "key_takeaways": "Prepare raw messy datasets for machine learning feature pipelines."},
        {"title": "Machine Learning with Scikit-Learn", "topic": "Machine Learning", "domain": "AI & Machine Learning", "difficulty": "Intermediate", "prerequisites_summary": "Pandas & Linear Algebra", "estimated_hours": 7.5, "resource_type": "Course", "url": "https://scikit-learn.org/stable/tutorial/index.html", "skill_id": 25, "description": "Train, evaluate, and tune supervised models (Random Forests, Gradient Boosting) and unsupervised clustering models.", "key_takeaways": "Perform cross-validation, hyperparameter tuning, and interpret model feature importances."},
        {"title": "PyTorch Neural Networks & GPU Acceleration", "topic": "Deep Learning", "domain": "AI & Machine Learning", "difficulty": "Intermediate", "prerequisites_summary": "Classical Machine Learning", "estimated_hours": 8.0, "resource_type": "Course", "url": "https://pytorch.org/tutorials/", "skill_id": 27, "description": "Construct custom neural network architectures, write custom training loops with autograd, and optimize GPU tensor operations.", "key_takeaways": "Train deep convolutional and recurrent models while tracking training/validation loss."},
        {"title": "Production RAG & Vector Search Architectures", "topic": "Generative AI", "domain": "AI & Machine Learning", "difficulty": "Advanced", "prerequisites_summary": "PyTorch & Transformers", "estimated_hours": 6.5, "resource_type": "Interactive Lab", "url": "https://docs.langchain.com/", "skill_id": 29, "description": "Build end-to-end Retrieval Augmented Generation pipelines with vector embeddings, semantic chunking, and LLM synthesis.", "key_takeaways": "Eliminate hallucinations and provide grounded document question-answering systems."},

        # Data Engineering Resources
        {"title": "Advanced SQL for Analytics Engineers", "topic": "SQL", "domain": "Data Engineering", "difficulty": "Beginner", "prerequisites_summary": "Basic SQL SELECT", "estimated_hours": 5.0, "resource_type": "Interactive Lab", "url": "https://mode.com/sql-tutorial/", "skill_id": 32, "description": "Window functions (ROW_NUMBER, LAG/LEAD), recursive CTEs, query plan profiling, and analytical aggregate functions.", "key_takeaways": "Solve complex analytical queries and optimize slow reporting queries."},
        {"title": "Large-Scale Data Processing with PySpark", "topic": "Big Data", "domain": "Data Engineering", "difficulty": "Intermediate", "prerequisites_summary": "Python & SQL", "estimated_hours": 7.0, "resource_type": "Course", "url": "https://spark.apache.org/docs/latest/api/python/", "skill_id": 35, "description": "Architect distributed batch processing pipelines on multi-gigabyte datasets with Catalyst optimizer and resilient DataFrames.", "key_takeaways": "Perform distributed joins, partitioning, and Parquet data transformations without memory spills."},
        # UI/UX Design Resources
        {"title": "User Research & Empathy Mapping Masterclass", "topic": "UX Research", "domain": "UI/UX Design", "difficulty": "Beginner", "prerequisites_summary": "None", "estimated_hours": 4.5, "resource_type": "Interactive Lab", "url": "https://www.nngroup.com/articles/empathy-mapping/", "skill_id": 41, "description": "Learn to conduct structured user interviews, synthesize empathy maps, and extract actionable user problem statements.", "key_takeaways": "Formulate user personas, identify pain points, and define problem statements."},
        {"title": "Wireframing & Layout Grids from Scratch", "topic": "UI Design", "domain": "UI/UX Design", "difficulty": "Beginner", "prerequisites_summary": "User Research", "estimated_hours": 5.0, "resource_type": "Tutorial", "url": "https://balsamiq.com/learn/articles/what-are-wireframes/", "skill_id": 43, "description": "Master low-fidelity sketching, responsive 8pt layout grid systems, and structural hierarchy before visual styling.", "key_takeaways": "Create wireframe user flows and responsive column grids for mobile and web."},
        {"title": "Figma Masterclass: Auto-Layout & Design Tokens", "topic": "Design Tools", "domain": "UI/UX Design", "difficulty": "Beginner", "prerequisites_summary": "Wireframing basics", "estimated_hours": 6.5, "resource_type": "Interactive Lab", "url": "https://help.figma.com/hc/en-us/articles/360040451373", "skill_id": 44, "description": "Deep dive into Figma frames, vector tools, component variants, nested auto-layout, and color/typography variables.", "key_takeaways": "Build responsive UI layouts in Figma that mirror real flexbox CSS."},
        {"title": "Scalable Design Systems & Component Libraries", "topic": "Design Systems", "domain": "UI/UX Design", "difficulty": "Intermediate", "prerequisites_summary": "Figma Essentials", "estimated_hours": 7.0, "resource_type": "Course", "url": "https://uxdesign.cc/design-systems/home", "skill_id": 46, "description": "Architect atomic design systems with tokens, button hierarchies, form elements, accessible color contrasts, and documentation.", "key_takeaways": "Maintain consistent design languages and hand off tokens to frontend engineering."},
        {"title": "Usability Testing & Heuristic Evaluation", "topic": "Usability", "domain": "UI/UX Design", "difficulty": "Intermediate", "prerequisites_summary": "Interactive Prototyping", "estimated_hours": 5.5, "resource_type": "Tutorial", "url": "https://www.nngroup.com/articles/ten-usability-heuristics/", "skill_id": 48, "description": "Evaluate digital products using Jakob Nielsen's 10 usability heuristics and run remote moderated task tests.", "key_takeaways": "Identify usability friction, calculate task success rates, and iterate design."}
    ]

    for r in resources_data:
        existing = db.query(LearningResource).filter(LearningResource.title == r["title"]).first()
        if not existing:
            resource = LearningResource(**r)
            db.add(resource)
    db.commit()

    # =========================================================================
    # 4. PRACTICAL PROJECTS
    # =========================================================================
    projects_data = [
        {
            "title": "Deploy a Containerized Web Application with CI/CD",
            "domain": "Cloud / DevOps",
            "topic": "Docker & CI/CD",
            "difficulty": "Intermediate",
            "required_skills": "Linux, Docker, CI/CD Automation",
            "prerequisites": "Linux Fundamentals, Docker basics",
            "estimated_hours": 6.0,
            "objective": "Build a Docker container for a full-stack web service and configure a GitHub Actions workflow that automatically builds, tests, and publishes the container image on every pull request.",
            "suggested_steps": json.dumps([
                "Step 1: Write an optimized multi-stage Dockerfile with non-root user execution.",
                "Step 2: Create a docker-compose.yml file to spin up both application and database services locally.",
                "Step 3: Write automated health check scripts in bash.",
                "Step 4: Create a GitHub Actions workflow (.github/workflows/deploy.yml) that runs linting, unit tests, and builds the container image.",
                "Step 5: Test the CI pipeline with a test branch and verify that all stages pass successfully."
            ]),
            "expected_outcome": "A fully working repository with reproducible Docker Compose setup and passing automated CI pipeline.",
            "related_skill_id": 8
        },
        {
            "title": "Provision a Resilient Multi-Tier AWS Infrastructure with Terraform",
            "domain": "Cloud / DevOps",
            "topic": "Terraform & AWS",
            "difficulty": "Advanced",
            "required_skills": "AWS Core Services, Terraform, IAM",
            "prerequisites": "AWS Core Services, IAM & Cloud Security",
            "estimated_hours": 8.0,
            "objective": "Create declarative Infrastructure-as-Code modules in Terraform to deploy a VPC across 2 Availability Zones, an Application Load Balancer, an Auto-Scaling Group, and a managed PostgreSQL RDS instance.",
            "suggested_steps": json.dumps([
                "Step 1: Set up Terraform remote backend with S3 and DynamoDB state locking.",
                "Step 2: Write reusable modules for vpc, compute, and database.",
                "Step 3: Define security group rules restricting database access solely to application instances.",
                "Step 4: Execute terraform plan and inspect resource changes before applying.",
                "Step 5: Verify ALB health check endpoint and test zero-downtime rolling update."
            ]),
            "expected_outcome": "Complete Terraform module code that spins up and tears down an entire enterprise cloud architecture on demand.",
            "related_skill_id": 7
        },
        {
            "title": "Build a Full-Stack Collaborative Task Board with Auth & REST API",
            "domain": "Full-Stack Web",
            "topic": "React & FastAPI",
            "difficulty": "Intermediate",
            "required_skills": "React, FastAPI, SQL, JWT Auth",
            "prerequisites": "Frontend React, Backend APIs, Relational DBs",
            "estimated_hours": 7.0,
            "objective": "Develop an interactive Kanban task board where authenticated users can create columns, drag-and-drop tasks, assign priorities, and persist state in a relational database.",
            "suggested_steps": json.dumps([
                "Step 1: Design database schema for users, boards, columns, and task cards.",
                "Step 2: Implement FastAPI endpoints with JWT access token protection.",
                "Step 3: Build React frontend with component-driven state and optimistic UI updates.",
                "Step 4: Add form validation with instant client-side feedback.",
                "Step 5: Write unit tests for API route authentication and task creation."
            ]),
            "expected_outcome": "A responsive single-page application with full user registration, login, and real-time task board management.",
            "related_skill_id": 16
        },
        {
            "title": "Build a Document-Grounded RAG Assistant with Vector Search",
            "domain": "AI & Machine Learning",
            "topic": "GenAI & RAG",
            "difficulty": "Advanced",
            "required_skills": "Python, Pandas, Transformers, Vector Search",
            "prerequisites": "Data Manipulation, PyTorch & NLP",
            "estimated_hours": 8.0,
            "objective": "Implement an intelligent knowledge retrieval assistant that ingests technical PDF documents, converts text chunks into high-dimensional vector embeddings, and answers user questions with exact citations.",
            "suggested_steps": json.dumps([
                "Step 1: Extract and clean text from technical documentation files.",
                "Step 2: Chunk documents into semantic overlapping segments of 500 tokens.",
                "Step 3: Generate vector embeddings using a modern open embedding model.",
                "Step 4: Implement cosine similarity search to retrieve top-k relevant chunks.",
                "Step 5: Construct grounded prompts instructing the LLM to cite document references."
            ]),
            "expected_outcome": "A functional QA tool that provides accurate answers grounded in provided documents without hallucinations.",
            "related_skill_id": 29
        },
        {
            "title": "Build an Automated Batch & Streaming ETL Pipeline with Airflow",
            "domain": "Data Engineering",
            "topic": "Airflow & Spark",
            "difficulty": "Advanced",
            "required_skills": "Python, SQL, Apache Airflow, PySpark",
            "prerequisites": "Advanced SQL, Airflow Orchestration",
            "estimated_hours": 8.0,
            "objective": "Build a production-grade data pipeline that ingests daily e-commerce transactional data, performs schema validation with data quality checks, transforms metrics with PySpark, and loads into an analytical warehouse.",
            "suggested_steps": json.dumps([
                "Step 1: Set up Apache Airflow environment with SQLite/Postgres backend.",
                "Step 2: Author a DAG with tasks for extraction, staging, validation, and loading.",
                "Step 3: Implement PySpark transformation aggregating revenue by category and region.",
                "Step 4: Add Great Expectations or schema assertion checks to catch bad rows.",
                "Step 5: Verify idempotency by running the pipeline backfill across 7 historical days."
            ]),
            "expected_outcome": "An idempotent, monitored Airflow DAG that produces clean dimensional data tables ready for business analytics.",
            "related_skill_id": 36
        },
        {
            "title": "Design a High-Fidelity Mobile Banking & Savings App in Figma",
            "domain": "UI/UX Design",
            "topic": "Figma & UI/UX",
            "difficulty": "Intermediate",
            "required_skills": "Figma Essentials, Wireframing, Design Systems, Prototyping",
            "prerequisites": "Wireframing & Structural Grids, Figma Essentials",
            "estimated_hours": 7.5,
            "objective": "Conduct rapid user research, build wireframe journeys for sending money and tracking expenses, create a comprehensive Figma design system, and produce an interactive animated mobile prototype.",
            "suggested_steps": json.dumps([
                "Step 1: Define user personas and key user journeys for quick money transfers.",
                "Step 2: Create low-fidelity wireframes mapping screen-to-screen transaction flows.",
                "Step 3: Establish a 4-level design token palette (colors, typography, spacing, corner radius).",
                "Step 4: Design high-fidelity UI components using nested Figma auto-layout and interactive variants.",
                "Step 5: Connect prototype micro-interactions with Smart Animate and test with 3 users."
            ]),
            "expected_outcome": "A shareable Figma interactive prototype link along with a documented design system style guide.",
            "related_skill_id": 47
        }
    ]

    for p in projects_data:
        existing = db.query(Project).filter(Project.title == p["title"]).first()
        if not existing:
            project = Project(**p)
            db.add(project)
    db.commit()

    # =========================================================================
    # 5. ASSESSMENTS & QUESTIONS
    # =========================================================================
    assessments_data = [
        {
            "title": "Linux Systems & CLI Proficiency Assessment",
            "topic": "Linux Fundamentals",
            "domain": "Cloud / DevOps",
            "skill_id": 1,
            "passing_percentage": 70,
            "description": "Evaluates foundational understanding of Linux command line operations, permissions, and process inspection.",
            "questions": [
                {
                    "question_text": "Which command and argument combination recursively changes file permissions so that only the owner has read, write, and execute permissions?",
                    "options": json.dumps(["chmod -R 700 /target/dir", "chown -R 777 /target/dir", "chmod 755 /target/dir", "chgrp -R 600 /target/dir"]),
                    "correct_option_index": 0,
                    "explanation": "chmod 700 grants rwx (4+2+1=7) to owner, and 0 to group and others. The -R flag applies it recursively."
                },
                {
                    "question_text": "What does the exit status '$?' return in bash when a command completes successfully without errors?",
                    "options": json.dumps(["1", "0", "-1", "255"]),
                    "correct_option_index": 1,
                    "explanation": "In Unix/Linux POSIX standards, an exit code of 0 indicates success, while any non-zero value indicates an error or abnormal termination."
                },
                {
                    "question_text": "Which command allows you to view currently active network connections, listening ports, and associated process IDs on Linux?",
                    "options": json.dumps(["ls -la", "ps aux", "ss -tulpn", "df -h"]),
                    "correct_option_index": 2,
                    "explanation": "'ss -tulpn' shows TCP (t), UDP (u), listening (l), process (p), and numeric (n) network socket information."
                }
            ]
        },
        {
            "title": "Cloud Networking & Protocol Fundamentals",
            "topic": "Networking & DNS Protocols",
            "domain": "Cloud / DevOps",
            "skill_id": 2,
            "passing_percentage": 70,
            "description": "Tests understanding of CIDR subnetting, DNS resolution flow, and transport layer protocols.",
            "questions": [
                {
                    "question_text": "How many usable host IP addresses are available in a standard IPv4 /24 CIDR subnet?",
                    "options": json.dumps(["256", "254", "512", "128"]),
                    "correct_option_index": 1,
                    "explanation": "A /24 subnet has 2^(32-24) = 256 total addresses. The network address (.0) and broadcast address (.255) are reserved, leaving 254 usable host addresses."
                },
                {
                    "question_text": "Which DNS record type is specifically used to map a domain hostname directly to an IPv4 address?",
                    "options": json.dumps(["CNAME record", "MX record", "A record", "TXT record"]),
                    "correct_option_index": 2,
                    "explanation": "An 'A' record maps a domain name directly to an IPv4 address. 'AAAA' is used for IPv6, and CNAME is an alias to another domain."
                },
                {
                    "question_text": "What is the primary difference between TCP and UDP at the transport layer?",
                    "options": json.dumps([
                        "TCP is connection-oriented and guarantees ordered delivery via handshakes, while UDP is connectionless and faster without delivery guarantees.",
                        "UDP encrypts packets by default while TCP sends plaintext.",
                        "TCP operates only over local area networks while UDP operates across the internet.",
                        "TCP uses IP addresses while UDP uses MAC addresses."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "TCP establishes a 3-way handshake and handles packet retransmission and sequencing. UDP transmits datagrams with minimal overhead for latency-critical streams."
                }
            ]
        },
        {
            "title": "Docker Containers & Microservices Assessment",
            "topic": "Containerization with Docker",
            "domain": "Cloud / DevOps",
            "skill_id": 6,
            "passing_percentage": 70,
            "description": "Evaluates knowledge of Docker image layers, multi-stage builds, and volume mounts.",
            "questions": [
                {
                    "question_text": "Why is multi-stage building recommended in production Dockerfiles?",
                    "options": json.dumps([
                        "To compile binaries in a build container and copy only the final artifact into a minimal runtime image, reducing image size and attack surface.",
                        "To run multiple containers simultaneously inside one Docker process.",
                        "To bypass Linux kernel namespace isolation.",
                        "To automatically push images to Docker Hub on every build."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "Multi-stage builds leave behind bulky compilers, package caches, and dev tools, resulting in lean, secure production container images."
                },
                {
                    "question_text": "What happens to data written inside a Docker container if no volume or bind mount was configured and the container is deleted?",
                    "options": json.dumps([
                        "The data persists in the host's /tmp folder.",
                        "The data is permanently lost because the container's writable layer is destroyed.",
                        "The data is automatically synced to the cloud.",
                        "The data is restored when a new container is launched from the same image."
                    ]),
                    "correct_option_index": 1,
                    "explanation": "Container file systems are ephemeral by default; changes written to the container's writable layer are destroyed when the container instance is removed."
                },
                {
                    "question_text": "Which Docker instruction should be used to specify the default executable that should always run when a container starts?",
                    "options": json.dumps(["RUN", "COPY", "ENTRYPOINT", "LABEL"]),
                    "correct_option_index": 2,
                    "explanation": "ENTRYPOINT sets the default command that will execute when the container starts, with CMD providing default arguments that can be overridden."
                }
            ]
        },
        {
            "title": "Modern JavaScript & React Core Concepts",
            "topic": "Modern JavaScript & React",
            "domain": "Full-Stack Web",
            "skill_id": 13,
            "passing_percentage": 70,
            "description": "Tests understanding of React state hooks, immutability, and component rendering cycles.",
            "questions": [
                {
                    "question_text": "Why should you never mutate React state directly (e.g. state.push(item)) instead of using the setter function?",
                    "options": json.dumps([
                        "Direct mutation breaks React's shallow equality check, causing React to miss state changes and fail to re-render the component.",
                        "Direct mutation causes a browser memory leak immediately.",
                        "Direct mutation converts strings to numbers unexpectedly.",
                        "Direct mutation triggers an infinite loop immediately."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "React relies on object identity changes (immutable updates) to trigger reconciliation and re-render the DOM."
                },
                {
                    "question_text": "What does passing an empty dependency array '[]' to useEffect accomplish in a React component?",
                    "options": json.dumps([
                        "It makes the effect run on every single state change.",
                        "It runs the effect exactly once after the initial component mount.",
                        "It prevents the component from rendering at all.",
                        "It cancels all pending HTTP requests automatically."
                    ]),
                    "correct_option_index": 1,
                    "explanation": "An empty dependency array indicates the effect has no reactive dependencies, so it only executes once after the first paint."
                },
                {
                    "question_text": "Which JavaScript feature allows handling asynchronous operations cleanly without callback hell?",
                    "options": json.dumps(["async / await syntax with Promises", "eval() statements", "Synchronous while loops", "setTimeout() nesting"]),
                    "correct_option_index": 0,
                    "explanation": "async/await provides clean sequential syntax on top of ECMAScript Promises, allowing linear-style code and try/catch error handling."
                }
            ]
        },
        {
            "title": "Data Manipulation & ML Foundations Assessment",
            "topic": "Pandas & Machine Learning",
            "domain": "AI & Machine Learning",
            "skill_id": 25,
            "passing_percentage": 70,
            "description": "Tests machine learning evaluation, overfitting prevention, and feature preprocessing.",
            "questions": [
                {
                    "question_text": "What is the primary indicator of an overfitted machine learning model?",
                    "options": json.dumps([
                        "Extremely low training error but significantly higher error on unseen test/validation data.",
                        "High training error and high test error.",
                        "Slow inference speed on GPU.",
                        "A confusion matrix with all zeros."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "Overfitting occurs when a model memorizes noise and specific patterns in the training data rather than generalizing, resulting in high test loss."
                },
                {
                    "question_text": "Why should feature scaling (e.g. StandardScaler) be fit strictly on the training set rather than the combined dataset?",
                    "options": json.dumps([
                        "To prevent data leakage from the test set into the model training phase.",
                        "Because test sets cannot contain numerical columns.",
                        "To speed up GPU compilation.",
                        "To convert all numbers to integers."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "Fitting scalers or encoders on test data leaks statistical distribution parameters (mean, variance) from the future evaluation data into training."
                },
                {
                    "question_text": "Which metric is most appropriate for evaluating a binary classification model when the classes are heavily imbalanced (e.g., 99% negative, 1% fraud)?",
                    "options": json.dumps(["Overall Accuracy", "Precision-Recall AUC / F1-Score", "Mean Squared Error", "R-squared"]),
                    "correct_option_index": 1,
                    "explanation": "In extreme class imbalance, a naive model predicting all negatives achieves 99% accuracy but catches zero fraud. F1-score and PR-AUC measure true positive detection and false alarm trade-offs."
                }
            ]
        },
        {
            "title": "UI/UX Design & Heuristic Evaluation Assessment",
            "topic": "Usability Testing & Design Principles",
            "domain": "UI/UX Design",
            "skill_id": 48,
            "passing_percentage": 70,
            "description": "Tests understanding of usability heuristics, layout hierarchy, and Figma auto-layout mechanics.",
            "questions": [
                {
                    "question_text": "According to Jakob Nielsen's usability heuristics, what is the core purpose of 'Visibility of System Status'?",
                    "options": json.dumps([
                        "To keep users informed about what is going on through appropriate feedback within reasonable time.",
                        "To show system server CPU usage to all end users.",
                        "To make sure all text is colored bright red when loading.",
                        "To hide loading spinners until an error occurs."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "Visibility of system status ensures users always know where they are in a flow and what action is currently executing."
                },
                {
                    "question_text": "In Figma, how does configuring an Auto-Layout frame with 'Fill Container' differ from 'Hug Contents'?",
                    "options": json.dumps([
                        "'Fill Container' expands the child layer to stretch to its parent's width, while 'Hug Contents' shrinks the frame to wrap tightly around its children.",
                        "'Fill Container' locks the pixel width permanently.",
                        "'Hug Contents' only works for vector shapes, not text.",
                        "'Fill Container' hides child elements that overflow."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "'Fill' adapts responsively to parent dimensions, whereas 'Hug' dynamically sizes to child elements."
                },
                {
                    "question_text": "Why do product designers produce low-fidelity wireframes before high-fidelity visual mockups?",
                    "options": json.dumps([
                        "To validate information architecture and user flow without getting distracted by visual polish, colors, and typography.",
                        "Because wireframes cannot be shown to clients.",
                        "To convert design files into HTML automatically.",
                        "Because high-fidelity tools cannot handle text."
                    ]),
                    "correct_option_index": 0,
                    "explanation": "Low-fidelity wireframing isolates structure and usability questions early when changes are quick and inexpensive."
                }
            ]
        }
    ]

    for a_data in assessments_data:
        questions_list = a_data.pop("questions")
        existing_assessment = db.query(Assessment).filter(Assessment.title == a_data["title"]).first()
        if not existing_assessment:
            assessment = Assessment(**a_data)
            db.add(assessment)
            db.commit()

            for q in questions_list:
                question = AssessmentQuestion(assessment_id=assessment.id, **q)
                db.add(question)
            db.commit()

    # =========================================================================
    # 6. DEFAULT MILESTONES
    # =========================================================================
    milestones_data = [
        {"title": "First Step Taken", "description": "Enrolled in your personalized learning path and reviewed your profile.", "badge_icon": "rocket", "requirement_type": "first_topic", "requirement_value": 1},
        {"title": "Prerequisite Master", "description": "Completed your first core prerequisite topic.", "badge_icon": "shield-check", "requirement_type": "skill_count", "requirement_value": 1},
        {"title": "Skill Builder", "description": "Mastered 3 foundational skills along your learning trajectory.", "badge_icon": "zap", "requirement_type": "skill_count", "requirement_value": 3},
        {"title": "Hands-On Maker", "description": "Completed your first practical real-world project.", "badge_icon": "code", "requirement_type": "first_project", "requirement_value": 1},
        {"title": "Assessment Ace", "description": "Passed a topic assessment with 70% or higher score.", "badge_icon": "check-circle", "requirement_type": "first_assessment", "requirement_value": 1},
        {"title": "Career Ready", "description": "Completed all milestones and stages in your personalized roadmap.", "badge_icon": "award", "requirement_type": "path_complete", "requirement_value": 1}
    ]

    for m in milestones_data:
        milestone = Milestone(**m)
        db.add(milestone)
    db.commit()

    print("Database seeding completed successfully.")
