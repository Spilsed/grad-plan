import json

from typing import Dict, List, TypedDict

class SectionDict(TypedDict):
    act: int
    attribute: str
    cap: int
    credMax: float
    credMin: float
    crn: int
    crse: int
    rem: int
    sec: str
    subj: str
    timeslots: List[Dict]
    title: str

class CourseDict(TypedDict):
    crse: int
    id: str
    sections: List[SectionDict]

class Prereq(TypedDict):
    title: str
    prereqs: List[str]

class Course:
    def __init__(self, course_data: Dict, prereq_data: Dict[str, Prereq]) -> None:
        # CODE-0000
        self.id: str = course_data['id']
        # 0000
        self.course: int = course_data['crse']
        # Course Title
        self.title: str = course_data['title']
        # CODE
        self.subject: str = course_data['subj']

        section = course_data['sections'][0]
        self.attribute: str = section['attribute']
        self.credit_max: float = section['credMax']
        self.credit_min: float = section['credMin']

        self.prereqs: List[str] = [x.replace(' ', '-') for x in prereq_data[self.id.replace('-', ' ')]['prereqs']]
        print(self.prereqs)
    
    def __str__(self) -> str:
        return f'{self.id} [{self.title}]'

class Courses:
    def __init__(self, courses_path: str, prereq_path: str) -> None:
        with open(courses_path, 'r') as f:
            raw_course_data: List[Dict] = json.load(f)
            self.course_data: Dict[str, Dict] = {}
            for _, value in enumerate(raw_course_data):
                raw_courses: Dict = value['courses']
                courses: Dict[str, CourseDict] = {}
                for _, course in enumerate(raw_courses):
                    courses[course['crse']] = course

                self.course_data[value['code']] = courses
        
        with open(prereq_path, 'r') as f:
            self.prereq_data: Dict[str, Prereq] = json.load(f)
    
    def get_course(self, code: str, course: int) -> Course | None:
        try:
            code_list = self.course_data[code.upper()]
            course_data = code_list[course]
            return Course(course_data, self.prereq_data)
        except KeyError:
            return None

if __name__ == "__main__":
    c = Courses('./src/courses.json', './src/prereq_graph.json')
    print(c.get_course("math", 4090))
    print(c.get_course("math", 4100))