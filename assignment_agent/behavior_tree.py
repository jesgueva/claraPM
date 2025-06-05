"""
Behavior tree implementation for task assignment decisions.
"""

import py_trees
import json
import redis
from dotenv import load_dotenv
import os
from logger.config import agent_logger

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class TaskAssignmentBehaviorTree:
    def __init__(self):
        """Initialize the behavior tree for task assignment decisions"""
        self.blackboard = py_trees.blackboard.Blackboard()
        self.tree = self._create_tree()
        
    def _create_tree(self):
        """Create the behavior tree structure"""
        # Root sequence node - all children must succeed for the sequence to succeed
        root = py_trees.composites.Sequence("TaskAssignmentSequence", memory=True)
        
        # Check developer availability
        check_availability = self.CheckDeveloperAvailability("CheckAvailability")
        
        # Check skill match
        check_skills = self.CheckSkillMatch("CheckSkillMatch")
        
        # Check workload
        check_workload = self.CheckDeveloperWorkload("CheckWorkload")
        
        # Check task priority
        check_priority = self.CheckTaskPriority("CheckPriority")
        
        # Final decision selector - succeeds if any child succeeds
        decision = py_trees.composites.Selector("AssignmentDecision", memory=True)
        
        # Highly recommended assignment
        highly_recommended = self.HighlyRecommendedMatch("HighlyRecommended")
        
        # Good match
        good_match = self.GoodMatch("GoodMatch")
        
        # Consider other developers
        consider_others = self.ConsiderOtherDevelopers("ConsiderOthers")
        
        # Add children to decision selector
        decision.add_children([highly_recommended, good_match, consider_others])
        
        # Add all checks and decision to root sequence
        root.add_children([
            check_availability, 
            check_skills, 
            check_workload, 
            check_priority,
            decision
        ])
        
        return root
    
    # Behavior Tree Node Classes
    class CheckDeveloperAvailability(py_trees.behaviour.Behaviour):
        """Check if the developer is available for new tasks"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            developer_id = blackboard.get("developer_id")
            
            # Check developer availability in Redis
            availability_data = redis_client.get(f"developer:{developer_id}:availability")
            if not availability_data:
                blackboard.set("error", f"Developer with ID {developer_id} not found")
                return py_trees.common.Status.FAILURE
                
            availability = availability_data.decode('utf-8')
            blackboard.set("developer_availability", availability)
            
            if availability != "available":
                blackboard.set("recommendation", "Developer is not available")
                return py_trees.common.Status.FAILURE
                
            return py_trees.common.Status.SUCCESS
    
    class CheckSkillMatch(py_trees.behaviour.Behaviour):
        """Check how well the developer's skills match the task requirements"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            developer_id = blackboard.get("developer_id")
            task_id = blackboard.get("task_id")
            
            # Get developer skills from Redis
            skills_data = redis_client.get(f"developer:{developer_id}:skills")
            if not skills_data:
                blackboard.set("skill_match", 0.0)
                return py_trees.common.Status.SUCCESS  # Continue even without skills data
                
            developer_skills = json.loads(skills_data.decode('utf-8'))
            
            # Get task required skills from Redis
            task_data = redis_client.get(f"task:{task_id}")
            if not task_data:
                blackboard.set("error", f"Task with ID {task_id} not found")
                return py_trees.common.Status.FAILURE
                
            task = json.loads(task_data.decode('utf-8'))
            required_skills = task.get("required_skills", [])
            
            # Calculate skill match
            if not required_skills:
                blackboard.set("skill_match", 1.0)  # No skills required
            else:
                matching_skills = sum(1 for skill in required_skills if skill in developer_skills)
                skill_match = matching_skills / len(required_skills)
                blackboard.set("skill_match", skill_match)
            
            return py_trees.common.Status.SUCCESS
    
    class CheckDeveloperWorkload(py_trees.behaviour.Behaviour):
        """Check the developer's current workload"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            developer_id = blackboard.get("developer_id")
            
            # Get developer task count from Redis
            task_count_data = redis_client.get(f"developer:{developer_id}:task_count")
            task_count = int(task_count_data.decode('utf-8')) if task_count_data else 0
            
            # Get developer capacity from Redis
            capacity_data = redis_client.get(f"developer:{developer_id}:capacity")
            capacity = int(capacity_data.decode('utf-8')) if capacity_data else 5  # Default capacity
            
            # Calculate workload percentage
            workload = task_count / capacity if capacity > 0 else 1.0
            blackboard.set("workload", workload)
            
            return py_trees.common.Status.SUCCESS
    
    class CheckTaskPriority(py_trees.behaviour.Behaviour):
        """Check the priority of the task"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            task_id = blackboard.get("task_id")
            
            # Get task data from Redis
            task_data = redis_client.get(f"task:{task_id}")
            if not task_data:
                blackboard.set("error", f"Task with ID {task_id} not found")
                return py_trees.common.Status.FAILURE
                
            task = json.loads(task_data.decode('utf-8'))
            
            # Get priority (1-5 scale, 5 being highest)
            priority = task.get("priority", 3)  # Default to medium priority
            blackboard.set("priority", priority)
            
            return py_trees.common.Status.SUCCESS
    
    class HighlyRecommendedMatch(py_trees.behaviour.Behaviour):
        """Determine if this is a highly recommended match"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            skill_match = blackboard.get("skill_match")
            workload = blackboard.get("workload")
            priority = blackboard.get("priority")
            
            # Criteria for highly recommended match:
            # 1. Skill match > 0.8 (80% match)
            # 2. Workload < 0.7 (less than 70% capacity)
            # 3. Or high priority task (4-5) with skill match > 0.7
            if (skill_match > 0.8 and workload < 0.7) or (priority >= 4 and skill_match > 0.7):
                blackboard.set("recommendation", "Highly recommended match")
                blackboard.set("recommendation_score", 0.9)
                return py_trees.common.Status.SUCCESS
            
            return py_trees.common.Status.FAILURE
    
    class GoodMatch(py_trees.behaviour.Behaviour):
        """Determine if this is a good match"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            skill_match = blackboard.get("skill_match")
            workload = blackboard.get("workload")
            
            # Criteria for good match:
            # 1. Skill match > 0.6 (60% match)
            # 2. Workload < 0.8 (less than 80% capacity)
            if skill_match > 0.6 and workload < 0.8:
                blackboard.set("recommendation", "Good match")
                blackboard.set("recommendation_score", 0.7)
                return py_trees.common.Status.SUCCESS
            
            return py_trees.common.Status.FAILURE
    
    class ConsiderOtherDevelopers(py_trees.behaviour.Behaviour):
        """Fallback recommendation to consider other developers"""
        def __init__(self, name):
            super().__init__(name)
        
        def update(self):
            # Get blackboard data
            blackboard = py_trees.blackboard.Blackboard()
            
            # This is the fallback node, always succeeds
            blackboard.set("recommendation", "Consider other developers")
            blackboard.set("recommendation_score", 0.3)
            return py_trees.common.Status.SUCCESS
    
    def analyze_assignment(self, task_id, developer_id):
        """
        Analyze a potential task assignment using the behavior tree
        
        Args:
            task_id: ID of the task
            developer_id: ID of the developer
            
        Returns:
            Analysis results
        """
        # Set data in blackboard
        self.blackboard.set("task_id", task_id)
        self.blackboard.set("developer_id", developer_id)
        
        # Setup and tick the tree
        self.tree.setup()
        self.tree.tick_once()
        
        # Get results from blackboard
        error = self.blackboard.get("error", None)
        if error:
            return {"error": error, "task_id": task_id, "developer_id": developer_id}
            
        # Get recommendation
        recommendation = self.blackboard.get("recommendation", "No recommendation available")
        recommendation_score = self.blackboard.get("recommendation_score", 0.0)
        skill_match = self.blackboard.get("skill_match", 0.0)
        workload = self.blackboard.get("workload", 0.0)
        
        # Create result
        result = {
            "task_id": task_id,
            "developer_id": developer_id,
            "recommendation": recommendation,
            "score": recommendation_score,
            "skill_match": skill_match,
            "workload": workload
        }
        
        return result

# Initialize the behavior tree
assignment_tree = TaskAssignmentBehaviorTree() 