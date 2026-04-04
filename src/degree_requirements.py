import json
from src.courses import Course

from typing import Dict, List, TypedDict, Literal, Optional

class RestrictionDict(TypedDict):
    type: Literal["attribute"]
    operator: Literal["equal"]
    connector: Optional[Literal["none"]]
    attribute: Optional[Literal["CommunicationIntensive"] ]
    major: Optional[str]

class ConditionDict(TypedDict):
    type: Literal["if"] | Literal["nested"]
    connector: Literal["or"]
    left_condition: ConditionDict | RestrictionDict
    right_condition: ConditionDict | RestrictionDict

class CourseDict(TypedDict):
    dept: str
    crse: str | Literal["@"]
    restriction: List[RestrictionDict]

class CourseRuleDict(TypedDict):
    type: Literal["course"] | Literal["group"]
    num_courses_needed: int
    courses: List[CourseDict]
    except_courses: Optional[List[CourseDict]]

class IfSubRuleDict(TypedDict):
    label: str
    rule_data: CourseRuleDict | IfRuleDict

class IfRuleDict(TypedDict):
    type: Literal["if"]
    connector: Literal["or"] | Literal['and']
    condition: ConditionDict
    if_branch: List[IfSubRuleDict]
    else_branch: List[IfSubRuleDict]

def evaluate_if_condition(condition: ConditionDict) -> bool:
    if condition['type'] == 'major':
        return condition['major'] == 'CSCI'
    elif condition['type'] == 'degree':
        return condition['degree'] == 'CSCI'
    elif condition['type'] == 'nested':
        left = evaluate_if_condition(condition['left_condition']) # type: ignore
        right = evaluate_if_condition(condition['right_condition']) # type: ignore

        if condition['connector'] == 'or':
            return left or right
        elif condition['connector'] == 'and':
            return left and right
        else:
            raise Exception(f'Error: Unknown connector type for condition ({condition['connector']})!')
    else:
        raise Exception(f'Error: Unknown type ({condition['type']})!')

class Rule:
    def __init__(self, title: str, raw_rule: CourseRuleDict | IfRuleDict) -> None:
        self.title = title
        self.rule_data: CourseRuleDict | IfRuleDict = raw_rule   

    def does_course_satisfy(self, courses: List[Course]) -> bool:
        if self.rule_data['type'] == 'course':
            needed = self.rule_data.get('num_courses_needed', 1)
            found_count = 0
            
            for course in courses:
                if self._course_satisfies_requirement(course, self.rule_data):
                    found_count += 1
                
                if found_count >= needed:
                    return True

            return False
        elif self.rule_data['type'] == 'if':
            condition_met = evaluate_if_condition(self.rule_data['condition'])
            current_branch = self.rule_data['if_branch'] if condition_met else self.rule_data['else_branch']

            for sub_rule in current_branch:
                temp_rule = Rule(sub_rule['label'], sub_rule['rule_data'])
                if not temp_rule.does_course_satisfy(courses):
                    return False
            
            return True
        else:
            raise Exception(f'Error: unknown rule type ({self.rule_data['type']})!')
    
    def _course_satisfies_requirement(self, course: Course, rule_data: CourseRuleDict) -> bool:
        # print(self.title,"\n", rule_data)

        for exc in rule_data.get('except', []):
            if exc['dept'] == course.subject and (exc['crse'] == course.course or exc['crse'] == '@'):
                return False
        
        for req in rule_data['courses']:
            if req['dept'] == course.subject:
                if req['crse'] == str(course.course) or req['crse'] == '@':
                    return True
        
        return False

class DegreeRequirements:
    def __init__(self, degree_requirements_path: str) -> None:
        with open(degree_requirements_path, 'r') as f:
            raw_degree_reqs = json.load(f)
            
            self.rules: Dict[str, Dict[str, Rule]] = {}
            for requirement in raw_degree_reqs:
                rules = requirement['rules']
                title = requirement['title']

                # print(json.dumps(rules[0]['rule_data'], indent=1))
                print(title)
                for rule in rules:
                    if self.rules.get('title') is None:
                        self.rules[title] = {}
                    
                    self.rules[title][rule['label']] = Rule(rule['label'], rule['rule_data'])

if __name__ == "__main__":
    from src.courses import Courses

    dr = DegreeRequirements("./src/2026-BS-CSCI.json")
    courses = Courses('./src/courses.json', './src/prereq_graph.json')
    
    course_list = [
        courses.get_course('CHEM', 1100),
        courses.get_course('CHEM', 1200),
        courses.get_course('CSCI', 1100),
        courses.get_course('MATH', 1010),
        courses.get_course('MATH', 1020),
        courses.get_course('MGMT', 2100),
        courses.get_course('PHYS', 1100),
        courses.get_course('STSO', 1000),
        courses.get_course('WRIT', 1000),
        courses.get_course('WRIT', 1000),

        courses.get_course('BIOL', 1010),
        courses.get_course('BIOL', 1015)
    ]
    
    for i, course in enumerate(course_list):
        if course is None:
            print(i)
            exit()

    print(dr.rules.keys())
    for rule in dr.rules.values():
        for subrule in rule.values():
            print(subrule.title)
            print(subrule.does_course_satisfy(course_list)) # type: ignore