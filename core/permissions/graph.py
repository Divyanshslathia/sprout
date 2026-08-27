"""
Knowledge Graph using Neo4j

Permission relationships and capability management
"""
from typing import Dict, List, Optional, Tuple
from core.intent.types import RiskLevel

class KnowledgeGraph:
    """
    Neo4j-based knowledge graph for permissions

    Falls back to in-memory graph if Neo4j not available
    """

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None, use_neo4j: bool = False):
        """
        Initialize knowledge graph

        Args:
            uri: Neo4j database URI
            user: Neo4j username
            password: Neo4j password
            use_neo4j: Whether to use Neo4j (False = use networkx fallback)
        """
        self.use_neo4j = use_neo4j
        self.driver = None
        self.graph = None

        if use_neo4j:
            self._init_neo4j(uri, user, password)
        else:
            self._init_networkx()

    def _init_neo4j(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection"""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password))

            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")

            print("✓ Connected to Neo4j")
            self._create_neo4j_schema()

        except ImportError:
            print("Warning: Neo4j driver not installed. Install with: pip install neo4j")
            print("Falling back to in-memory graph")
            self._init_networkx()
        except Exception as e:
            print(f"Warning: Neo4j connection failed: {str(e)}")
            print("Falling back to in-memory graph")
            self._init_networkx()

    def _init_networkx(self):
        """Initialize in-memory graph using networkx"""
        try:
            import networkx as nx
            self.graph = nx.DiGraph()
            self.use_neo4j = False
            print("✓ Using in-memory permission graph")
            self._create_default_permissions()
        except ImportError:
            print("Warning: networkx not installed. Install with: pip install networkx")
            self.graph = None

    def _create_neo4j_schema(self):
        """Create Neo4j schema and constraints"""
        if not self.driver:
            return

        with self.driver.session() as session:
            # Create constraints
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS
                FOR (a:Agent) REQUIRE a.name IS UNIQUE
            """)

            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS
                FOR (r:Resource) REQUIRE r.name IS UNIQUE
            """)

    def _create_default_permissions(self):
        """Create default permission rules in graph"""
        if not self.graph:
            return

        # Add Sprout agent node
        self.graph.add_node("Sprout", type="agent")

        # Allowed apps
        allowed_apps = ["firefox", "chrome", "terminal", "code", "nautilus"]
        for app in allowed_apps:
            self.graph.add_node(app, type="app")
            self.graph.add_edge("Sprout", app, relation="can_open", risk="SENSITIVE")

        # Allowed directories
        allowed_dirs = [
            "/home/divyansh/Documents",
            "/home/divyansh/Downloads",
            "/home/divyansh/projects"
        ]
        for dir_path in allowed_dirs:
            self.graph.add_node(dir_path, type="directory")
            self.graph.add_edge("Sprout", dir_path, relation="can_access", risk="SAFE")

        # Blocked directories
        blocked_dirs = ["/etc", "/sys", "/proc", "/root"]
        for dir_path in blocked_dirs:
            self.graph.add_node(dir_path, type="directory")
            self.graph.add_edge("Sprout", dir_path, relation="blocked", risk="DESTRUCTIVE")

    def check_permission(self, agent: str, action: str, target: str) -> Tuple[bool, Optional[str]]:
        """
        Check if agent has permission for action on target

        Args:
            agent: Agent name (e.g., "Sprout")
            action: Action type (e.g., "can_open", "can_access")
            target: Target resource

        Returns:
            Tuple of (allowed, reason)
        """
        if self.use_neo4j and self.driver:
            return self._check_permission_neo4j(agent, action, target)
        elif self.graph:
            return self._check_permission_networkx(agent, action, target)
        else:
            return False, "Permission system unavailable"

    def _check_permission_neo4j(self, agent: str, action: str, target: str) -> Tuple[bool, Optional[str]]:
        """Check permission using Neo4j"""
        with self.driver.session() as session:
            # Check if explicit permission exists
            result = session.run("""
                MATCH (a:Agent {name: $agent})-[r {relation: $action}]->(t:Resource {name: $target})
                RETURN r.risk as risk
            """, agent=agent, action=action, target=target)

            record = result.single()
            if record:
                risk = record["risk"]
                if risk == "BLOCKED":
                    return False, f"Action {action} on {target} is blocked"
                return True, None

            # Check for wildcard permissions
            result = session.run("""
                MATCH (a:Agent {name: $agent})-[r {relation: $action}]->(t:Resource)
                WHERE t.name STARTS WITH $prefix OR t.type = 'wildcard'
                RETURN r.risk as risk
                LIMIT 1
            """, agent=agent, action=action, prefix=target.split('/')[0])

            record = result.single()
            if record:
                return True, None

            return False, f"No permission for {action} on {target}"

    def _check_permission_networkx(self, agent: str, action: str, target: str) -> Tuple[bool, Optional[str]]:
        """Check permission using networkx graph"""
        if not self.graph or not self.graph.has_node(agent):
            return False, "Agent not found"

        # Check direct permission
        if self.graph.has_node(target):
            if self.graph.has_edge(agent, target):
                edge_data = self.graph.get_edge_data(agent, target)
                relation = edge_data.get("relation", "")

                if relation == "blocked":
                    return False, f"Access to {target} is blocked"

                if relation == action or relation.startswith("can_"):
                    return True, None

        # Check prefix match for directories
        if "/" in target:
            for node in self.graph.nodes():
                if target.startswith(str(node)) and self.graph.has_edge(agent, node):
                    edge_data = self.graph.get_edge_data(agent, node)
                    if edge_data.get("relation") == "blocked":
                        return False, f"Access blocked by rule: {node}"
                    if edge_data.get("relation") == action:
                        return True, None

        return False, f"No permission found for {action} on {target}"

    def add_permission(self, agent: str, action: str, target: str, risk: str = "SAFE"):
        """Add a permission rule"""
        if self.use_neo4j and self.driver:
            self._add_permission_neo4j(agent, action, target, risk)
        elif self.graph:
            self._add_permission_networkx(agent, action, target, risk)

    def _add_permission_neo4j(self, agent: str, action: str, target: str, risk: str):
        """Add permission to Neo4j"""
        with self.driver.session() as session:
            session.run("""
                MERGE (a:Agent {name: $agent})
                MERGE (t:Resource {name: $target})
                MERGE (a)-[r:HAS_PERMISSION {relation: $action, risk: $risk}]->(t)
            """, agent=agent, target=target, action=action, risk=risk)

    def _add_permission_networkx(self, agent: str, action: str, target: str, risk: str):
        """Add permission to networkx graph"""
        if not self.graph:
            return

        if not self.graph.has_node(agent):
            self.graph.add_node(agent, type="agent")

        if not self.graph.has_node(target):
            self.graph.add_node(target, type="resource")

        self.graph.add_edge(agent, target, relation=action, risk=risk)

    def remove_permission(self, agent: str, action: str, target: str):
        """Remove a permission rule"""
        if self.use_neo4j and self.driver:
            with self.driver.session() as session:
                session.run("""
                    MATCH (a:Agent {name: $agent})-[r {relation: $action}]->(t:Resource {name: $target})
                    DELETE r
                """, agent=agent, action=action, target=target)
        elif self.graph and self.graph.has_edge(agent, target):
            self.graph.remove_edge(agent, target)

    def get_all_permissions(self, agent: str) -> List[Dict]:
        """Get all permissions for an agent"""
        if self.use_neo4j and self.driver:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Agent {name: $agent})-[r]->(t:Resource)
                    RETURN t.name as target, r.relation as action, r.risk as risk
                """, agent=agent)

                return [dict(record) for record in result]
        elif self.graph and self.graph.has_node(agent):
            permissions = []
            for target in self.graph.successors(agent):
                edge_data = self.graph.get_edge_data(agent, target)
                permissions.append({
                    "target": target,
                    "action": edge_data.get("relation", "unknown"),
                    "risk": edge_data.get("risk", "SAFE")
                })
            return permissions

        return []

    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
